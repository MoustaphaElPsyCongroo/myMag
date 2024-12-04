#!/usr/bin/env python3
"""Tests for feed_articles utils"""

import inspect
import unittest

import pycodestyle
from decouple import config


class TestExceptionsDocs(unittest.TestCase):
    """Tests to check the documentation and style of feed_articles utils"""

    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""

        import api.v1.utils.feed_articles as feed_articles_utils

        cls.feed_articles_utils_f = inspect.getmembers(
            feed_articles_utils, inspect.isfunction
        )

    def setUp(self):
        if config("MYSQL_ENV") != "test":
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database"""
            )

    def test_pep8_conformance(self):
        """Test that api/v1/utils/feed_articles.py conforms to PEP8."""
        for path in [
            "api/v1/utils/feed_articles.py",
            "tests/test_api/test_v1/test_utils/test_feed_articles.py",
        ]:
            with self.subTest(path=path):
                errors = pycodestyle.Checker(path).check_all()
                self.assertEqual(errors, 0)

    def test_module_docstring(self):
        """Test for the existence of feed_articles utils module docstring"""
        import api.v1.utils.feed_articles as feed_articles_utils

        self.assertIsNot(
            feed_articles_utils.__doc__,
            None,
            "api/v1/utils/feed_articles.py needs a docstring",
        )
        self.assertTrue(
            len(feed_articles_utils.__doc__) > 1,
            "api/v1/utils/feed_articles.py needs a docstring",
        )

    def test_feed_articles_utils_func_docstrings(self):
        """Test for the presence of docstrings in feed_articles utils"""
        for func in self.feed_articles_utils_f:
            self.assertIsNot(
                func[1].__doc__,
                None,
                "{:s} method needs a docstring".format(func[0]),
            )
            self.assertTrue(
                len(func[1].__doc__) >= 1,
                "{:s} method needs a docstring".format(func[0]),
            )
