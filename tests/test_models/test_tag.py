#!/usr/bin/python3
"""
Tests for the Tag model
"""

import inspect
import unittest

import pycodestyle
from decouple import config

from models.base_model import BaseModel
from models.tag import Tag


class TestTagDocs(unittest.TestCase):
    """Tests to check the documentation and style of Tag class"""

    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.tag_f = inspect.getmembers(Tag, inspect.isfunction)

    def setUp(self):
        if config("MYSQL_ENV") != "test":
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database"""
            )

    def test_pycodestyle_conformance_tag(self):
        """Test that models/tag.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(["models/tag.py"])
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_pycodestyle_conformance_test_tag(self):
        """Test that
        tests/test_models/test_tag.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(["tests/test_models/test_tag.py"])
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_tag_module_docstring(self):
        """Test for the tag.py module docstring"""
        self.assertIsNot(Tag.__doc__, None, "tag.py needs a docstring")
        self.assertTrue(len(Tag.__doc__) >= 1, "tag.py needs a docstring")

    def test_tag_class_docstring(self):
        """Test for the Tag class docstring"""
        self.assertIsNot(Tag.__doc__, None, "Tag class needs a docstring")
        self.assertTrue(len(Tag.__doc__) >= 1, "Tag class needs a docstring")

    def test_tag_func_docstrings(self):
        """Test for the presence of docstrings in Tag methods"""
        for func in self.tag_f:
            self.assertIsNot(
                func[1].__doc__,
                None,
                "{:s} method needs a docstring".format(func[0]),
            )
            self.assertTrue(
                len(func[1].__doc__) >= 1,
                "{:s} method needs a docstring".format(func[0]),
            )


class TestTag(unittest.TestCase):
    """Tests for the Tag model"""

    def test_is_subclass(self):
        """Test that Tag is a subclass of BaseModel"""
        tag = Tag()
        self.assertIsInstance(tag, BaseModel)
        self.assertTrue(hasattr(tag, "id"))
        self.assertTrue(hasattr(tag, "created_at"))
        self.assertTrue(hasattr(tag, "updated_at"))
