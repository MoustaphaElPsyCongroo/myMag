#!/usr/bin/python3
"""
Tests for the feeds API views
"""

from decouple import config
from models import storage
from models.feed import Feed
import unittest
import requests

BACKEND_URL = config('BACKEND_URL')


class TestFeed(unittest.TestCase):
    """Tests for the Users API views"""
    @classmethod
    def setUpClass(cls):
        """Prepare dummy feeds and add it to database for tests"""
        feed = Feed(
            name='Test feed',
            link='link'
        )

        feed2 = Feed(
            name='Test feed2',
            link='link2'
        )

        storage.new_all([feed, feed2])
        storage.save()
        cls.feed = feed
        cls.feed2 = feed2

    def setUp(self):
        if config('MYSQL_ENV') != 'test':
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database""")

    def test_get_feeds(self):
        """Test GETing all feeds"""
        feed = self.feed
        feed2 = self.feed2

        req = requests.get(f'{BACKEND_URL}/feeds')
        self.assertEqual(req.status_code, 200)
        j = req.json()
        self.assertTrue(len(j) == 2)

        for feed in req.json():
            self.assertTrue(feed['id'] or feed2['id'] in feed.values())

    def test_subscribe_user_to_feed(self):
        """Test making a user subscribe to a feed"""
        feed_name = 'Test feed3'
        req = requests.post(f'{BACKEND_URL}/feeds', json={
            "name": feed_name,
            "link": "Test link"
        })

        self.assertEqual(req.status_code, 201)
        j = req.json()
        j['name'] = feed_name
