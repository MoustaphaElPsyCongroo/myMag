#!/usr/bin/python3
"""Cronjob for feed stat extraction"""
from datetime import timedelta, datetime
from models.feed import Feed
from models import storage

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

    feeds = storage.all(Feed).values()
    for feed in feeds:
        articles_of_week = tuple(
            filter(filter_articles_of_week, feed.feed_articles))
        calc_articles_of_week(feed, articles_of_week)
        if articles_of_week and feed.created_at >= five_days_ago:
            calc_avg_shares_of_week(feed, articles_of_week)
    storage.close()


def calc_articles_of_week(feed, articles_of_week):
    """Get articles published this week.

    When a feed is younger than a week, takes articles published this day
    and multiplies * 5 working days to get an estimate for this week.

    If a feed never published any article for the whole day, bump its
    number to 1. So that if it's a dormant source, it will only be checked
    once per day instead of every ten minutes."""
    if not articles_of_week:
        feed.articles_per_week = 1
    elif feed.created_at >= five_days_ago:
        feed.articles_per_week = len(articles_of_week) * 5
    else:
        feed.articles_per_week = len(articles_of_week)


def calc_avg_shares_of_week(feed, articles_of_week):
    """Get average number of shares of articles this week"""
    total_shares = 0
    for article in articles_of_week:
        total_shares += article.shares
    feed.average_shares_per_week = total_shares / len(articles_of_week)


def filter_articles_of_week(article):
    """Filter out articles that are older than a week"""
    return True if article.updated_at <= one_week_ago else False
