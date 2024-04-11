#!/usr/bin/python3
"""Feeds routes"""

import logging

import feedparser
from flask import abort, jsonify, request

from api.v1.utils.feed_articles import extract_article_language
from api.v1.views import app_views
from models import storage
from models.feed import Feed


@app_views.route("/feeds")
def get_feeds():
    """GET all feeds in database"""
    feeds = storage.all(Feed).values()
    return jsonify([feed.to_dict() for feed in feeds]), 200


@app_views.route("/feeds/<feed_id>")
def get_feed(feed_id):
    """GET a feed in database"""
    feed = storage.get(Feed, feed_id)
    return jsonify(feed.to_dict())


@app_views.route("/feeds", methods=["POST"])
def import_feed():
    """Import a feed into the database from its RSS url
    body:
        link: <link of the feed>
    """
    feed = {}
    try:
        req = request.get_json()
        if req is None:
            abort(400, description="Not a JSON")
        elif req.get("link") is None:
            abort(400, description="Missing link")
        else:
            link = req.get("link")
            found = storage.query(Feed).filter(Feed.link == link).first()

            if found is not None:
                return jsonify(found.to_dict()), 200

            f = feedparser.parse(link)

            if not f.feed:
                abort(404, description="Not a valid feed address")

            # Check if the feed is permanently redirected
            if f.status == 301:
                link = f.href
                f = feedparser.parse(link)

            # Check if the feed is inactive
            if f.status == 410:
                abort(410, description="Feed is permanently inactive")

            if "title" not in f.feed:
                abort(400, description="Not a valid feed")

            feed["name"] = f.feed.title
            feed["link"] = link

            if "subtitle" in f.feed and f.feed.subtitle:
                feed["description"] = f.feed.subtitle

            if "image" in f.feed and "href" in f.feed.image:
                feed["banner_img"] = f.feed.image.href

            # TODO: Récupérer le lien de la favicon trouvée côté client grâce au
            # feedsearch et l'envoyer dans le body de la requête pour que je la
            # définisse ici, semble plus fiable que le icon du créateur du rss.
            if "icon" in f.feed:
                feed["icon"] = f.feed.icon
            elif "logo" in f.feed:
                feed["icon"] = f.feed.logo

            feed["language"] = f.feed.get("language", "en").split("-")[0]
            # Double check 'en' feeds
            if feed["language"] == "en":
                try:
                    feed["language"] = extract_article_language(f.entries[0])
                except Exception:
                    logging.exception(
                        f"Error fetching language for feed {feed['name']}"
                    )

            created = Feed(**feed)
            storage.new(created)
            storage.save()
            return jsonify(created.to_dict()), 201
    except ValueError:
        abort(400, description="Not a valid url")


@app_views.route("/feeds/<feed_id>", methods=["PUT"])
def update_feed(feed_id):
    """UPDATE a feed's details

    body:
        <feed attribute to update>: <value>
    invalid: id, created_at, updated_at
    """
    feed = storage.get(Feed, feed_id)
    if feed is None:
        abort(404)

    try:
        req = request.get_json()
        if req is None:
            abort(404, description="Not a JSON")
        else:
            invalid = ["id", "user_id", "created_at", "updated_at"]
            for key, value in req.items():
                if key not in invalid:
                    setattr(feed, key, value)
            storage.save()
            return jsonify(feed.to_dict()), 200
    except ValueError:
        abort(400, description="Not a JSON")


@app_views.route("/feeds/<feed_id>", methods=["DELETE"])
def delete_feed(feed_id):
    """DELETE a feed from db"""
    feed = storage.get(Feed, feed_id)
    if feed is None:
        abort(404)
    else:
        storage.delete(feed)
        storage.save()
        return {}, 200
