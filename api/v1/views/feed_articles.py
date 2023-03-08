#!/usr/bin/python3
import feedparser
from models.tag import TagArticleAssociation, Tag
from models.feed import Feed
from models.article import Article
from models import storage
from flask import jsonify, abort, request
from time import mktime
from datetime import datetime
from api.v1.views import app_views
from api.v1.utils import (
    extract_article_content,
    extract_tags,
    get_new_entries_for_feed,
    serialize_articles)


@app_views.route('/feeds/<feed_id>/articles')
def get_feed_articles(feed_id):
    """GET all stored articles of a feed"""
    feed = storage.get(Feed, feed_id)
    articles = serialize_articles(feed.feed_articles)
    return jsonify(articles), 200


@app_views.route('/feeds/<feed_id>/articles/fetch')
def fetch_feed_new_articles(feed_id):
    """Get all new articles of a feed, or the ten first"""
    feed = storage.get(Feed, feed_id)
    if not feed.active:
        abort(410, description='Feed is permanently inactive')
    if feed is None:
        abort(404, description='No feed has this id')
    f = None
    entries = []

    # Feed has never been fetched
    if feed.etag is None and feed.last_modified is None:
        f = feedparser.parse(feed.link)
        if 'etag' in f:
            feed.etag = f.etag
        elif 'modified' in f:
            feed.last_modified = f.modified
    elif feed.etag:
        f = feedparser.parse(feed.link, etag=feed.etag)
    elif feed.last_modified:
        f = feedparser.parse(feed.link, modified=feed.last_modified)
    else:
        abort(400, description='Invalid feed')

    # Check if the feed has been permanently redirected
    if f.status == 301:
        feed.link = f.href
        storage.save()

    # Check if the feed is inactive
    if f.status == 410:
        feed.active = False
        storage.save()
        abort(410, description='Feed is permanently inactive')

    if len(feed.feed_articles) == 0:
        entries = f.entries[:10]
    elif entries is not None and len(entries) > 0:
        latest = storage.query(Article.publish_date).filter(
            Article.feed_id == feed.id).order_by(
            Article.publish_date.desc()).first()
        entries = get_new_entries_for_feed(
            f, latest[0])

    if entries is None or len(entries) == 0:
        return jsonify({
            'message': 'No new articles'
        }), 204

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
            # abort(400, "Article missing required elements")
            continue
        properties['description'] = article.get('summary', '')[:1000]

        content = f'{article.title}. {extract_article_content(article.link)}'
        print('content before length: ', len(content))
        if len(content) <= 500:
            content = f"{content} {properties['description']}"
        print('text content: ', content)
        tags_with_confidence = extract_tags(
            content, feed.language)

        # Maintenant qu'on a les tags, créer chaque tag dans la base de données
        # et ajouter l'article
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
            # print('tag_name: ', tag_name)
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
    return {}, 201