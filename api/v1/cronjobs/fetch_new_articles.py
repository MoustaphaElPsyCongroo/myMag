#!/usr/bin/python3
"""Cronjob function for fetching of new articles to add to the database"""
from api.v1.utils import fetch_articles, parse_save_articles
from datetime import timedelta, datetime
from models.tag import Tag
from models.feed import Feed
from models import storage


def fetch_new_articles():
    """Poll each feed in database for new articles,
    with different frequencies depending on their
    average number of articles per week
    """
    # feeds = storage.query(Feed).all()
    # fetch_timespan = timedelta()

    # for feed in feeds:
    #     print('feed_id: ', feed.id)
    #     print('updated_at: ', feed.updated_at)
    #     print('timespan since update: ', datetime.now() - feed.updated_at)
    devto = storage.get(Feed, 'f5e0d5d4-607b-457a-95c3-5980cf6e9a6e')
    print('updated_at before fetching article: ', devto.updated_at)
    articles = fetch_articles(devto)
    print(parse_save_articles(articles, devto))
    print('updated_at after fetching article: ', devto.updated_at)
