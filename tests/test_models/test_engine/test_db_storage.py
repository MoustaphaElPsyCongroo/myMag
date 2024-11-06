#!/usr/bin/python3
"""
Contains the TestDBStorageDocs and TestDBStorage classes
"""

import inspect
import unittest

import pycodestyle
from decouple import config

from models import storage
from models.article import Article
from models.engine.db_storage import DBStorage
from models.feed import Feed
from models.tag import Tag
from models.user import User

classes = {"Article": Article, "Feed": Feed, "Tag": Tag, "User": User}


class TestDBStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of DBStorage class"""

    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.dbs_f = inspect.getmembers(DBStorage, inspect.isfunction)

    def setUp(self):
        if config("MYSQL_ENV") != "test":
            self.fail(
                """You're on the prod database.
                Edit .env to test on the right database"""
            )

    def test_pycodestyle_conformance_db_storage(self):
        """Test that models/engine/db_storage.py conforms to Pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(["models/engine/db_storage.py"])
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_pycodestyle_conformance_test_db_storage(self):
        """Test that tests/test_models/test_db_storage.py
        conforms to Pycodestyle."""
        pycodestyles = pycodestyle.StyleGuide(quiet=True)
        result = pycodestyles.check_files(
            [
                "tests/test_models/test_engine/\
test_db_storage.py"
            ]
        )
        self.assertEqual(
            result.total_errors, 0, "Found code style errors (and warnings)."
        )

    def test_db_storage_module_docstring(self):
        """Test for the db_storage.py module docstring"""
        self.assertIsNot(
            DBStorage.__doc__, None, "db_storage.py needs a docstring"
        )
        self.assertTrue(
            len(DBStorage.__doc__) >= 1, "db_storage.py needs a docstring"
        )

    def test_db_storage_class_docstring(self):
        """Test for the DBStorage class docstring"""
        self.assertIsNot(
            DBStorage.__doc__, None, "DBStorage class needs a docstring"
        )
        self.assertTrue(
            len(DBStorage.__doc__) >= 1, "DBStorage class needs a docstring"
        )

    def test_dbs_func_docstrings(self):
        """Test for the presence of docstrings in DBStorage methods"""
        for func in self.dbs_f:
            self.assertIsNot(
                func[1].__doc__,
                None,
                "{:s} method needs a docstring".format(func[0]),
            )
            self.assertTrue(
                len(func[1].__doc__) >= 1,
                "{:s} method needs a docstring".format(func[0]),
            )


class TestDBStorage(unittest.TestCase):
    """Tests for the DBStorage class"""

    def test_all_returns_dict(self):
        """Test that all returns a dictionary"""
        self.assertIs(type(storage.all()), dict)

    def test_all_no_class(self):
        """Test that all returns all rows when no class is passed"""
        user = User(
            name="test", email="test@email.test", profile_pic="urlpic.nic"
        )
        storage.new(user)
        storage.save()
        all = storage.all()
        self.assertTrue(f"User.{user.id}" in all)

    def test_get(self):
        """Test that get properly retrieves one object, None if not found"""
        user = User(
            name="test", email="test@email.test", profile_pic="urlpic.nic"
        )

        storage.new(user)
        storage.save()

        obj = storage.get(User, user.id)
        self.assertEqual(obj, user)

        storage.delete(user)
        storage.save()

        dummy = storage.get(User, user.id)
        self.assertIsNone(dummy)

    def test_count(self):
        """Test that count properly gets the number of objects matching"""
        user = User(
            name="test", email="test@email.test", profile_pic="urlpic.nic"
        )

        storage.new(user)
        storage.save()

        storage_len = len(storage.all())
        self.assertEqual(storage.count(), storage_len)

        user_nb = len(storage.all(User).values())
        self.assertEqual(storage.count(User), user_nb)

        user_nb = len(storage.all(User).values())
        self.assertEqual(storage.count(User), user_nb)
