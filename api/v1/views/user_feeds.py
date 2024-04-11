#!/usr/bin/python3
"""Routes for user_feeds relationships"""

from flask import abort, jsonify, request

from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError
from api.v1.utils.feed_articles import fetch_articles, parse_save_articles
from api.v1.utils.user_articles import calculate_initial_article_score_for_user
from api.v1.views import app_views
from models import storage
from models.article import Article
from models.feed import Feed
from models.user import User


@app_views.route("/users/<user_id>/feeds")
def get_user_feeds(user_id):
    """GET a user's all feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    feeds = [feed.to_dict() for feed in user.user_feeds]
    return jsonify(feeds), 200


@app_views.route("/users/<user_id>/feeds", methods=["POST"])
def subscribe_user_to_feed(user_id):
    """Make a user subscribe to a feed in database, fetching articles for it if
    first subscriber
        body:
            feed_id: <feed_id>
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    try:
        req = request.get_json()
        if req is None:
            abort(400, description="Not a JSON")
        elif req.get("feed_id") is None:
            abort(400, description="Missing feed_id")
        else:
            feed_id = req.get("feed_id")
            feed = storage.get(Feed, feed_id)
            if feed is None:
                abort(404, description="This feed doesn't exist in database")
            if user in feed.feed_users:
                abort(404, description="User already subscribed to this feed")

            # if the feed has no user, fetch its articles first
            if not feed.feed_users:
                try:
                    articles = fetch_articles(feed)
                except FeedInactiveError:
                    abort(410, description="This feed is permanently inactive")
                except FeedNotFoundError:
                    abort(404, description="Feed not found")
                else:
                    if len(articles) < 10:
                        ten_recent_articles = (
                            storage.query(Article)
                            .filter(Article.feed_id == feed.id)
                            .order_by(Article.created_at.desc())
                            .limit(10)
                            .all()
                        )
                        for article in ten_recent_articles:
                            calculate_initial_article_score_for_user(user, article)
                        user.user_feeds.append(feed)
                    else:
                        user.user_feeds.append(feed)
                        parse_save_articles(articles, feed)
            else:
                ten_recent_articles = (
                    storage.query(Article)
                    .join(Feed.feed_articles)
                    .filter(Article.feed_id == feed.id)
                    .order_by(Article.created_at.desc())
                    .limit(10)
                    .all()
                )
                for article in ten_recent_articles:
                    calculate_initial_article_score_for_user(user, article)
                user.user_feeds.append(feed)
            storage.save()
    except ValueError:
        abort(400, description="Not a JSON")
    return jsonify(feed.to_dict()), 200


@app_views.route("/users/<user_id>/feeds/<feed_id>", methods=["DELETE"])
def unsubscribe_user_from_feed(user_id, feed_id):
    """Make a user unsubscribe from a feed in database"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    feed = storage.get(Feed, feed_id)
    if feed is None:
        abort(404)

    try:
        if feed not in user.user_feeds:
            abort(404, description="This user is not subscribed to this feed")
        else:
            read_ids = (
                storage.query(Article.id)
                .join(User.read_articles)
                .filter(User.id == user_id)
            )

            feed_unread_articles = (
                storage.query(Article)
                .filter(Article.feed_id == feed_id)
                .filter(Article.id.not_in(read_ids))
                .all()
            )

            for article in feed_unread_articles:
                for asso in article.article_user_score_associations:
                    if asso.user == user:
                        storage.delete(asso)
            user.user_feeds.remove(feed)
            storage.save()
    except ValueError:
        abort(400, description="Not a JSON")
    return {}, 200
