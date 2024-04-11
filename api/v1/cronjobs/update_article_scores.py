#!/usr/bin/python3
import logging
from datetime import datetime, timedelta

from sqlalchemy import or_

from api.v1.utils.user_articles import calculate_updated_article_scores
from models import storage
from models.article import Article, ArticleUserScoreAssociation
from models.user import User

logging = logging.getLogger(__name__)


def update_article_scores():
    """Update the score of all unread articles of a user, with different
    frequencies depending on their last read date.

        Update rules:
        - Last read under 30 minutes ago: score every ten minutes
        - Last read between 30 and 1 hour ago: score every 30 minutes
        - Last read between 1 - 2 hours ago: score every hour
        - Last read between 2 - 4 hours ago: score every two hours
        - Last read between 4 - 10 hours ago: score every three hours
        - Last read between 10 - a day ago: score every seven hours
        - Last read more than a day ago: don't update past the initial score
    """
    scoring_start_date = datetime.now()
    ten_minutes_ago = scoring_start_date - timedelta(minutes=10)
    thirty_minutes_ago = scoring_start_date - timedelta(minutes=30)
    one_hour_ago = scoring_start_date - timedelta(hours=1)
    two_hours_ago = scoring_start_date - timedelta(hours=2)
    three_hours_ago = scoring_start_date - timedelta(hours=3)
    four_hours_ago = scoring_start_date - timedelta(hours=4)
    seven_hours_ago = scoring_start_date - timedelta(hours=7)
    ten_hours_ago = scoring_start_date - timedelta(hours=10)
    one_day_ago = scoring_start_date - timedelta(days=1)

    users = (
        storage.query(User)
        .filter(
            or_(
                (User.last_scoring_date.is_(None)),
                (
                    (User.last_read_date >= thirty_minutes_ago)
                    & (User.last_scoring_date <= ten_minutes_ago)
                ),
                (
                    (User.last_read_date < thirty_minutes_ago)
                    & (User.last_read_date >= one_hour_ago)
                    & (User.last_scoring_date <= thirty_minutes_ago)
                ),
                (
                    (User.last_read_date < one_hour_ago)
                    & (User.last_read_date >= two_hours_ago)
                    & (User.last_scoring_date <= one_hour_ago)
                ),
                (
                    (User.last_read_date < two_hours_ago)
                    & (User.last_read_date >= four_hours_ago)
                    & (User.last_scoring_date <= two_hours_ago)
                ),
                (
                    (User.last_read_date < four_hours_ago)
                    & (User.last_read_date >= ten_hours_ago)
                    & (User.last_scoring_date <= three_hours_ago)
                ),
                (
                    (User.last_read_date < ten_hours_ago)
                    & (User.last_read_date >= one_day_ago)
                    & (User.last_scoring_date <= seven_hours_ago)
                ),
            )
        )
        .all()
    )

    for user in users:
        user_id = user.id
        read_ids = (
            storage.query(Article.id)
            .join(User.read_articles)
            .filter(User.id == user_id)
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

            asso.score_from_time = scores["score_from_time"]
            asso.score_from_tags = scores["score_from_tags"]
            asso.total_score = scores["total_score"]
            asso.last_scoring_date = datetime.now()

            if scores["total_score"] <= 0:
                user.read_articles.append(asso.article)
        user.last_scoring_date = datetime.now()
    storage.save()
    storage.close()
