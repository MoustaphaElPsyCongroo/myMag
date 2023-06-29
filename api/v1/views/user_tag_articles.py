#!/usr/bin/python3
from api.v1.views import app_views
from api.v1.utils.pagination import paginate
from api.v1.utils.feed_articles import serialize_paginated_articles
from flask import jsonify, abort, request
from models import storage
from models.article import Article
from models.tag import TagLikeAssociation, TagDislikeAssociation
from models.user import User
from sqlalchemy import func


@app_views.route('/users/<user_id>/articles/liked/<int:page>')
def get_liked_articles(user_id, page):
    """GET all liked articles of a user"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")
    if page is None:
        abort(405, description="This route is paginated. Select a page")

    liked_articles_query = (
        storage.query(Article)
        .join(User.liked_articles)
        .filter(User.id == user_id)
    )

    liked_articles_count_query = (
        storage.query(func.count(Article.id))
        .join(User.liked_articles)
        .filter(User.id == user_id)
    )

    liked_articles_paginated = paginate(
        liked_articles_query, liked_articles_count_query, page, 30)

    if liked_articles_paginated.total == 0:
        abort(404, description="No liked articles yet")

    liked_articles = serialize_paginated_articles(
        liked_articles_paginated, user)
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
            liked_articles = user.liked_articles
            previously_disliked = False

            if article is None:
                abort(404, description="The specified article doesn't exist")
            if article in liked_articles:
                abort(405, description="Article already liked by the user")

            tag_article_associations = article.article_tag_associations
            tags = [asso.tag for asso in tag_article_associations]

            if article in user.disliked_articles:
                user.disliked_articles.remove(article)
                previously_disliked = True

            tag_counts = []
            for tag in tags:
                slot = {}
                slot['name'] = tag.name
                slot['likes_from_article'] = 1
                slot['likes_from_user'] = 0

                if previously_disliked:
                    for asso in tag.tag_dislike_associations:
                        if asso.user == user:
                            asso.dislike_count_from_article -= 1
                for asso in tag.tag_like_associations:
                    if asso.user == user:
                        asso.like_count_from_article += 1
                        slot['likes_from_article'] = \
                            asso.like_count_from_article
                        slot['likes_from_user'] = \
                            asso.like_count_from_user
                        break
                else:
                    asso = TagLikeAssociation(like_count_from_article=1)
                    asso.tag = tag
                    asso.user = user
                tag_counts.append(slot)
            liked_articles.append(article)
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return jsonify(tag_counts), 200


@app_views.route(
    '/users/<user_id>/articles/liked/<article_id>',
    methods=['DELETE'])
def delete_like_article(user_id, article_id):
    """Make a user cancel their like on an article"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    article = storage.get(Article, article_id)

    if article is None:
        abort(404, description="The specified article doesn't exist")
    if article not in user.liked_articles:
        abort(405, description="The specified article hasn't been liked")

    tag_article_associations = article.article_tag_associations
    tags = [asso.tag for asso in tag_article_associations]

    tag_counts = []
    for tag in tags:
        slot = {}
        slot['name'] = tag.name
        for asso in tag.tag_like_associations:
            if asso.user == user:
                asso.like_count_from_article -= 1
                slot['likes from article'] = \
                    asso.like_count_from_article
                slot['likes from user'] = asso.like_count_from_user
                break
        tag_counts.append(slot)
    user.liked_articles.remove(article)
    storage.save()
    return jsonify(tag_counts), 200


@app_views.route('/users/<user_id>/articles/disliked/<int:page>')
def get_disliked_articles(user_id, page):
    """GET all disliked articles of a user"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")
    if page is None:
        abort(405, description="This route is paginated. Select a page")

    disliked_articles_query = (
        storage.query(Article)
        .join(User.disliked_articles)
        .filter(User.id == user_id)
    )

    disliked_articles_count_query = (
        storage.query(func.count(Article.id))
        .join(User.disliked_articles)
        .filter(User.id == user_id)
    )

    disliked_articles_paginated = paginate(
        disliked_articles_query, disliked_articles_count_query, page, 30)

    if disliked_articles_paginated.total == 0:
        abort(404, description="No disliked articles yet")

    disliked_articles = serialize_paginated_articles(
        disliked_articles_paginated, user)
    return jsonify(disliked_articles), 200


@app_views.route('/users/<user_id>/articles/disliked', methods=['POST'])
def dislike_article(user_id):
    """Make a user dislike an article, incrementing its tags' dislikes count

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
            disliked_articles = user.disliked_articles
            previously_liked = False

            if article is None:
                abort(404, description="The specified article doesn't exist")
            if article in disliked_articles:
                abort(405, description="Article already disliked by the user")

            tag_article_associations = article.article_tag_associations
            tags = [asso.tag for asso in tag_article_associations]

            if article in user.liked_articles:
                user.liked_articles.remove(article)
                previously_liked = True

            tag_counts = []
            for tag in tags:
                slot = {}
                slot['name'] = tag.name
                slot['dislikes_from_article'] = 1
                slot['dislikes_from_user'] = 0

                if previously_liked:
                    for asso in tag.tag_like_associations:
                        if asso.user == user:
                            asso.like_count_from_article -= 1
                for asso in tag.tag_dislike_associations:
                    if asso.user == user:
                        asso.dislike_count_from_article += 1
                        slot['dislikes_from_article'] = \
                            asso.dislike_count_from_article
                        slot['dislikes_from_user'] = \
                            asso.dislike_count_from_user
                        break
                else:
                    asso = TagDislikeAssociation(dislike_count_from_article=1)
                    asso.tag = tag
                    asso.user = user
                tag_counts.append(slot)

            disliked_articles.append(article)
            storage.save()
    except ValueError:
        abort(400, description='Not a JSON')
    return jsonify(tag_counts), 200


@app_views.route(
    '/users/<user_id>/articles/disliked/<article_id>',
    methods=['DELETE'])
def delete_dislike_article(user_id, article_id):
    """Make a user cancel their dislike on an article"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="The specified user doesn't exist")

    article = storage.get(Article, article_id)

    if article is None:
        abort(404, description="The specified article doesn't exist")
    if article not in user.disliked_articles:
        abort(405, description="The specified article hasn't been liked")

    tag_article_associations = article.article_tag_associations
    tags = [asso.tag for asso in tag_article_associations]

    tag_counts = []
    for tag in tags:
        slot = {}
        slot['name'] = tag.name
        for asso in tag.tag_dislike_associations:
            if asso.user == user:
                asso.dislike_count_from_article -= 1
                slot['dislikes_from_article'] = \
                    asso.dislike_count_from_article
                slot['dislikes_from_user'] = asso.dislike_count_from_user
                break
        tag_counts.append(slot)
    user.disliked_articles.remove(article)
    storage.save()
    return jsonify(tag_counts), 200
