#!/usr/bin/python3
import logging
from datetime import datetime, timedelta

from sqlalchemy import or_

from api.v1.utils.user_articles import calculate_updated_article_scores_for_user
from models import storage
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
        calculate_updated_article_scores_for_user(user)
    storage.save()
    storage.close()
