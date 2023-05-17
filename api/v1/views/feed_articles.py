#!/usr/bin/python3
"""Routes for feed_articles relationships"""
from models.feed import Feed
from models import storage
from flask import jsonify
from api.v1.views import app_views
from api.v1.utils.feed_articles import serialize_articles


@app_views.route('/feeds/<feed_id>/articles')
def get_feed_articles(feed_id):
    """GET all stored articles of a feed"""
    feed = storage.get(Feed, feed_id)
    articles = serialize_articles(feed.feed_articles)
    return jsonify(articles), 200
