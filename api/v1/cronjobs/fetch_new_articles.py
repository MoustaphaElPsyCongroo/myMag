#!/usr/bin/python3
"""Cronjob function for fetching of new articles to add to the database"""
from api.v1.utils.feed_articles import fetch_articles, parse_save_articles
from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError
from datetime import timedelta, datetime
from models.feed import Feed
from models import storage
from sqlalchemy import or_
from time import sleep


def fetch_new_articles():
    """Poll each feed in database for new articles,
    with different frequencies depending on their
    average number of articles per week

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
    # Fetch articles according to the update rules
    #  only if the feed is active and has followers
    fetching_start_date = datetime.now()
    ten_minutes_ago = fetching_start_date - timedelta(minutes=10)
    thirty_minutes_ago = fetching_start_date - timedelta(minutes=30)
    one_hour_ago = fetching_start_date - timedelta(hours=1)
    two_hours_ago = fetching_start_date - timedelta(hours=2)
    three_hours_ago = fetching_start_date - timedelta(hours=3)
    one_day_ago = fetching_start_date - timedelta(days=1)

    feeds = storage.query(Feed).filter(
        Feed.active.is_(True),
        Feed.feed_users.any(),
        or_(
            (
                (Feed.articles_per_week == 0) &
                (Feed.updated_at < ten_minutes_ago)
            ),
            (
                (Feed.articles_per_week >= 300) &
                (Feed.updated_at < ten_minutes_ago)
            ),
            (
                (Feed.articles_per_week >= 150) &
                (Feed.articles_per_week < 300) &
                (Feed.updated_at < thirty_minutes_ago)
            ),
            (
                (Feed.articles_per_week >= 90) &
                (Feed.articles_per_week < 150) &
                (Feed.updated_at < one_hour_ago)
            ),
            (
                (Feed.articles_per_week >= 30) &
                (Feed.articles_per_week < 90) &
                (Feed.updated_at < two_hours_ago)
            ),
            (
                (Feed.articles_per_week >= 6) &
                (Feed.articles_per_week < 30) &
                (Feed.updated_at < three_hours_ago)
            ),
            (
                (Feed.articles_per_week >= 1) &
                (Feed.articles_per_week < 6) &
                (Feed.updated_at < one_day_ago)
            )
        )
    ).all()

    articles_fetched_this_minute = 0
    for feed in feeds:
        print('fetching new articles for feed: ', feed.name)
        print('feed_id: ', feed.id)
        print('updated_at: ', feed.updated_at)
        print('timespan since update: ', datetime.now() - feed.updated_at)

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
                and datetime.now() - fetching_start_date < timedelta(minutes=1)
            ):
                print('fetched 570+ articles - sleeping for a minute')
                sleep(60)
                articles_fetched_this_minute = 0
            elif datetime.now() - fetching_start_date > timedelta(minutes=1):
                articles_fetched_this_minute = 0
                fetching_start_date = datetime.now()

            feed_article_save_status = parse_save_articles(articles, feed)
            print(feed_article_save_status)
            articles_added = feed_article_save_status['articles added']
            articles_fetched_this_minute += articles_added
            print('articles fetched this minute: ',
                  articles_fetched_this_minute)
