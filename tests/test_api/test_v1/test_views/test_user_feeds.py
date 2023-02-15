#!/usr/bin/python3
"""
Tests for the user_feeds API views
"""

from decouple import config
from models import storage
from models.feed import Feed
from models.user import User
import unittest
import requests

BACKEND_URL = config('BACKEND_URL')


class TestFeed(unittest.TestCase):
    """Tests for the Users API views"""
    @classmethod
    def setUpClass(cls):
        """Prepare a dummy user and add it to database for tests"""
        user = User(
            email='email@mail.mail',
            name='Test user',
            profile_pic='pic'
        )

        storage.new(user)
        storage.save()
        cls.user = user

    def setUp(self):
        if config('MYSQL_ENV') != 'test':
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database""")

    def test_get_user_feeds(self):
        """Test GETing a user's feeds"""
        user = self.user
        user_id = user.id

        feed1 = Feed(
            name='Test feed',
            link='link'
        )
        feed2 = Feed(
            name='Test feed2',
            link='link2'
        )

        storage.new_all([feed1, feed2])
        feed1.feed_users.append(user)
        feed2.feed_users.append(user)
        storage.save()

        req = requests.get(f'{BACKEND_URL}/users/{user_id}/feeds')
        self.assertEqual(req.status_code, 200)
        j = req.json()
        self.assertTrue(len(j) == 2)

        for feed in req.json():
            self.assertTrue(feed1.id or feed2.id in feed.values())

    def test_subscribe_user_to_feed(self):
        """Test making a user subscribe to a feed"""
        user = self.user
        user_id = user.id

        feed = Feed(
            name='Test feed',
            link='link'
        )

        storage.new(feed)
        storage.save()
        feed_id = feed.id

        req = requests.post(f'{BACKEND_URL}/users/{user_id}/feeds', json={
            "feed_id": feed_id
        })

        self.assertEqual(req.status_code, 200)
        self.assertTrue(feed in user.user_feeds)
