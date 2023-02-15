#!/usr/bin/python3
"""
Tests for the User model
"""

from decouple import config
import inspect
from models.user import User
from models.base_model import BaseModel
import pycodestyle
import unittest


class TestUserDocs(unittest.TestCase):
    """Tests to check the documentation and style of User class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.user_f = inspect.getmembers(User, inspect.isfunction)

    def setUp(self):
        if config('MYSQL_ENV') != 'test':
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database""")

    def test_pycodestyle_conformance_user(self):
        """Test that models/user.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(['models/user.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pycodestyle_conformance_test_user(self):
        """Test that
        tests/test_models/test_user.py conforms to pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(
            ['tests/test_models/test_user.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_user_module_docstring(self):
        """Test for the user.py module docstring"""
        self.assertIsNot(User.__doc__, None,
                         "user.py needs a docstring")
        self.assertTrue(len(User.__doc__) >= 1,
                        "user.py needs a docstring")

    def test_user_class_docstring(self):
        """Test for the User class docstring"""
        self.assertIsNot(User.__doc__, None,
                         "User class needs a docstring")
        self.assertTrue(len(User.__doc__) >= 1,
                        "User class needs a docstring")

    def test_user_func_docstrings(self):
        """Test for the presence of docstrings in User methods"""
        for func in self.user_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestUser(unittest.TestCase):
    """Tests for the User class"""

    def test_is_subclass(self):
        """Test that User is a subclass of BaseModel"""
        user = User()
        self.assertIsInstance(user, BaseModel)
        self.assertTrue(hasattr(user, "id"))
        self.assertTrue(hasattr(user, "created_at"))
        self.assertTrue(hasattr(user, "updated_at"))

    def test_attributes(self):
        """Test that User has the right attributes"""
        user = User()
        self.assertTrue(hasattr(user, "email"))
        self.assertTrue(hasattr(user, "name"))
        self.assertTrue(hasattr(user, "profile_pic"))
        self.assertTrue(hasattr(user, "user_feeds"))
        self.assertTrue(hasattr(user, "liked_articles"))
        self.assertTrue(hasattr(user, "disliked_articles"))
        self.assertTrue(hasattr(user, "read_articles"))
        self.assertTrue(hasattr(user, "user_tag_like_associations"))
        self.assertTrue(hasattr(user, "user_tag_dislike_associations"))

    def test_to_dict_creates_dict(self):
        """Test that to_dict method creates a dictionary"""
        cl = User()
        new_d = cl.to_dict()
        self.assertEqual(type(new_d), dict)
        for attr in cl.__dict__:
            if attr != '_sa_instance_state':
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_str(self):
        """test that the str method has the correct output"""
        user = User()
        string = "[User] ({}) {}".format(user.id, user.__dict__)
        self.assertEqual(string, str(user))
