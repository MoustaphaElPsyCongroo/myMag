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
    if asso:
        print("article title dans user_articles test: ", asso.article.title)
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

    # new score after percentage loss = score * (1 - percentage)**time
    # time being the days after 16h or the hours after 30 min. We are not
    # guaranteed to update scores regularly (update frequency depending on user
    # connection frequency) so updating must take into account hours
    if article_date_delta.days > 0:
        single_day_percentage_points = 25
        days = article_date_delta.days - 1
        # weeks = article_date_delta.days // 7
        if article_date > last_scoring_date:
            score = calculate_timerot_score_for_firstday(
                article_date, last_scoring_date, one_hour_ago, score
            )
        if last_scoring_delta.days > 0:
            percentage = (single_day_percentage_points + days * 5) / 100
            logging.info("%s days scoring percentage %s", days + 1, percentage)
            score *= (1 - percentage) ** last_scoring_delta.days
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
        The default score acts as a recency bonus. Article loses this bonus
        due to time rot.
        - Article older than 30 minutes: -10% bonus pts
        - Older than 1 hour: -8% pts
        - Each subsequent hour until 3h excl: -8% pts
        - Each subsequent hour from 3h until 8h excl: -6%
        - Each subsequent hour from 8h until 16h incl: -7%
        - After 16h, article loses 25% per subsequent day, with +5
        percentage points per day
        (so an article published 8h ago = 52 pts)
        (article published 16h ago = 29 pts)
        (article published 1w ago = 0 bonus pts)

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
                {"confidence": 0.3, "name": "Mars"},
                {"confidence": 0.793886, "name": "Business & Industrial"},
                {"confidence": 0.793886, "name": "Space Technology"},
                {"confidence": 0.397247, "name": "Technology News"},
                {"confidence": 0.793886, "name": "Aerospace & Defense"},
                {"confidence": 0.397247, "name": "News"},
                {"confidence": 0.571891, "name": "Astronomy"},
                {"confidence": 0.3, "name": "MOXIE"}
            ]
            1 like on this article: 57 pts
            1 like on article with same tags: 66 pts
            1 like on Science: + 11.4 pts = 77 pts
            If article with same tags was published now: 177 pts.
            After 8h: 129 pts
            After 12 days: 77 pts.

            1 dislike on Aerospace & Defense with article like kept: 161
            pts (-15.8)
            1 dislike on some earlier article with 3 first tags in common,
            other different with same confidence values: -33 pts to this
            article (128 pts)
            3 dislikes on Aerospace & Defense: -47.7.

            Total:
            Article published now: 81
            After 8h: 33 pts
            After 2d: 0 pts
        )
        Article at 0 will be automatically marked as read
    """
    asso = article_user_score_association
    score_from_time = asso.score_from_time or 100
    score_from_tags = 0
    scoring_start_date = datetime.now()

    logging.info("score before calculating: %s", asso.total_score)

    # Articles start with no last_scoring_date by default
    if asso.last_scoring_date:
        logging.info("Calculating time rot")
        score_from_time = calculate_timerot_score(
            asso.article.created_at,
            asso.last_scoring_date,
            scoring_start_date,
            score_from_time,
        )
        score_from_time = round(score_from_time)
        logging.info("score after time rot calculated: %s", score_from_time)

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
    total_score = round(score_from_tags + score_from_time)
    logging.info("total score %s", total_score)
    logging.info("------end------\n")
    return {
        "score_from_tags": score_from_tags,
        "score_from_time": score_from_time,
        "total_score": total_score,
    }
