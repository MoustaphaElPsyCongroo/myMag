#!/usr/bin/python3
"""Routes for user_articles relationships"""
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.article import Article
from models.user import User
from api.v1.utils.feed_articles import serialize_articles


@app_views.route('/users/<user_id>/articles')
def get_user_articles(user_id):
    """GET all articles (read and unread) from user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    articles = []
    for feed in user.user_feeds:
        feed_articles = serialize_articles(feed.feed_articles)
        for article in feed_articles:
            article['feed_name'] = feed.name
            article['feed_banner_img'] = feed.banner_img
            article['feed_articles_per_week'] = feed.articles_per_week
            article['feed_avg_shares_per_week'] = feed.average_shares_per_week
            articles.append(article)

    return jsonify(articles), 200


@app_views.route('/users/<user_id>/articles/read')
def get_user_read_articles(user_id):
    """GET all read articles from a user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    if not user.read_articles:
        abort(404, description="No read articles yet")

    read_articles = []
    for feed in user.user_feeds:
        feed_articles = serialize_articles(
            feed.feed_articles,
            read_articles=user.read_articles,
            only_unread=False
        )
        for article in feed_articles:
            article['feed_name'] = feed.name
            article['feed_banner_img'] = feed.banner_img
            article['feed_icon'] = feed.icon
            article['feed_articles_per_week'] = feed.articles_per_week
            article['feed_avg_shares_per_week'] = feed.average_shares_per_week
            read_articles.append(article)
    return jsonify(read_articles), 200


@app_views.route('/users/<user_id>/articles/read', methods=['POST'])
def mark_article_as_read(user_id):
    """Mark an article as read by a user

        body:
            article_id: <article_id>
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    try:
        req = request.get_json()
        if req is None:
            abort(400, description='Not a JSON')
        elif req.get('article_id') is None:
            abort(400, description='Missing article_id')
        else:
            article_id = req.get('article_id')
            article = storage.get(Article, article_id)

            if article is None:
                abort(404, description="The specified article doesn't exist")

            user.read_articles.append(article)
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return {}, 200


@app_views.route('/users/<user_id>/articles/<article_id>', methods=['DELETE'])
def mark_article_as_unread(user_id, article_id):
    """Mark an article as unread by a user
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    article = storage.get(Article, article_id)
    if article is None:
        abort(404, description="The specified article doesn't exist")

    try:
        if article not in user.read_articles:
            abort(404, description="This article is already marked as unread")
        else:
            user.read_articles.remove(article)
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return {}, 200


@app_views.route('/users/<user_id>/articles/unread')
def get_user_unread_articles(user_id):
    """GET all unread articles from user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    unread_articles = []
    for feed in user.user_feeds:
        feed_articles = serialize_articles(
            feed.feed_articles,
            read_articles=user.read_articles,
            only_unread=True
        )
        for article in feed_articles:
            article['feed_name'] = feed.name
            article['feed_banner_img'] = feed.banner_img
            article['feed_icon'] = feed.icon
            article['feed_articles_per_week'] = feed.articles_per_week
            article['feed_avg_shares_per_week'] = feed.average_shares_per_week
            unread_articles.append(article)

    return jsonify(unread_articles), 200
