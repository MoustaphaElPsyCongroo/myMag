#!/usr/bin/python3
"""Cronjob for feed stat extraction"""


def extract_weekly_stats():
    """Calculate and save weekly stats for feeds, such as:
    - article shares per week
    - articles per week
    Executes each day.
    """
