#!/usr/bin/python3
from api.v1.views import app_views
from flask import jsonify, abort, request
from google.cloud import language_v1
from models import storage
from models.article import Article
from models.feed import Feed
from models.tag import TagArticleAssociation, Tag
import article_parser
import feedparser
import json
from random import randint
import re
import yake
from Levenshtein import ratio


def get_random_header(header_list):
    random_index = randint(0, len(header_list) - 1)
    return header_list[random_index]


def extract_article_content(url):
    """Extract article content from url"""
    try:
        with open('headers.json', 'r', encoding='utf8') as f:
            headers = json.load(f)
    except Exception as e:
        print('error: ', e)
        return None

    title, content = article_parser.parse(
        url=url,
        output="markdown",
        timeout=5,
        headers=get_random_header(headers))

    # Remove all text between parenthesis (links)
    content = re.sub(r"\([^)]*\)", "", content)

    final_text = f'{title}. {content}'

    return final_text[:1970]


def extract_tags(content, lang):
    """Extract tags from a string

    Returns:
        A list of tuples of (tag, confidence)
    """
    tags = []
    invalid_tags = ['', 'Other']
    all_tags_raw = []

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"content": content, "type_": type_}

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
    keywords = custom_kw_extractor.extract_keywords(content)[:3]

    # Ce truc en-dessous est probablement un tuple d'un chractère, vérifier si
    # j'ai une erreur

    # Check the Levenshtein ratio of Yake's keywords against all keywords (not
    # tags) already in database. If this ratio is > 0 with this score cutoff,
    # we consider the two words the same keyword. Ex: révolutionner et
    # révolution.
    known_keywords = storage.query(Tag.name).filter(
        Tag.type == 'keyword').all()
    for keyword in known_keywords:
        for kw in keywords:
            kw_name = kw[0]
            if ratio(keyword.lower(),
                     kw_name.lower(),
                     score_cutoff=0.65) > 0 and keyword not in tag_keywords:
                tag_keywords.append(keyword)

    if len(tag_keywords) == 0:
        tag_keywords = keywords[:2]
    tag_keywords = [(tag[0], None) for tag in tag_keywords]

    for false_couples in tag_keywords:
        tags.append(false_couples)

    print(tags)
    return tags


@app_views.route('/feeds/<feed_id>/articles')
def get_feed_articles(feed_id):
    """GET all articles of a feed"""
    feed = storage.get(Feed, feed_id)
    return jsonify([article.to_dict() for article in feed.feed_articles]), 200


@app_views.route('/feeds/<feed_id>/articles/fetch')
def fetch_feed_new_articles(feed_id):
    """Get all new articles of a feed, or the ten first"""
    feed = storage.get(Feed, feed_id)
    f = None
    entries = []

    # Feed has never been fetched
    if feed.etag is None and feed.last_modified is None:
        f = feedparser.parse(feed.link)
    elif feed.etag:
        f = feedparser.parse(feed.link, etag=feed.etag)
    elif feed.last_modified:
        f = feedparser.parse(feed.link, modified=feed.last_modified)
    else:
        abort(400, description='Invalid feed')

    if feed.etag is None and feed.last_modified is None:
        entries = f.entries[:10]
    else:
        entries = f.entries

    for article in entries:
        properties = {}

        properties['feed_id'] = feed_id
        try:
            properties['title'] = article.title
            properties['publish_date'] = article.published_parsed
        except KeyError as e:
            abort(400, "Article missing required elements")
        properties['description'] = article.get('summary', '')

        content = extract_article_content(article.link)
        print('text content: ', content)
        tags_with_confidence = extract_tags(content, feed.language)

        # Maintenant qu'on a les tags, créer chaque tag dans la base de données
        # et ajouter l'article
