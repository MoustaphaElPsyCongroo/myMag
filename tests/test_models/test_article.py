#!/usr/bin/python3
"""
Tests for the Article model
"""

import inspect
import unittest

import pycodestyle
from decouple import config

from models.article import Article
from models.base_model import BaseModel


class TestArticleDocs(unittest.TestCase):
    """Tests to check the documentation and style of Article class"""

    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.article_f = inspect.getmembers(Article, inspect.isfunction)

    def setUp(self):
        if config("MYSQL_ENV") != "test":
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database"""
            )

    def test_pycodestyle_conformance_article(self):
        """Test that models/article.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(["models/article.py"])
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_pycodestyle_conformance_test_article(self):
        """Test that
        tests/test_models/test_article.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(
            ["tests/test_models/test_article.py"]
        )
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_article_module_docstring(self):
        """Test for the article.py module docstring"""
        self.assertIsNot(Article.__doc__, None, "article.py needs a docstring")
        self.assertTrue(
            len(Article.__doc__) >= 1, "article.py needs a docstring"
        )

    def test_article_class_docstring(self):
        """Test for the article class docstring"""
        self.assertIsNot(
            Article.__doc__, None, "article class needs a docstring"
        )
        self.assertTrue(
            len(Article.__doc__) >= 1, "article class needs a docstring"
        )

    def test_article_func_docstrings(self):
        """Test for the presence of docstrings in article methods"""
        for func in self.article_f:
            self.assertIsNot(
                func[1].__doc__,
                None,
                "{:s} method needs a docstring".format(func[0]),
            )
            self.assertTrue(
                len(func[1].__doc__) >= 1,
                "{:s} method needs a docstring".format(func[0]),
            )


class TestArticle(unittest.TestCase):
    """Tests for the Article model"""

    def test_is_subclass(self):
        """Test that Article is a subclass of BaseModel"""
        article = Article()
        self.assertIsInstance(article, BaseModel)
        self.assertTrue(hasattr(article, "id"))
        self.assertTrue(hasattr(article, "created_at"))
        self.assertTrue(hasattr(article, "updated_at"))

    def test_attributes(self):
        """Test that Article has the right attributes"""
        article = Article()
        self.assertTrue(hasattr(article, "feed_id"))
        self.assertTrue(hasattr(article, "title"))
        self.assertTrue(hasattr(article, "image"))
        self.assertTrue(hasattr(article, "link"))
        self.assertTrue(hasattr(article, "description"))
        self.assertTrue(hasattr(article, "publish_date"))
        self.assertTrue(hasattr(article, "shares"))
        self.assertTrue(hasattr(article, "article_feed"))
        self.assertTrue(hasattr(article, "article_liked_by"))
        self.assertTrue(hasattr(article, "article_disliked_by"))
        self.assertTrue(hasattr(article, "article_read_by"))
        self.assertTrue(hasattr(article, "article_tag_associations"))
        self.assertTrue(hasattr(article, "article_user_score_associations"))
