#!/usr/bin/python3
"""Utility functions for article and tag extraction"""
from datetime import datetime
from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError
from google.cloud import language_v1
from models import storage
from models.article import Article
from models.feed import Feed
from models.tag import Tag, TagArticleAssociation
from random import randint
from time import mktime
import article_parser
import feedparser
import html2text
import json
import re
import yake
from Levenshtein import ratio

html_to_text = html2text.HTML2Text()
html_to_text.ignore_links = True
html_to_text.ignore_images = True
html_to_text.images_to_alt = True
html_to_text.ignore_tables = True
html_to_text.ignore_emphasis = True


def extract_article_content(url):
    """Extract article content from url"""
    try:
        with open('headers.json', 'r', encoding='utf8') as f:
            headers = json.load(f)
    except Exception as e:
        print('error: ', e)
        return ''

    title, content = article_parser.parse(
        url=url,
        output="html",
        timeout=5,
        headers=get_random_header(headers))

    try:
        plain_content = html_to_text.handle(f'{content}')
    except Exception as e:
        print('Caught exception when extracting html: ', e)
        return ''

    return plain_content


def extract_tags(full_content, trimmed_content, lang):
    """Extract tags from a string

    Returns:
        A list of tuples of (tag, confidence)
    """
    tags = []
    invalid_tags = ['', 'Other', 'span', 'span class', 'p', 'div', 'div class']
    all_tags_raw = []

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"content": trimmed_content, "type_": type_}

    content_categories_version = (
        language_v1
        .ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2
    )
    response = client.classify_text(
        request={
            "document": document,
            "classification_model_options": {
                "v2_model":
                    {"content_categories_version": content_categories_version}
            },
        }
    )

    for category in response.categories:
        name_path = category.name
        confidence = category.confidence
        names = name_path.split('/')

        for tag in names:
            if tag not in invalid_tags and tag not in all_tags_raw:
                tags.append((tag, confidence))
            all_tags_raw.append(tag)

    custom_kw_extractor = yake.KeywordExtractor(
        lan=lang,
        n=2,
        dedupLim=0.9,
        dedupFunc='seqm',
        windowsSize=1,
        top=15,
        features=None)
    tag_keywords = []
    keywords = custom_kw_extractor.extract_keywords(full_content)

    # Check the Levenshtein ratio of Yake's keywords against all keywords (not
    # tags) already in database. If this ratio is > 0 with this score cutoff,
    # we consider the two words the same keyword. Ex: révolutionner/révolution.
    known_keywords = storage.query(Tag.name).filter(
        Tag.type == 'keyword').all()

    # Keyword in known_keywords is a one char tuple, so keyword[0]
    keywords = [kw[0] for kw in keywords]
    for keyword in known_keywords:
        for kw in keywords:
            if ratio(keyword[0].lower(),
                     kw.lower(),
                     score_cutoff=0.65) > 0 and keyword[0] not in tag_keywords:
                tag_keywords.append(keyword[0])

    if len(tag_keywords) == 0:
        tag_keywords = keywords[:2]

    tag_keywords = [(tag, None) for tag in tag_keywords]

    for false_couples in tag_keywords:
        tags.append(false_couples)

    print('all tags final: ', tags)
    return tags


def fetch_articles(feed_id):
    """Fetch all new articles of a feed, or the ten first if never fetched"""
    feed = storage.get(Feed, feed_id)
    if not feed.active:
        message = f'Feed {feed_id} is permanently inactive'
        raise FeedInactiveError(message)
    if feed is None:
        message = f'No feed with id {feed_id} found'
        raise FeedNotFoundError(message)
    f = None
    entries = []

    # Feed has never been fetched or doesn't support etag/last_modified headers
    if feed.etag is None and feed.last_modified is None:
        f = feedparser.parse(feed.link)
        if 'etag' in f:
            feed.etag = f.etag
        if 'modified' in f:
            feed.last_modified = f.modified
    elif feed.etag and feed.last_modified:
        f = feedparser.parse(feed.link, etag=feed.etag,
                             modified=feed.last_modified)
    elif feed.etag:
        f = feedparser.parse(feed.link, etag=feed.etag)
    elif feed.last_modified:
        f = feedparser.parse(feed.link, modified=feed.last_modified)

    # Check if the feed has been permanently redirected
    if f.status == 301:
        feed.link = f.href
        storage.save()

    # Check if the feed is inactive
    if f.status == 410:
        feed.active = False
        storage.save()
        message = f'Feed {feed_id} is permanently inactive'
        raise FeedInactiveError(message)

    if len(feed.feed_articles) == 0:
        entries = f.entries[:10]
    else:
        latest = storage.query(Article.publish_date).filter(
            Article.feed_id == feed.id).order_by(
            Article.publish_date.desc()).first()
        entries = get_new_entries_for_feed(
            f, latest[0])

    if entries is None or len(entries) == 0:
        storage.save()
        return []
    return entries


def get_new_entries_for_feed(feed_obj, last_update):
    """Get new feed entries if they are younger
    than the last time the feed was polled"""
    lst = last_update
    entries = []

    for entry in feed_obj.entries:
        if 'published_parsed' in entry:
            published_parsed = entry.published_parsed
        else:
            published_parsed = entry.updated_parsed

        if datetime.fromtimestamp(mktime(published_parsed)) > lst:
            entries.append(entry)

    return entries


def get_random_header(header_list):
    """Get a random header from a list of headers"""
    random_index = randint(0, len(header_list) - 1)
    return header_list[random_index]


def parse_save_articles(entries, feed_id, language):
    """Parse, extract tags and save in database a list of entries"""
    articles_added = 0
    for article in entries:
        properties = {}

        properties['feed_id'] = feed_id
        try:
            properties['title'] = article.title
            # published_parsed is a Python 9-tuple that we need to convert
            #  to a datetime object
            if 'published_parsed' in article:
                published_parsed = article.published_parsed
            else:
                published_parsed = article.updated_parsed
            properties['publish_date'] = datetime.fromtimestamp(
                mktime(published_parsed))
        except Exception as e:
            continue

        if 'summary' in article:
            if article.summary_detail.type != 'text/plain':
                try:
                    description = html_to_text.handle(article.summary)
                    properties['description'] = description[:2000]
                except Exception as e:
                    print('Caught exception when extracting html: ', e)
                    properties['description'] = ''
            else:
                properties['description'] = article.summary[:2000]

        content = f'{article.title}. {extract_article_content(article.link)}'
        print('length content before: ', len(content))
        if len(content) <= 800:
            content = f"{article.title} {properties['description']}"
        tags_with_confidence = extract_tags(
            content, content[:1970], language)

        # Now that we have the article's tags, create each Tag in database and
        # add the Article
        created_article = Article(**properties)
        tag_names = []
        for tag_confidence_couple in tags_with_confidence:
            tag_name = tag_confidence_couple[0]
            tag_type = 'tag'
            tag_confidence = tag_confidence_couple[1]
            if tag_confidence_couple[1] is None:
                tag_type = 'keyword'
                tag_confidence = 0.00

            assoc = TagArticleAssociation(confidence=tag_confidence)
            assoc.tag = None
            existing = storage.query(Tag).filter(Tag.name == tag_name).first()
            if tag_name in tag_names:
                continue
            if existing is not None:
                assoc.tag = existing
            else:
                new_tag = Tag(
                    name=tag_name,
                    type=tag_type
                )
                assoc.tag = new_tag
                tag_names.append(tag_name)
                storage.new(new_tag)
            created_article.article_tag_associations.append(assoc)
        storage.new(created_article)
        storage.save()
        articles_added += 1
    storage.save()
    return {
        'total new articles': len(entries),
        'articles added': articles_added
    }


def serialize_article(article):
    """Convert an article object into a dict, displaying tags"""
    article_dict = article.to_dict()
    article_dict['tags'] = []
    for assoc in article.article_tag_associations:
        tag_name = assoc.tag.name
        tag_confidence = assoc.confidence
        article_dict['tags'].append([tag_name, tag_confidence])
    return article_dict


def serialize_articles(articles):
    """Convert a list of articles to a list of dicts, displaying tags"""
    articles_dicts = [serialize_article(article) for article in articles]
    return articles_dicts
