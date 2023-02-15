#!/usr/bin/python3
"""Index for general API info"""
from models.feed import Feed
from models.tag import Tag
from models.user import User
from models import storage
from api.v1.views import app_views
from api.v1.auth import login_required
from flask import jsonify


@app_views.route('/status', methods=['GET'])
@login_required
def status(user_token, current_user):
    """Status of the API"""
    return jsonify({
        'status': 'OK',
        'user_token': user_token
    })


@app_views.route('/stats', methods=['GET'])
def number_objects():
    """Retrieves the number of each object by type"""
    classes = [Feed, Tag, User]
    names = ['feeds', 'tags', 'users']

    num_objs = {}
    for i in range(len(classes)):
        num_objs[names[i]] = storage.count(classes[i])

    return jsonify(num_objs)
