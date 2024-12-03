#!/usr/bin/env python3
"""Tests for custom exceptions"""

import unittest

import pycodestyle

from api.v1.utils.exceptions import FeedInactiveError, FeedNotFoundError


class TestExceptionsDocs(unittest.TestCase):
    """Tests to check the documentation and style of custom exceptions"""

    def test_pep8_conformance(self):
        """Test that api/v1/utils/exceptions.py conforms to PEP8."""
        for path in [
            "api/v1/utils/exceptions.py",
            "tests/test_api/test_v1/test_utils/test_exceptions.py",
        ]:
            with self.subTest(path=path):
                errors = pycodestyle.Checker(path).check_all()
                self.assertEqual(errors, 0)

    def test_module_docstring(self):
        """Test for the existence of exception module docstring"""
        import api.v1.utils.exceptions as exceptions

        self.assertIsNot(
            exceptions.__doc__,
            None,
            "api/v1/utils/exceptions.py needs a docstring",
        )
        self.assertTrue(
            len(exceptions.__doc__) > 1,
            "api/v1/utils/exceptions.py needs a docstring",
        )

    def test_classes_docstrings(self):
        """Test the Exception classes docstrings"""
        self.assertIsNot(
            FeedInactiveError.__doc__,
            None,
            "FeedNotFoundError class needs a docstring",
        )
        self.assertTrue(
            len(FeedNotFoundError.__doc__) >= 1,
            "FeedNotFoundError class needs a docstring",
        )

        self.assertIsNot(
            FeedNotFoundError.__doc__,
            None,
            "FeedNotFoundError class needs a docstring",
        )
        self.assertTrue(
            len(FeedNotFoundError.__doc__) >= 1,
            "FeedNotFoundError class needs a docstring",
        )
