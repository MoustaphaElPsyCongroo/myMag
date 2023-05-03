#!/usr/bin/python3
"""Cron job functions"""
from models.tag import Tag
from models.feed import Feed
from models import storage


def populate_tags():
    """Add the tags from taglist.txt and current trends to the database"""


def fetch_new_articles():
    """Poll each feed in database for new articles,
    with different frequencies depending on their
    average number of articles per week
    """
    feeds = storage.query(Feed).all()


def get_random_headers_list():
    """Get new random headers from API and save them in headers.json"""


def extract_weekly_stats():
    """Calculate and save weekly stats for feeds, such as:
    article shares per week
    articles per week
    """


def get_articles_per_day():
    """Calculate and save the number of articles posted by feeds this day"""
