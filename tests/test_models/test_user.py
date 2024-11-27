#!/usr/bin/python3
"""
Tests for the User model
"""

import inspect
import unittest

import pycodestyle
from decouple import config

from models.base_model import BaseModel
from models.user import User


class TestUserDocs(unittest.TestCase):
    """Tests to check the documentation and style of User class"""

    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.user_f = inspect.getmembers(User, inspect.isfunction)

    def setUp(self):
        if config("MYSQL_ENV") != "test":
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database"""
            )

    def test_pycodestyle_conformance_user(self):
        """Test that models/user.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(["models/user.py"])
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_pycodestyle_conformance_test_user(self):
        """Test that
        tests/test_models/test_user.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(["tests/test_models/test_user.py"])
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_user_module_docstring(self):
        """Test for the user.py module docstring"""
        self.assertIsNot(User.__doc__, None, "user.py needs a docstring")
        self.assertTrue(len(User.__doc__) >= 1, "user.py needs a docstring")

    def test_user_class_docstring(self):
        """Test for the User class docstring"""
        self.assertIsNot(User.__doc__, None, "User class needs a docstring")
        self.assertTrue(len(User.__doc__) >= 1, "User class needs a docstring")

    def test_user_func_docstrings(self):
        """Test for the presence of docstrings in User methods"""
        for func in self.user_f:
            self.assertIsNot(
                func[1].__doc__,
                None,
                "{:s} method needs a docstring".format(func[0]),
            )
            self.assertTrue(
                len(func[1].__doc__) >= 1,
                "{:s} method needs a docstring".format(func[0]),
            )


class TestUser(unittest.TestCase):
    """Tests for the User model"""

    def test_is_subclass(self):
        """Test that User is a subclass of BaseModel"""
        user = User()
        self.assertIsInstance(user, BaseModel)
        self.assertTrue(hasattr(user, "id"))
        self.assertTrue(hasattr(user, "created_at"))
        self.assertTrue(hasattr(user, "updated_at"))
