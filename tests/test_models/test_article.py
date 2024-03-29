#!/usr/bin/python3
"""
Tests for the Article model
"""

from decouple import config
import inspect
from models.base_model import BaseModel
from models.article import Article
from models.user import User
from models.feed import Feed
from models.tag import Tag, TagArticleAssociation
from models import storage
import pycodestyle
import unittest
from datetime import datetime


class TestArticleDocs(unittest.TestCase):
    """Tests to check the documentation and style of Article class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.article_f = inspect.getmembers(Article, inspect.isfunction)

    def setUp(self):
        if config('MYSQL_ENV') != 'test':
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database""")

    def test_pycodestyle_conformance_article(self):
        """Test that models/article.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(['models/article.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pycodestyle_conformance_test_article(self):
        """Test that
        tests/test_models/test_article.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(
            ['tests/test_models/test_article.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_article_module_docstring(self):
        """Test for the article.py module docstring"""
        self.assertIsNot(Article.__doc__, None,
                         "article.py needs a docstring")
        self.assertTrue(len(Article.__doc__) >= 1,
                        "article.py needs a docstring")

    def test_article_class_docstring(self):
        """Test for the article class docstring"""
        self.assertIsNot(Article.__doc__, None,
                         "article class needs a docstring")
        self.assertTrue(len(Article.__doc__) >= 1,
                        "article class needs a docstring")

    def test_article_func_docstrings(self):
        """Test for the presence of docstrings in article methods"""
        for func in self.article_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestArticle(unittest.TestCase):
    """Tests for the Article class"""

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
        self.assertTrue(hasattr(article, "description"))
        self.assertTrue(hasattr(article, "publish_date"))
        self.assertTrue(hasattr(article, "shares"))
        self.assertTrue(hasattr(article, "article_liked_by"))
        self.assertTrue(hasattr(article, "article_disliked_by"))
        self.assertTrue(hasattr(article, "article_read_by"))
        self.assertTrue(hasattr(article, "article_tag_associations"))

    def test_to_dict_creates_dict(self):
        """Test that to_dict method creates a dictionary"""
        ar = Article()
        new_d = ar.to_dict()
        self.assertEqual(type(new_d), dict)
        for attr in ar.__dict__:
            if attr != '_sa_instance_state':
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_str(self):
        """test that the str method has the correct output"""
        article = Article()
        string = "[Article] ({}) {}".format(article.id, article.__dict__)
        self.assertEqual(string, str(article))

    def test_like(self):
        """Test article likes"""
        feed = Feed(
            name="FeedName",
            link="FeedUrl"
        )

        storage.new(feed)

        article = Article(
            feed_id=feed.id,
            title="ArticleTitle",
            description="ArticleDescription",
            publish_date=datetime.now(),
            shares=150
        )

        user = User(
            email="UserEmail",
            name='UserName',
            profile_pic="UserProfilepic"
        )

        storage.new(article)
        storage.new(user)
        article.article_liked_by.append(user)

        storage.save()

        found_user = storage.get(User, user.id)
        self.assertTrue(article in found_user.liked_articles)

        dummy = Article(
            feed_id=feed.id,
            title="ArticleTitle",
            description="ArticleDescription",
            publish_date=datetime.now(),
            shares=50
        )

        storage.new(dummy)

        self.assertFalse(dummy in found_user.liked_articles)

    def test_tag_associations(self):
        """Test article tag Association object"""
        feed = Feed(
            name="FeedName",
            link="FeedUrl"
        )

        storage.new(feed)

        article = Article(
            feed_id=feed.id,
            title="ArticleTitle",
            description="ArticleDescription",
            publish_date=datetime.now(),
            shares=150
        )

        storage.new(article)

        assoc = TagArticleAssociation(confidence=0.95)
        assoc.tag = Tag(
            name="TagName",
            type='Tag'
        )

        article.article_tag_associations.append(assoc)
        storage.save()

        for asso in article.article_tag_associations:
            if assoc.tag.id == asso.tag.id:
                confidence = asso.confidence
                tag = asso.tag

        self.assertEqual(confidence, 0.95)
        self.assertEqual(assoc.tag, tag)
