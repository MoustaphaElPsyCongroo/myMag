#!/usr/bin/python3
"""Cron job functions"""
from models.tag import Tag
from models import storage


def populate_tags():
    """Add the tags from taglist.txt and current trends to the database"""


def fetch_new_articles():
    """Poll each feed in database for new articles,
    with different frequencies depending on their
    average number of articles per week
    """


def get_random_headers_list():
    """Get new random headers from API and save them in headers.json"""
