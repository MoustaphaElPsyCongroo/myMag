#!/usr/bin/python3
"""Routes for feed_articles relationships"""

from flask import abort, jsonify
from sqlalchemy import func

from api.v1.utils.feed_articles import serialize_articles, serialize_paginated_articles
from api.v1.utils.pagination import paginate
from api.v1.views import app_views
from models import storage
from models.article import Article
from models.feed import Feed
from models.user import User


@app_views.route("/feeds/<feed_id>/articles/<int:page>")
def get_feed_articles(feed_id, page):
    """GET paginated articles of a feed"""
    feed = storage.get(Feed, feed_id)

    if feed is None:
        abort(404, description="The specified feed doesn't exist")

    feed_articles_query = (
        storage.query(Article)
        .join(Feed.feed_articles)
        .filter(Article.feed_id == feed_id)
    )

    feed_articles_count_query = (
        storage.query(func.count(Article.id))
        .join(Feed.feed_articles)
        .filter(Article.feed_id == feed_id)
    )

    feed_articles_paginated = paginate(
        feed_articles_query, feed_articles_count_query, page, 30
    )

    if feed_articles_paginated.total == 0:
        abort(404, description="No read articles yet")

    feed_articles = serialize_paginated_articles(feed_articles_paginated)

    return jsonify(feed_articles), 200


@app_views.route("/feeds/<feed_id>/users/<user_id>/articles/unread")
def get_feed_unread_articles(feed_id, user_id):
    """GET unread articles of a feed (whether user subscribed or not)"""
    user = storage.get(User, user_id)
    feed = storage.get(Feed, feed_id)

    read_ids = (
        storage.query(Article.id).join(User.read_articles).filter(User.id == user_id)
    )
    if user is None:
        abort(404, description="The specified user doesn't exist")
    if feed is None:
        abort(404, description="The specified feed doesn't exist")

    feed_unread_articles = (
        storage.query(Article)
        .join(Feed.feed_articles)
        .filter(Article.feed_id == feed_id)
        .filter(Article.id.not_in(read_ids))
        .limit(30)
        .all()
    )

    all_user_articles_count = (
        storage.query(func.count(Article.id))
        .join(Feed.feed_articles)
        .filter(Article.feed_id == feed_id)
        .filter(Article.id.not_in(read_ids))
        .scalar()
    )

    unread_articles = serialize_articles(feed_unread_articles, user)
    unread_articles["total"] = all_user_articles_count
    return jsonify(unread_articles), 200
