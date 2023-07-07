#!/usr/bin/python3
"""Cronjob for feed stat extraction"""
from datetime import timedelta, datetime
from models.article import Article
from models.feed import Feed
from models import storage
from sqlalchemy import func
import logging

today = datetime.now()
one_week_ago = today - timedelta(weeks=1)
five_days_ago = today - timedelta(days=5)


def extract_weekly_stats():
    """Calculate and save weekly stats for feeds, such as:
    - article shares per week
    - articles per week
    Executes each day.
    """
    # When a feed is younger than a week, takes articles published this day
    # and multiplies * 5 working days to get an estimate for this week. I fixed
    # the case where every user unfollowed the feed, which will cease its
    # updates: now when the first user follows a feed (feed_users count goes
    # from 0 to 1), immediately update it.

    # Also if a feed never published  any article for the whole day, bump its
    # number to 1. So that if it's a dormant source, it will only be checked
    # once per day instead of every ten minutes.

    feeds = storage.query(Feed).all()

    for feed in feeds:
        logging.info('feed name: %s', feed.name)
        logging.info('feed id: %s', feed.id)
        shares_of_week = (
            storage.query(Article.shares)
            .filter(Article.feed_id == feed.id)
            .filter(Article.publish_date >= one_week_ago)
            .all()
        )

        articles_of_week_count = (
            storage.query(func.count(Article.id))
            .filter(Article.feed_id == feed.id)
            .filter(Article.publish_date >= one_week_ago)
            .scalar()
        )

        logging.info('articles of week count: %s', articles_of_week_count)

        calc_articles_of_week(feed, articles_of_week_count)
        if articles_of_week_count > 0 and feed.created_at <= five_days_ago:
            calc_avg_shares_of_week(
                feed, shares_of_week, articles_of_week_count)
        storage.save()
    storage.close()


def calc_articles_of_week(feed, articles_of_week_count):
    """Get articles published this week.

    When a feed is younger than a week, takes articles published this day
    and multiplies * 5 working days to get an estimate for this week.

    If a feed never published any article for the whole day, bump its
    number to 1. So that if it's a dormant source, it will only be checked
    once per day instead of every ten minutes."""
    if articles_of_week_count == 0:
        feed.articles_per_week = 1
    elif feed.created_at >= five_days_ago:
        feed.articles_per_week = articles_of_week_count * 5
    else:
        feed.articles_per_week = articles_of_week_count


def calc_avg_shares_of_week(feed, shares_of_week, articles_of_week_count):
    """Get average number of shares of articles this week"""
    total_shares = 0
    for shares in shares_of_week:
        total_shares += shares[0]
    feed.average_shares_per_week = total_shares / articles_of_week_count
