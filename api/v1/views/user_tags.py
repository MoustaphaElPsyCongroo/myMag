#!/usr/bin/python3
from flask import abort, jsonify, request

from api.v1.views import app_views
from models import storage
from models.tag import Tag, TagDislikeAssociation, TagLikeAssociation
from models.user import User


@app_views.route("/users/<user_id>/tags/liked", methods=["POST"])
def like_tag(user_id):
    """Make a user like a tag, incrementing its likes count (tag can and should
    be liked multiple times)

           body:
               tag_id: <tag_id>
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    try:
        req = request.get_json()
        if req is None:
            abort(400, description="Not a JSON")
        elif req.get("tag_id") is None:
            abort(400, description="Missing tag_id")
        else:
            tag_id = req.get("tag_id")
            tag = storage.get(Tag, tag_id)

            if tag is None:
                abort(404, description="The specified tag doesn't exist")

            tag_stats = {}
            tag_stats["name"] = tag.name
            tag_stats["like_count_from_user"] = 1
            tag_stats["dislike_count_from_user"] = 0
            for asso in tag.tag_like_associations:
                if asso.user == user:
                    asso.like_count_from_user += 1
                    tag_stats["like_count_from_user"] = asso.like_count_from_user
                    break
            else:
                asso = TagLikeAssociation(like_count_from_user=1)
                asso.tag = tag
                asso.user = user
            for asso in tag.tag_dislike_associations:
                if asso.user == user:
                    tag_stats["dislike_count_from_user"] = asso.dislike_count_from_user
                    break
            storage.save()
    except ValueError:
        abort(400, description="Not a JSON")
    return jsonify(tag_stats), 200


@app_views.route("/users/<user_id>/tags/liked/<tag_id>", methods=["DELETE"])
def delete_like_tag(user_id, tag_id):
    """Make a user cancel their like on a tag"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    tag = storage.get(Tag, tag_id)

    if tag is None:
        abort(404, description="The specified tag doesn't exist")

    tag_stats = {}
    tag_stats["id"] = tag.id
    tag_stats["name"] = tag.name
    tag_stats["like_count_from_user"] = 0
    tag_stats["dislike_count_from_user"] = 0
    for asso in tag.tag_like_associations:
        if asso.user == user:
            asso.like_count_from_user -= 1
            tag_stats["like_count_from_user"] = asso.like_count_from_user
            break
    else:
        abort(405, description="The specified tag hasn't been liked")
    for asso in tag.tag_dislike_associations:
        if asso.user == user:
            tag_stats["dislike_count_from_user"] = asso.dislike_count_from_user
            break
    storage.save()
    return jsonify(tag_stats), 200


@app_views.route("/users/<user_id>/tags/disliked", methods=["POST"])
def dislike_tag(user_id):
    """Make a user dislike a tag, incrementing its dislikes count (tag can and
    should be disliked multiple times)

        body:
            tag_id: <tag_id>
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    try:
        req = request.get_json()
        if req is None:
            abort(400, description="Not a JSON")
        elif req.get("tag_id") is None:
            abort(400, description="Missing tag_id")
        else:
            tag_id = req.get("tag_id")
            tag = storage.get(Tag, tag_id)

            if tag is None:
                abort(404, description="The specified tag doesn't exist")

            tag_stats = {}
            tag_stats["name"] = tag.name
            tag_stats["dislike_count_from_user"] = 1
            tag_stats["like_count_from_user"] = 0
            for asso in tag.tag_dislike_associations:
                if asso.user == user:
                    asso.dislike_count_from_user += 1
                    tag_stats["dislike_count_from_user"] = asso.dislike_count_from_user
                    break
            else:
                asso = TagDislikeAssociation(dislike_count_from_user=1)
                asso.tag = tag
                asso.user = user
            for asso in tag.tag_like_associations:
                if asso.user == user:
                    tag_stats["like_count_from_user"] = asso.like_count_from_user
                    break
            storage.save()
    except ValueError:
        abort(400, description="Not a JSON")
    return jsonify(tag_stats), 200


@app_views.route("/users/<user_id>/tags/disliked/<tag_id>", methods=["DELETE"])
def delete_dislike_tag(user_id, tag_id):
    """Make a user cancel their dislike on a tag"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    tag = storage.get(Tag, tag_id)

    if tag is None:
        abort(404, description="The specified tag doesn't exist")

    tag_stats = {}
    tag_stats["id"] = tag.id
    tag_stats["name"] = tag.name
    tag_stats["dislike_count_from_user"] = 0
    tag_stats["like_count_from_user"] = 0
    for asso in tag.tag_dislike_associations:
        if asso.user == user:
            asso.dislike_count_from_user -= 1
            tag_stats["dislike_count_from_user"] = asso.dislike_count_from_user
            break
    else:
        abort(405, description="The specified tag hasn't been disliked")
    for asso in tag.tag_like_associations:
        if asso.user == user:
            tag_stats["like_count_from_user"] = asso.like_count_from_user
            break
    storage.save()
    return jsonify(tag_stats), 200
