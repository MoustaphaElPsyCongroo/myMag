#!/usr/bin/python3
"""SQLAlchemy query pagination
    Forked from: https://github.com/wizeline/sqlalchemy-pagination
"""
from models import storage
from sqlalchemy import func


class Page:
    """Page class to hold page data and stats"""

    def __init__(self, items, page, page_size, total):
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        if total is None:
            total = 0
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = (total // page_size) + 1


def paginate(query, count_query, page, page_size):
    """Paginate a query, returning a Page with its stats

        count_query: count version of the same query, issued using SQLAlchemy
        func.count to prevent using subqueries, which is way more performant
        for large tables
    """
    if page <= 0:
        raise AttributeError('page needs to be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size needs to be >= 1')
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    # Get the count of items without issuing a SQL subquery, greatly improving
    # performance for large tables
    total = count_query.scalar()
    return Page(items, page, page_size, total)
