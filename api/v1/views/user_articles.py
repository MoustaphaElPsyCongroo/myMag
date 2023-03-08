#!/usr/bin/python3
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.feed import Feed
from models.user import User
from api.v1.utils import (
    serialize_articles)


@app_views.route('/users/<user_id>/articles')
def get_user_articles(user_id):
    """GET all articles from user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    articles = []
    for feed in user.user_feeds:
        feed_articles = serialize_articles(feed.feed_articles)
        for article in feed_articles:
            article['feed_name'] = feed.name
            article['feed_banner_img'] = feed.banner_img
            articles.append(article)

    return jsonify(articles), 200

# TODO: Add route for unread articles and add liked/disliked status


def get_user_feeds(user_id):
    """GET current user's all feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    feeds = [feed.to_dict() for feed in user.user_feeds]
    return jsonify(feeds), 200
