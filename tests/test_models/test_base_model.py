#!/usr/bin/python3
"""Test BaseModel for expected behavior and documentation"""

import inspect
import unittest
from unittest import mock

import pycodestyle

from models.base_model import BaseModel


class TestBaseModelDocs(unittest.TestCase):
    """Tests to check the documentation and style of BaseModel class"""

    @classmethod
    def setUpClass(self):
        """Set up for docstring tests"""
        self.base_funcs = inspect.getmembers(BaseModel, inspect.isfunction)

    def test_pep8_conformance(self):
        """Test that models/base_model.py conforms to PEP8."""
        for path in [
            "models/base_model.py",
            "tests/test_models/test_base_model.py",
        ]:
            with self.subTest(path=path):
                errors = pycodestyle.Checker(path).check_all()
                self.assertEqual(errors, 0)

    def test_module_docstring(self):
        """Test for the existence of module docstring"""
        self.assertIsNot(
            BaseModel.__doc__, None, "base_model.py needs a docstring"
        )
        self.assertTrue(
            len(BaseModel.__doc__) > 1, "base_model.py needs a docstring"
        )

    def test_class_docstring(self):
        """Test for the BaseModel class docstring"""
        self.assertIsNot(
            BaseModel.__doc__, None, "BaseModel class needs a docstring"
        )
        self.assertTrue(
            len(BaseModel.__doc__) >= 1, "BaseModel class needs a docstring"
        )

    def test_func_docstrings(self):
        """Test for the presence of docstrings in BaseModel methods"""
        for func in self.base_funcs:
            with self.subTest(function=func):
                self.assertIsNot(
                    func[1].__doc__,
                    None,
                    "{:s} method needs a docstring".format(func[0]),
                )
                self.assertTrue(
                    len(func[1].__doc__) > 1,
                    "{:s} method needs a docstring".format(func[0]),
                )


class TestBaseModel(unittest.TestCase):
    """Tests for the BaseModel class"""

    def test_instantiation(self):
        """Test that instance is correctly created"""
        instance = BaseModel()
        self.assertIs(type(instance), BaseModel)
        instance.name = "Test"
        instance.number = 89
        attributes = {"id": str, "name": str, "number": int}
        for attribute_name, attribute_type in attributes.items():
            with self.subTest(
                attribute_name=attribute_name, attribute_type=attribute_type
            ):
                self.assertIn(attribute_name, instance.__dict__)
                self.assertIs(
                    type(instance.__dict__[attribute_name]),
                    attribute_type,
                )
        self.assertEqual(instance.name, "Test")
        self.assertEqual(instance.number, 89)

    def test_uuid(self):
        """Test that id attribute is a valid uuid4 id"""
        instance1 = BaseModel()
        instance2 = BaseModel()
        for instance in [instance1, instance2]:
            uuid = instance.id
            with self.subTest(uuid=uuid):
                self.assertIs(type(uuid), str)
                self.assertRegex(
                    uuid,
                    "^[0-9a-f]{8}-[0-9a-f]{4}"
                    "-[0-9a-f]{4}-[0-9a-f]{4}"
                    "-[0-9a-f]{12}$",
                )
        self.assertNotEqual(instance1.id, instance2.id)

    def test_to_dict(self):
        """Test that to_dict method correctly converts instance's attributes to
        a jsonifiable dictionary"""
        base_model = BaseModel()
        base_model.name = "Test"
        base_model.a_number = 89
        base_model.a_list_normally_excluded = [89, 90, 91, "abcd"]
        jsonifiable_dict = base_model.to_dict()
        expected_keys = ["id", "name", "a_number", "__class__"]
        self.assertNotIn("a_list_normally_excluded", jsonifiable_dict)
        self.assertCountEqual(jsonifiable_dict.keys(), expected_keys)
        self.assertEqual(jsonifiable_dict["__class__"], "BaseModel")
        self.assertEqual(jsonifiable_dict["name"], "Test")
        self.assertEqual(jsonifiable_dict["a_number"], 89)

    def test_str(self):
        """Test that the str method has the correct output"""
        base_model = BaseModel()
        string = f"[BaseModel] ({base_model.id}) {base_model.__dict__}"
        self.assertEqual(string, str(base_model))

    @mock.patch("models.storage")
    def test_save(self, mock_storage):
        """Test that save method calls `storage.new` and `storage.save`"""
        base_model = BaseModel()
        base_model.save()
        self.assertTrue(mock_storage.new.called)
        self.assertTrue(mock_storage.save.called)

    @mock.patch("models.storage")
    def test_delete(self, mock_storage):
        """Test that delete method calls `storage.delete`"""
        base_model = BaseModel()
        base_model.delete()
        self.assertTrue(mock_storage.delete.called)
