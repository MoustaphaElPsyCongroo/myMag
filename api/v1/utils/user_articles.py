#!/usr/bin/python3
import logging
from datetime import datetime, timedelta

from models import storage
from models.article import Article, ArticleUserScoreAssociation
from models.user import User

logging = logging.getLogger(__name__)


def calculate_initial_article_score(article, feed):
    """Calculate the first score of an article for each user subscribed to the
    corresponding feed"""
    future_readers = feed.feed_users

    for user in future_readers:
        article_user_score_association = ArticleUserScoreAssociation()
        article_user_score_association.article = article
        article_user_score_association.user = user

        logging.info("Calculating initial score for article_id: %s", article.id)
        logging.info("title: %s", article.title)
        scores = calculate_updated_article_scores(article_user_score_association)
        article_user_score_association.score_from_time = scores["score_from_time"]
        article_user_score_association.score_from_tags = scores["score_from_tags"]
        article_user_score_association.total_score = scores["total_score"]
        article_user_score_association.last_scoring_date = datetime.now()


def calculate_initial_article_score_for_user(user, article):
    """Calculate the first score of an article for an user"""
    asso = (
        storage.query(ArticleUserScoreAssociation)
        .join(User)
        .join(Article)
        .filter(User.id == user.id)
        .filter(Article.id == article.id)
        .first()
    )
    # if asso:
    #     print("article title dans user_articles test: ", asso.article.title)
    if not asso:
        asso = ArticleUserScoreAssociation()
        asso.article = article
        asso.user = user

    logging.info("Calculating initial score for article_id: %s", article.id)
    logging.info("User id: %s", user.id)
    logging.info("title: %s", article.title)
    scores = calculate_updated_article_scores(asso)
    asso.score_from_time = scores["score_from_time"]
    asso.score_from_tags = scores["score_from_tags"]
    asso.total_score = scores["total_score"]
    asso.last_scoring_date = datetime.now()


def calculate_timerot_score(article_date, last_scoring_date, scoring_start_date, score):
    """Calculate the new bonus score of an article following its time rot"""
    thirty_minutes_ago = scoring_start_date - timedelta(minutes=30)
    one_hour_ago = scoring_start_date - timedelta(hours=1)
    sixteen_hours_ago = scoring_start_date - timedelta(hours=16)

    article_date_delta = scoring_start_date - article_date
    last_scoring_delta = scoring_start_date - last_scoring_date

    logging.info("article_date %s", article_date)
    logging.info("last scoring date %s", last_scoring_date)

    if article_date_delta.days > 0:
        percentage = 25 / 100
        days_penalty = 5 * article_date_delta.days
        # weeks = article_date_delta.days // 7

        # If the article date is more recent than the last time we updated scores
        # (while still being older than a day), it means we didn't cumulatively
        # calculate the score for the first day. So do it before calculating
        # the score for subsequent days
        if article_date > last_scoring_date:
            score = calculate_timerot_score_for_firstday(
                article_date, last_scoring_date, one_hour_ago, score
            )
        if last_scoring_delta.days > 0:
            logging.info(
                "%s days scoring penalty: %s", article_date_delta.days, days_penalty
            )
            score = score * (1 - percentage) - days_penalty
    elif article_date <= one_hour_ago and last_scoring_date <= one_hour_ago:
        score = calculate_timerot_score_for_firstday(
            article_date, last_scoring_date, one_hour_ago, score
        )
    elif (
        article_date <= thirty_minutes_ago
        and article_date >= sixteen_hours_ago
        and last_scoring_date <= thirty_minutes_ago
    ):
        logging.info("scoring article of 30min")
        score *= 1 - 0.1

    return score


def calculate_timerot_score_for_firstday(
    article_date, last_scoring_date, one_hour_ago, score
):
    """Calculates the new bonus score of an article following its time rot for
    its first day of existence. Check calculate_updated_article_scores's
    documentation for bonus score loss rules"""
    article_delta = one_hour_ago - article_date
    scoring_delta = one_hour_ago - last_scoring_date
    article_hours = article_delta.seconds // 3600 + 1
    scoring_hours = scoring_delta.seconds // 3600 + 1
    logging.info("article_hours: %s", article_hours)
    logging.info("scoring_hours %s", scoring_hours)

    # If scoring_hours > article_hours the article has never been scored
    # past 30 min. If more than an hour separate the two, it never has been
    # scored at all so add the missing 30 min difference.
    if scoring_hours > article_hours:
        if scoring_hours - article_hours > 1:
            score *= 1 - 0.1
        starting_hour = 1
        ending_hour = article_hours + 1
    elif scoring_hours < article_hours:
        starting_hour = article_hours - scoring_hours + 1
        ending_hour = article_hours + 1
    else:
        if article_date <= last_scoring_date and article_hours > 2:
            starting_hour = 2
            ending_hour = article_hours + 1
        else:
            starting_hour = 1
            ending_hour = article_hours + 1

    if ending_hour > 16:
        ending_hour == 17
    # Constructing and using the formula
    # score = (score * ((1 - %)**1.30min * (1 - %)**1-2h * (1 -
    # %)**3-8h)...)
    # would be confusing, so just just do a O(n.ending_hour) time
    # complexity loop instead

    for i in range(starting_hour, ending_hour):
        percentage = 1
        if i in range(3):
            percentage = 1 - 0.08
        if i in range(3, 8):
            percentage = 1 - 0.06
        if i in range(8, 17):
            percentage = 1 - 0.07
        score *= percentage

    return score


def calculate_updated_article_scores(article_user_score_association):
    """Calculate the score of an article after time rot and likes/dislikes

    Score rules:
    - Default score: 100
        Date
        The default score acts as a recency bonus. Article loses score
        due to time rot. For the first day this loss is cumulative, each
        percentage loss adds to the previous. After a day it stays cumulative
        only if user reads articles each day. Rationale: very active user has more
        chance to read old articles so can afford to see them lose score to time
        more quickly; occasional user will have more older articles buried under new
        ones, so slower timerot will give them more chance to see them if they
        are relevant.
        - Article older than 30 minutes: -10% bonus pts
        - Older than 1 hour: -8% pts
        - Each subsequent hour until 3h excl: -8% pts
        - Each subsequent hour from 3h until 8h excl: -6%
        - Each subsequent hour from 8h until 16h incl: -7%
        - After 16h, article loses 25% of its TOTAL score (score from tags
        included) + (5 * number of days) points each day (so an article at 100
        pts published 8h ago = 52 pts)
        (article published 16h ago = 29 pts)
        (article published 2d ago = 3 pts)
        (article published 3d ago = -12.75 pts)

        Tag
        Pts from likes on articles and tags are added to this bonus score
        - Liking article gives +1 pt to each tag like_count_from_article
        - Liking tag gives +1 pt to single tag like_count_from_user
        - Each like_count_from_article gives (confidence * 10 + count)
        - Each like_count_from_user gives (count * (confidence * 10) * 2)
        Same for dislikes
        (Exemple
            "tags": [
                {"confidence": 0.571891, "name": "Science"},
                {"confidence": 0.9, "name": "Mars"},
                {"confidence": 0.793886, "name": "Business & Industrial"},
                {"confidence": 0.793886, "name": "Space Technology"},
                {"confidence": 0.397247, "name": "Technology News"},
                {"confidence": 0.793886, "name": "Aerospace & Defense"},
                {"confidence": 0.397247, "name": "News"},
                {"confidence": 0.571891, "name": "Astronomy"},
                {"confidence": 0.9, "name": "MOXIE"}
            ]
            1 like on this article: 61 pts
            1 like on article with same tags: 69 pts
            1 like on Science: + 11.4 pts = 80 pts
            If article with same tags was published now: 180 pts.
            After 8h: 129 pts
            After 1d: 92 pts
            After 4d: 2 pts

            Same for dislikes:
            +1 dislike on Aerospace & Defense with previous article like kept: 64
            pts from tags (-15.8)
            +1 dislike on some earlier article with 3 first tags in common,
            other different with same confidence values: -69.5 pts to the new
            article's tags (-5 pts for tags total)
            3 dislikes on Mars: -54 (-59 total for the article's tags)

            Total:
            Such article published now: 41 pts
            After 30 min: 31 pts
            After 3h: 12 pts
            After 6h: exactly 0 pts
        )
        Article at 0 or less will be automatically marked as read
    """
    # Calculate updated score_from_tags and add it to the pure score
    asso = article_user_score_association
    previous_score_without_tags = asso.total_score - asso.score_from_tags
    scoring_start_date = datetime.now()

    logging.info("total score before calculating: %s", asso.total_score)
    logging.info(
        "score without tags before calculating: %s", previous_score_without_tags
    )

    tag_article_assos = asso.article.article_tag_associations
    like_assos = []
    dislike_assos = []

    for tag_article_asso in tag_article_assos:
        tag_confidence = tag_article_asso.confidence
        for like_asso in tag_article_asso.tag.tag_like_associations:
            if like_asso.user == asso.user:
                like_assos.append((like_asso, tag_confidence))
        for dislike_asso in tag_article_asso.tag.tag_dislike_associations:
            if dislike_asso.user == asso.user:
                dislike_assos.append((dislike_asso, tag_confidence))

    like_score = 0
    for like_asso in like_assos:
        like = like_asso[0]
        confidence = like_asso[1]
        like_count_from_article = like.like_count_from_article
        like_count_from_user = like.like_count_from_user

        if like_count_from_article >= 1:
            like_score += confidence * 10 + like_count_from_article
        like_score += like_count_from_user * (confidence * 10) * 2

    logging.info("Like score: %s", like_score)

    dislike_score = 0
    for dislike_asso in dislike_assos:
        dislike = dislike_asso[0]
        confidence = dislike_asso[1]
        dislike_count_from_article = dislike.dislike_count_from_article
        dislike_count_from_user = dislike.dislike_count_from_user

        if dislike_count_from_article >= 1:
            dislike_score += confidence * 10 + dislike_count_from_article
        dislike_score += dislike_count_from_user * (confidence * 10) * 2

    logging.info("Dislike score: %s", dislike_score)

    score_from_tags = round(like_score - dislike_score)
    updated_score = previous_score_without_tags + score_from_tags

    logging.info("Score from tags: %s", score_from_tags)
    logging.info("Updated score before timerot: %s", updated_score)

    # Substract the timerot from the new total score
    # Articles start with no last_scoring_date by default but should have one
    # when fetched so adding this check only as a fallback
    if asso.last_scoring_date:
        logging.info("Calculating time rot")
        updated_score = calculate_timerot_score(
            asso.article.created_at,
            asso.last_scoring_date,
            scoring_start_date,
            updated_score,
        )

    total_score = round(updated_score)
    logging.info("total score %s", total_score)
    logging.info("------end------\n")
    return {
        "score_from_tags": score_from_tags,
        "total_score": total_score,
    }


def calculate_updated_article_scores_for_user(user):
    """Calculate the score of all unread articles for a user"""
    user_id = user.id
    read_ids = (
        storage.query(Article.id).join(User.read_articles).filter(User.id == user_id)
    )

    unread_article_score_associations = (
        storage.query(ArticleUserScoreAssociation)
        .filter(ArticleUserScoreAssociation.article_id.not_in(read_ids))
        .filter(ArticleUserScoreAssociation.user_id == user_id)
        .all()
    )

    logging.info("Scoring user: %s", user_id)
    logging.debug("Last read date: %s", user.last_read_date)
    logging.debug("Last scoring date: %s", user.last_scoring_date)
    for asso in unread_article_score_associations:
        logging.info(
            "Calculating updated article score for article_id: %s", asso.article.id
        )
        logging.info("title: %s", asso.article.title)

        scores = calculate_updated_article_scores(asso)

        asso.score_from_tags = scores["score_from_tags"]
        asso.total_score = scores["total_score"]
        asso.last_scoring_date = datetime.now()

        if scores["total_score"] <= 0:
            user.read_articles.append(asso.article)
    user.last_scoring_date = datetime.now()
