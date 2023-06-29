#!/usr/bin/python3
from api.v1.views import app_views
from api.v1.utils.pagination import paginate
from api.v1.utils.feed_articles import serialize_paginated_articles
from flask import jsonify, abort, request
from models import storage
from models.tag import Tag, TagLikeAssociation, TagDislikeAssociation
from models.user import User
from sqlalchemy import func


@app_views.route('/users/<user_id>/tags/liked', methods=['POST'])
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
            abort(400, description='Not a JSON')
        elif req.get('tag_id') is None:
            abort(400, description='Missing tag_id')
        else:
            tag_id = req.get('tag_id')
            tag = storage.get(Tag, tag_id)

            if tag is None:
                abort(404, description="The specified tag doesn't exist")

            tag_stats = {}
            tag_stats['name'] = tag.name
            tag_stats['like_count_from_user'] = 1
            for asso in tag.tag_like_associations:
                if asso.user == user:
                    asso.like_count_from_user += 1
                    tag_stats['like_count_from_user'] = \
                        asso.like_count_from_user
                    tag_stats['like_count_from_article'] = \
                        asso.like_count_from_article
                    break
            else:
                asso = TagLikeAssociation(like_count_from_user=1)
                asso.tag = tag
                asso.user = user
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return jsonify(tag_stats), 200


@app_views.route('/users/<user_id>/tags/disliked', methods=['POST'])
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
            abort(400, description='Not a JSON')
        elif req.get('tag_id') is None:
            abort(400, description='Missing tag_id')
        else:
            tag_id = req.get('tag_id')
            tag = storage.get(Tag, tag_id)

            if tag is None:
                abort(404, description="The specified tag doesn't exist")

            tag_stats = {}
            tag_stats['name'] = tag.name
            tag_stats['dislike_count_from_user'] = 1
            for asso in tag.tag_dislike_associations:
                if asso.user == user:
                    asso.dislike_count_from_user += 1
                    tag_stats['dislike_count_from_user'] = \
                        asso.dislike_count_from_user
                    tag_stats['dislike_count_from_article'] = \
                        asso.dislike_count_from_article
                    break
            else:
                asso = TagDislikeAssociation(dislike_count_from_user=1)
                asso.tag = tag
                asso.user = user
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return jsonify(tag_stats), 200
