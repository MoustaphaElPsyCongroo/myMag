#!/usr/bin/python3
"""Index for general API info"""
from models.article import Article
from models.feed import Feed
from models.tag import Tag
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import jsonify
from flask_login import login_required


@app_views.route('/status', methods=['GET'])
@login_required
def status():
    """Status of the API"""
    return jsonify({'status': 'OK'})


@app_views.route('/stats', methods=['GET'])
@login_required
def number_objects():
    """Retrieves the number of each object by type"""
    classes = [Feed, Tag, User]
    names = ['feeds', 'tags', 'users']

    num_objs = {}
    for i in range(len(classes)):
        num_objs[names[i]] = storage.count(classes[i])

    return jsonify(num_objs)
