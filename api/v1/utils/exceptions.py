#!/usr/bin/python3
"""User-defined exceptions"""


class FeedInactiveError(Exception):
    """Raised when a feed is permanently inactive"""
    pass


class FeedNotFoundError(Exception):
    """Raised when no feed with a specified id exists"""
    pass
