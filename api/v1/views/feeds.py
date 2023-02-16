#!/usr/bin/python3
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.feed import Feed
import feedparser


@app_views.route('/feeds')
def get_feeds():
    """GET all feeds in database"""
    feeds = storage.all(Feed).values()
    return jsonify([feed.to_dict() for feed in feeds]), 200


@app_views.route('/feeds', methods=['POST'])
def import_feed():
    """Import a feed into the database from its RSS url"""
    feed = {}
    try:
        req = request.get_json()
        if req is None:
            abort(400, description='Not a JSON')
        elif req.get('link') is None:
            abort(400, description='Missing link')
        else:
            link = req.get('link')
            found = storage.query(
                Feed).filter(Feed.link == link).first()

            if found is not None:
                return jsonify(found.to_dict()), 200

            f = feedparser.parse(link)

            if 'title' not in f.feed:
                abort(400, description='Not a valid feed')

            feed['name'] = f.feed.title
            feed['link'] = link

            if 'subtitle' in f.feed and f.feed.subtitle:
                feed['description'] = f.feed.subtitle

            if 'image' in f.feed and 'href' in f.feed.image:
                feed['banner_img'] = f.feed.image.href

            if 'content' in f.entries[0]:
                print('premier content: ', f.entries[0].content)

            created = Feed(**feed)
            storage.new(created)
            storage.save()
            return jsonify(created.to_dict()), 201
    except ValueError:
        abort(400, description='Not a valid url')
