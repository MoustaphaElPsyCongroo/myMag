#!/usr/bin/python3
"""Users routes"""

from flask import jsonify

from api.v1.auth import login_required
from api.v1.views import app_views
from models import storage


@app_views.route("/users/<user_id>")
@login_required
def get_user(token, current_user, user_id):
    """GET the current user"""
    return jsonify(token, current_user.to_dict()), 200


@app_views.route("/users/<user_id>", methods=["DELETE"])
@login_required
def delete_user(token, current_user, user_id):
    """DELETE the current user"""
    storage.delete(current_user)
    storage.save()
    return {}, 200
