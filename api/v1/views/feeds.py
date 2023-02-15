#!/usr/bin/python3
from api.v1.views import app_views
from api.v1.auth import login_required
from flask import jsonify, abort, request
from models import storage
from models.feed import Feed
from models.user import User


@app_views.route('/feeds')
def get_feeds():
    """GET all feeds in database"""
    feeds = storage.all(Feed).values()
    return jsonify([feed.to_dict() for feed in feeds]), 200


@app_views.route('/feeds', methods=['POST'])
def import_feed():
    """Import a feed into the database"""
    try:
        req = request.get_json()
        if req is None:
            abort(400, description='Not a JSON')
        elif req.get('name') is None:
            abort(400, description='Missing name')
        elif req.get('link') is None:
            abort(400, description='Missing link')
        else:
            created = Feed(**req)
            storage.new(created)
            storage.save()
            return jsonify(created.to_dict()), 201
    except ValueError:
        abort(400, description='Not a JSON')
