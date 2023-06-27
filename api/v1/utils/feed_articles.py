#!/usr/bin/python3
"""Utility functions for article and tag extraction"""
from datetime import datetime
from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError
from google.cloud import language_v1
from Levenshtein import ratio
from models import storage
from models.article import Article
from models.tag import Tag, TagArticleAssociation
from random import randint
from time import mktime
import article_parser
import feedparser
import html2text
import json
import logging
import yake

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
    except Exception:
        logging.exception('error loading headers.json')
        return ''

    try:
        title, content = article_parser.parse(
            url=url,
            output="html",
            timeout=5,
            headers=get_random_header(headers))
    except Exception:
        logging.exception('Caught exception when parsing with article parser')
        content = ''

    try:
        plain_content = html_to_text.handle(f'{content}')
    except Exception:
        logging.exception('Caught exception when extracting html')
        return ''

    return plain_content


def extract_tags(full_content, trimmed_content, lang):
    """Extract tags from a string

    Returns:
        A list of tuples of (tag, confidence)
    """
    tags = []
    invalid_tags = ['', 'Other', 'span', 'span class',
                    'p', 'div', 'div class', 'img alt', 'href']
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
        n=4,
        dedupLim=0.9,
        dedupFunc='seqm',
        windowsSize=1,
        top=20,
        features=None)
    tag_keywords = []
    keywords = custom_kw_extractor.extract_keywords(full_content)

    # Check the Levenshtein ratio of Yake's keywords against all keywords
    # already in database. If this ratio is > 0 with this score cutoff, we
    # consider the two words the same keyword. Ex: révolutionner/révolution.
    known_tags_raw = storage.query(Tag.name).filter(
        Tag.type == 'keyword').all()
    # Keyword in known_keywords is a one char tuple due to selecting a single
    # SQL column, so keyword[0]
    known_tags = [keyword[0] for keyword in known_tags_raw]
    keywords = [kw[0] for kw in keywords]
    for kw in keywords:
        if kw in known_tags and kw not in tag_keywords:
            tag_keywords.append(kw)
            known_tags.append(kw)
            continue
        for keyword in known_tags:
            if (
                ratio(keyword, kw, score_cutoff=0.85) > 0
                and keyword not in tag_keywords
            ):
                tag_keywords.append(keyword)
                known_tags.append(keyword)
                # print('keyword from yake:', kw)
                # print('accepted keyword from db:', keyword)

    # If no existing tag matched, add the two first ones that consist of two
    # words or less if extracted content is long enough for tags to be relevant
    if len(tag_keywords) == 0 and len(full_content) >= 800:
        for kw in keywords:
            if (
                (len(kw.split(' ')) <= 2) and
                (
                    len(tag_keywords) == 1 and (
                        ratio(kw, tag_keywords[0],
                              score_cutoff=0.85) == 0
                        and kw not in tag_keywords)
                )
                or (len(tag_keywords) == 0)
            ):
                tag_keywords.append(kw)
    tag_keywords = [(tag, None) for tag in tag_keywords]

    for false_couples in tag_keywords:
        tags.append(false_couples)

    print('all keywords:', keywords)
    # print('all tags final: ', tags)
    print('tag_keywords:', tag_keywords)
    return tags


def fetch_articles(feed):
    """Fetch all new articles of a feed, or the ten first if never fetched"""
    if not feed.active:
        message = f'Feed {feed.id} is permanently inactive'
        raise FeedInactiveError(message)
    if feed is None:
        message = f'No feed with id {feed.id} found'
        raise FeedNotFoundError(message)
    f = None
    entries = []

    # Feed has never been fetched or doesn't support etag/last_modified headers
    if feed.etag is None and feed.last_modified is None:
        f = feedparser.parse(feed.link)
    elif feed.etag and feed.last_modified:
        f = feedparser.parse(feed.link, etag=feed.etag,
                             modified=feed.last_modified)
    elif feed.etag:
        f = feedparser.parse(feed.link, etag=feed.etag)
    elif feed.last_modified:
        f = feedparser.parse(feed.link, modified=feed.last_modified)
    if 'etag' in f:
        feed.etag = f.etag
    if 'modified' in f:
        feed.last_modified = f.modified

    # Check if the feed has been permanently redirected
    if f.status == 301:
        feed.link = f.href
        storage.save()

    # Check if the feed is inactive
    if f.status == 410:
        feed.active = False
        storage.save()
        message = f'Feed {feed.id} is permanently inactive'
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


def parse_save_articles(entries, feed):
    """Parse, extract tags and save in database a list of entries"""
    articles_added = 0
    for article in entries:
        properties = {}

        properties['feed_id'] = feed.id
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
        except Exception:
            logging.exception()
            continue

        properties['description'] = ''
        if 'summary_detail' in article:
            if article.summary_detail.type != 'text/plain':
                try:
                    description = html_to_text.handle(article.summary)
                    properties['description'] = description
                except Exception as e:
                    logging.exception('Caught exception when extracting html')
                    properties['description'] = ''
            else:
                properties['description'] = article.summary

        if 'content' in article:
            for content in article.content:
                if content.type != 'text/plain' or '<p>' in content.value:
                    try:
                        description = html_to_text.handle(content.value)
                        properties['description'] += description
                    except Exception:
                        logging.exception(
                            'Caught exception when extracting html')
                        properties['description'] = ''
                else:
                    properties['description'] += content.value

        if not properties['description']:
            if 'summary' in article:
                properties['description'] = article.summary

        content = f'{article.title}. {extract_article_content(article.link)}'
        # print('length content before: ', len(content))
        if len(content) <= 800:
            content = f"{article.title} {properties['description']}"
        # print(content)

        properties['description'] = properties['description'][:2000]

        try:
            tags_with_confidence = extract_tags(
                content, content[:1970], feed.language)
        except Exception:
            logging.exception()
            continue

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
            if tag_name.lower() in tag_names:
                continue
            if existing is not None:
                print('tag exists in db:', tag_name)
                assoc.tag = existing
            else:
                new_tag = Tag(
                    name=tag_name,
                    type=tag_type
                )
                assoc.tag = new_tag
                storage.new(new_tag)
            tag_names.append(tag_name.lower())
            created_article.article_tag_associations.append(assoc)
        storage.new(created_article)
        storage.save()
        articles_added += 1
    feed.updated_at = datetime.now()
    storage.save()
    return {
        'feed': f'{feed.id}',
        'articles per week': f'{feed.articles_per_week}',
        'total new articles': len(entries),
        'articles added': articles_added
    }


def serialize_article(article):
    """Convert an article object into a dict, displaying tags and feed info"""
    article_dict = article.to_dict()
    feed = article.article_feed
    article_dict['feed_name'] = feed.name
    article_dict['feed_banner_img'] = feed.banner_img
    article_dict['feed_icon'] = feed.icon
    article_dict['feed_articles_per_week'] = feed.articles_per_week
    article_dict['feed_avg_shares_per_week'] = feed.average_shares_per_week
    article_dict['tags'] = []
    for assoc in article.article_tag_associations:
        tag_name = assoc.tag.name
        tag_confidence = assoc.confidence
        article_dict['tags'].append([tag_name, tag_confidence])
    return article_dict


def serialize_articles(articles, *args, **kwargs):
    """Convert a list of articles to a list of dicts, displaying tags"""
    read_articles = kwargs.get('read_articles')
    only_unread = kwargs.get('only_unread')

    if read_articles:
        if only_unread:
            articles_dicts = [serialize_article(
                article) for article in articles
                if article not in read_articles]
        else:
            articles_dicts = [serialize_article(
                article) for article in articles if article in read_articles]
    else:
        articles_dicts = [serialize_article(article) for article in articles]
    return articles_dicts
