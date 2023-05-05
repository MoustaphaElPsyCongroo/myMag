#!/usr/bin/python3
"""Cronjob function for fetching of new articles to add to the database"""
from api.v1.utils import fetch_articles, parse_save_articles
from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError
from datetime import timedelta, datetime
from models.tag import Tag
from models.feed import Feed
from models import storage
from time import sleep


def fetch_new_articles():
    """Poll each feed in database for new articles,
    with different frequencies depending on their
    average number of articles per week
    """
    # Fetch articles only if the feed is active and has followers
    feeds = storage.query(Feed).filter(
        Feed.active.is_(True), Feed.feed_users.any()).all()

    articles_fetched_this_minute = 0
    fetching_start = datetime.now()

    for feed in feeds:
        time_since_last_update = datetime.now() - feed.updated_at
        print('feed_id: ', feed.id)
        print('updated_at: ', feed.updated_at)
        print('timespan since update: ', datetime.now() - feed.updated_at)

        """
        Update rules:
        - 0 articles per week (value never calculated, new feed): check feed
        every 10 minutes. Will stay 0 for at most 1 day
        - >= 300 articles per week: check feed every 10 minutes
        - between 150 - 299 articles per week: check feed every 30 minutes
        - between 90 - 149 articles per week: check feed every hour
        - between 30 - 89 articles per week: check feed every two hours
        - between 6 - 29 articles per week: check feed every 3 hours
        - between 1 - 5 articles per week: check feed once per day.
        """
        update_rules = [
            feed.articles_per_week == 0
            and time_since_last_update > timedelta(minutes=10),
            feed.articles_per_week >= 300
            and time_since_last_update > timedelta(minutes=10),
            feed.articles_per_week >= 150
            and feed.articles_per_week < 300
            and time_since_last_update > timedelta(minutes=30),
            feed.articles_per_week >= 90
            and feed.articles_per_week < 150
            and time_since_last_update > timedelta(hours=1),
            feed.articles_per_week >= 30
            and feed.articles_per_week < 90
            and time_since_last_update > timedelta(hours=2),
            feed.articles_per_week >= 6
            and feed.articles_per_week < 30
            and time_since_last_update > timedelta(hours=3),
            feed.articles_per_week >= 1
            and feed.articles_per_week < 6
            and time_since_last_update > timedelta(days=1)
        ]

        if any(update_rules):
            # print("It's been more than 10 minutes")
            try:
                articles = fetch_articles(feed)
            except FeedInactiveError:
                feed.active = False
                continue
            except FeedNotFoundError:
                continue
            else:
                # Prevent fetching more than 570 articles per minute, to
                # prevent hitting Google NLP API's rate limit (of 600).
                if (
                    articles_fetched_this_minute > 570
                    and datetime.now() - fetching_start < timedelta(minutes=1)
                ):
                    sleep(60)
                elif datetime.now() - fetching_start > timedelta(minutes=1):
                    articles_fetched_this_minute = 0
                    fetching_start = datetime.now()

                feed_article_save_status = parse_save_articles(articles, feed)
                print(feed_article_save_status)
                articles_added = feed_article_save_status['articles added']
                articles_fetched_this_minute += articles_added
                print('articles fetched this minute: ',
                      articles_fetched_this_minute)

        else:
            # print('It has not been more than 10 minutes')
            continue
