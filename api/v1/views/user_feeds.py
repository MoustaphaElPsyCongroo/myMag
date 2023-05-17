#!/usr/bin/python3
"""Routes for user_feeds relationships"""
from api.v1.views import app_views
from api.v1.auth import login_required
from api.v1.utils.feed_articles import fetch_articles, parse_save_articles
from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError
from flask import jsonify, abort, request
from models import storage
from models.feed import Feed
from models.user import User


@app_views.route('/users/<user_id>/feeds')
def get_user_feeds(user_id):
    """GET current user's all feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    feeds = [feed.to_dict() for feed in user.user_feeds]
    return jsonify(feeds), 200


@app_views.route('/users/<user_id>/feeds', methods=['POST'])
def subscribe_user_to_feed(user_id):
    """Make a user subscribe to a feed in database"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    try:
        req = request.get_json()
        if req is None:
            abort(400, description='Not a JSON')
        elif req.get('feed_id') is None:
            abort(400, description='Missing feed_id')
        else:
            feed_id = req.get('feed_id')
            feed = storage.get(Feed, feed_id)
            if feed is None:
                abort(404, description="This feed doesn't exist in database")

            # if the feed has no user, fetch its 10 first articles first
            if not feed.feed_users:
                try:
                    articles = fetch_articles(feed)
                except FeedInactiveError:
                    abort(410, description="This feed is permanently inactive")
                except FeedNotFoundError:
                    abort(404, description="Feed not found")
                else:
                    parse_save_articles(articles, feed)
            user.user_feeds.append(feed)
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return jsonify(feed.to_dict()), 200


@app_views.route('/users/<user_id>/feeds/<feed_id>', methods=['DELETE'])
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
            abort(400, description="This feed doesn't exist in database")
        else:
            user.user_feeds.remove(feed)
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return {}, 200
