#!/usr/bin/python3
"""Index for general API info"""

from flask import jsonify

from api.v1.views import app_views
from models import storage
from models.feed import Feed
from models.tag import Tag
from models.user import User


@app_views.route("/status", methods=["GET"])
def status():
    """Status of the API"""
    return jsonify(
        {
            "status": "OK",
        }
    )


@app_views.route("/stats", methods=["GET"])
def number_objects():
    """Retrieves the number of each object by type"""
    classes = [Feed, Tag, User]
    names = ["feeds", "tags", "users"]

    num_objs = {}
    for i in range(len(classes)):
        num_objs[names[i]] = storage.count(classes[i])

    return jsonify(num_objs)
