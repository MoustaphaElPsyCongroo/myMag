#!/usr/bin/python3
"""Extends unittest's startTestRun to let integration tests that use a fresh
version of the real database to fail if on the production database."""

import unittest

from decouple import config

OLD_TEST_RUN = unittest.result.TestResult.startTestRun
STOP = unittest.result.TestResult.stop  # stops all tests


def startTestRun(self):
    """Runs once before all tests"""
    if config("MYSQL_ENV") == "test":
        print(
            """You're on the prod database.\nEdit .env to test on the right database"""
        )
        STOP(self)

    # just in case future versions do something in this method
    # we'll call the existing method
    OLD_TEST_RUN(self)


setattr(unittest.TestResult, "startTestRun", startTestRun)
