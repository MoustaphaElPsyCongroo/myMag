#!/usr/bin/python3
"""Routes for user_articles relationships"""

from datetime import datetime, timedelta

from flask import abort, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import contains_eager

from api.v1.utils.feed_articles import serialize_articles, serialize_paginated_articles
from api.v1.utils.pagination import paginate
from api.v1.utils.user_articles import calculate_updated_article_scores_for_user
from api.v1.views import app_views
from models import storage
from models.article import Article, ArticleUserScoreAssociation
from models.feed import Feed
from models.user import User


@app_views.route("/users/<user_id>/articles")
def get_user_articles(user_id):
    """GET all articles (read and unread) from user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    articles = (
        storage.query(Article)
        .join(Feed)
        .join(User, Feed.feed_users)
        .filter(User.id == user_id)
        .all()
    )

    articles = serialize_articles(articles)

    return jsonify(articles), 200


@app_views.route("/users/<user_id>/articles/read")
@app_views.route("/users/<user_id>/articles/read/<int:page>")
def get_user_read_articles(user_id, page=None):
    """GET full or paginated read articles from a user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    read_articles_query = (
        storage.query(Article).join(User.read_articles).filter(User.id == user_id)
    )

    read_articles_count_query = (
        storage.query(func.count(Article.id))
        .join(User.read_articles)
        .filter(User.id == user_id)
    )

    if page is None:
        objs = read_articles_query.all()
        read_articles = serialize_articles(objs, user)
        read_articles["total"] = read_articles_count_query.scalar()
        if read_articles["total"] == 0:
            abort(404, description="No read articles yet")
    else:
        read_articles_paginated = paginate(
            read_articles_query, read_articles_count_query, page, 30
        )

        if read_articles_paginated.total == 0:
            abort(404, description="No read articles yet")

        read_articles = serialize_paginated_articles(read_articles_paginated, user)
    return jsonify(read_articles), 200


@app_views.route("/users/<user_id>/articles/read", methods=["POST"])
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
            abort(400, description="Not a JSON")
        elif req.get("article_id") is None:
            abort(400, description="Missing article_id")
        else:
            article_id = req.get("article_id")
            article = storage.get(Article, article_id)

            if article is None:
                abort(404, description="The specified article doesn't exist")

            user.read_articles.append(article)
            user.last_read_date = datetime.now()
            storage.save()
    except ValueError:
        abort(400, description="Not a JSON")
    return {}, 200


@app_views.route("/users/<user_id>/articles/unread")
def get_user_unread_articles(user_id):
    """GET the 30 first unread articles from user's subscribed feeds
    Only use the limit instead of pagination since list order will
    change according to likes/dislikes and on the front articles will be
    marked as read on scroll/click.
    """
    user = storage.get(User, user_id)
    read_ids = (
        storage.query(Article.id).join(User.read_articles).filter(User.id == user_id)
    )

    if user is None:
        abort(404, description="The specified user doesn't exist")

    two_hours_ago = datetime.now() - timedelta(hours=2)

    # last_scoring_date is null if user never subscribed to feeds (just created
    # their account for example)
    try:
        last_scoring_date = user.last_scoring_date
    except AttributeError:
        last_scoring_date = None

    if last_scoring_date and last_scoring_date <= two_hours_ago:
        calculate_updated_article_scores_for_user(user)
        storage.save()

    all_user_articles = (
        storage.query(Article)
        .join(User, ArticleUserScoreAssociation.user)
        .join(Article, ArticleUserScoreAssociation.article)
        .filter(User.id == user_id)
        .filter(Article.id.not_in(read_ids))
        .order_by(ArticleUserScoreAssociation.total_score.desc())
        .options(contains_eager(Article.article_user_score_associations))
        .populate_existing()
        .limit(30)
        .all()
    )

    all_user_articles_count = (
        storage.query(func.count(Article.id))
        .join(User, ArticleUserScoreAssociation.user)
        .join(Article, ArticleUserScoreAssociation.article)
        .filter(User.id == user_id)
        .filter(Article.id.not_in(read_ids))
        .scalar()
    )

    unread_articles = serialize_articles(all_user_articles, user)
    unread_articles["total"] = all_user_articles_count

    # Slower method (and no pagination)
    # unread_articles = []
    # for feed in user.user_feeds:
    #     unread_articles += serialize_articles(
    #         feed.feed_articles,
    #         read_articles=read_articles,
    #         only_unread=True
    #     )
    return jsonify(unread_articles), 200


@app_views.route("/users/<user_id>/articles/<article_id>", methods=["DELETE"])
def mark_article_as_unread(user_id, article_id):
    """Mark an article as unread by a user"""
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
        abort(400, description="Not a JSON")
    return {}, 200
