#!/usr/bin/python3
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.article import Article
from models.tag import Tag, TagLikeAssociation
from models.user import User
from api.v1.utils.feed_articles import serialize_articles


@app_views.route('/users/<user_id>/articles/liked')
def get_liked_articles(user_id):
    """GET all liked articles from a user's subscribed feeds"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    if not user.liked_articles:
        abort(404, description="No liked articles yet")

    liked_articles = serialize_articles(user.liked_articles)
    return jsonify(liked_articles), 200


@app_views.route('/users/<user_id>/articles/liked', methods=['POST'])
def like_article(user_id):
    """Make a user like an article, incrementing its tags' likes count

        body:
            article_id: <article_id>
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    try:
        req = request.get_json()
        if req is None:
            abort(400, description='Not a JSON')
        elif req.get('article_id') is None:
            abort(400, description='Missing article_id')
        else:
            article_id = req.get('article_id')
            article = storage.get(Article, article_id)

            if article is None:
                abort(404, description="The specified article doesn't exist")

            tag_article_associations = article.article_tag_associations
            tags = [asso.tag for asso in tag_article_associations]

            for tag in tags:
                for asso in tag.tag_like_associations:
                    if asso.user == user:
                        asso.like_count_from_article += 1
                        break
                else:
                    asso = TagLikeAssociation(like_count_from_article=1)
                    asso.tag = tag
                    asso.user = user
            user.liked_articles.append(article)
            storage.save()

            tag_counts = []
            for tag in tags:
                slot = {}
                slot['name'] = tag.name
                for assoc in tag.tag_like_associations:
                    if assoc.user == user:
                        slot['likes from article'] = \
                            assoc.like_count_from_article
                        slot['likes from user'] = assoc.like_count_from_user
                tag_counts.append(slot)
    except ValueError:
        abort(400, description='Not a JSON')
    return jsonify(tag_counts), 200
