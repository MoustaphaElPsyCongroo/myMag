#!/usr/bin/python3
"""Cronjob for feed stat extraction"""


def extract_weekly_stats():
    """Calculate and save weekly stats for feeds, such as:
    - article shares per week
    - articles per week
    Executes each day.
    """

    # TODO: When a feed is younger than a week, take article published this day
    # and multiply * 5 working days to get an estimate for this week. I fixed
    # the case where every user unfollowed the feed, which will cease its
    # updates: now when the first user follows a feed (feed_users count goes
    # from 0 to 1), immediately update it.

    # Also if a feed never published  any article for the whole day, bump its
    # number to 1. So that if it's a dormant source, it will only be checked
    # once per day instead of every ten minutes.
