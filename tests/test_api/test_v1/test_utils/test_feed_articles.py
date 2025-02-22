#!/usr/bin/env python3
"""Tests for feed_articles utils"""

import inspect
import unittest
from os.path import getsize

import pycodestyle
from decouple import config

from models import storage
from models.tag import Tag


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


class TestExtractArticleContent(unittest.TestCase):
    """Tests for extract_article_content util"""

    def test_headers(self):
        """Test that headers file is not empty"""
        self.assertGreater(getsize("api/v1/headers.json"), 0)


class TestDedupKeywordsAgainstDB(unittest.TestCase):
    """Tests for dedup_keywords_against_db util"""

    @classmethod
    def setUpClass(cls):
        """Set up for this class' tests"""
        import api.v1.utils.feed_articles as feed_articles_utils

        cls.feed_articles = feed_articles_utils

    def test_keyword_has_correct_format(self):
        """Test that the added keyword has the correct format of
        [(name, confidence, type)]"""
        db_keyword = Tag(name="Tennis", type="keyword")
        storage.new(db_keyword)
        storage.save()

        all_tags = []
        keywords = [("Tennis", 0.9999, "keyword")]
        self.feed_articles.dedup_keywords_against_db(keywords, all_tags)
        self.assertEqual(all_tags[0][0], "Tennis")
        self.assertEqual(all_tags[0][1], 0.9999)
        self.assertEqual(all_tags[0][2], "keyword")

    def test_exact_is_added_once(self):
        """Test that a Yake keyword that is an exact match of one in database
        is only added once to all_tags"""
        db_keyword = Tag(name="Tennis", type="keyword")
        storage.new(db_keyword)
        storage.save()

        all_tags = []
        keywords = [("Tennis", 0.9999, "keyword")]
        self.feed_articles.dedup_keywords_against_db(keywords, all_tags)
        all_tag_names = [kw[0] for kw in all_tags]
        self.assertIn(keywords[0][0], all_tag_names)
        self.assertEqual(len(all_tags), 1)

    def test_near_exact_is_not_added(self):
        """Test that a near exact keyword extracted by Yake is considered a
        duplicate and not added to all_tags, so that only its matching keyword
        is added"""
        db_keyword = Tag(name="Révolution", type="keyword")
        storage.new(db_keyword)
        storage.save()

        all_tags = []
        keywords = [("révolution", 0.9999, "keyword")]
        self.feed_articles.dedup_keywords_against_db(keywords, all_tags)
        all_tag_names = [kw[0] for kw in all_tags]
        self.assertNotIn(keywords[0][0], all_tag_names)
