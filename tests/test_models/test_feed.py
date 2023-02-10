#!/usr/bin/python3
"""
Tests for the Feed model
"""

from decouple import config
import inspect
from models.feed import Feed
from models.base_model import BaseModel
import pycodestyle
import unittest


class TestFeedDocs(unittest.TestCase):
    """Tests to check the documentation and style of Feed class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.feed_f = inspect.getmembers(Feed, inspect.isfunction)

    def setUp(self):
        if config('MYSQL_ENV') != 'test':
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database""")

    def test_pycodestyle_conformance_feed(self):
        """Test that models/feed.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(['models/feed.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pycodestyle_conformance_test_feed(self):
        """Test that
        tests/test_models/test_feed.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(
            ['tests/test_models/test_feed.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_feed_module_docstring(self):
        """Test for the feed.py module docstring"""
        self.assertIsNot(Feed.__doc__, None,
                         "feed.py needs a docstring")
        self.assertTrue(len(Feed.__doc__) >= 1,
                        "feed.py needs a docstring")

    def test_feed_class_docstring(self):
        """Test for the Feed class docstring"""
        self.assertIsNot(Feed.__doc__, None,
                         "Feed class needs a docstring")
        self.assertTrue(len(Feed.__doc__) >= 1,
                        "Feed class needs a docstring")

    def test_feed_func_docstrings(self):
        """Test for the presence of docstrings in Feed methods"""
        for func in self.feed_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestFeed(unittest.TestCase):
    """Tests for the Feed class"""

    def test_is_subclass(self):
        """Test that Feed is a subclass of BaseModel"""
        feed = Feed()
        self.assertIsInstance(feed, BaseModel)
        self.assertTrue(hasattr(feed, "id"))
        self.assertTrue(hasattr(feed, "created_at"))
        self.assertTrue(hasattr(feed, "updated_at"))

    def test_attributes(self):
        """Test that Feed has the right attributes"""
        feed = Feed()
        self.assertTrue(hasattr(feed, "name"))
        self.assertTrue(hasattr(feed, "link"))
        self.assertTrue(hasattr(feed, "description"))
        self.assertTrue(hasattr(feed, "banner_img"))
        self.assertTrue(hasattr(feed, "etag"))
        self.assertTrue(hasattr(feed, "last_modified"))
        self.assertTrue(hasattr(feed, "active"))
        self.assertTrue(hasattr(feed, "average_shares_per_week"))
        self.assertTrue(hasattr(feed, "articles_per_week"))
        self.assertTrue(hasattr(feed, "feed_users"))
        self.assertTrue(hasattr(feed, "feed_articles"))

    def test_to_dict_creates_dict(self):
        """Test that to_dict method creates a dictionary"""
        cl = Feed()
        new_d = cl.to_dict()
        self.assertEqual(type(new_d), dict)
        for attr in cl.__dict__:
            self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_str(self):
        """test that the str method has the correct output"""
        feed = Feed()
        string = "[Feed] ({}) {}".format(feed.id, feed.__dict__)
        self.assertEqual(string, str(feed))
