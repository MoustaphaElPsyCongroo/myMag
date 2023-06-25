#!/usr/bin/python3
"""
Holds the representation of a Feed
"""

from models.base_model import BaseModel, Base
from models.user import user_feed
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship


class Feed(BaseModel, Base):
    """Representation of a Feed"""
    __tablename__ = 'feeds'
    name = Column(String(256), nullable=False)
    link = Column(String(2083), nullable=False)
    description = Column(String(1000), nullable=True)
    language = Column(String(15), default='en', nullable=False)
    banner_img = Column(String(2083), nullable=True)
    icon = Column(String(2083), nullable=True)
    etag = Column(String(1024), nullable=True)
    last_modified = Column(String(100), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    average_shares_per_week = Column(Integer, default=0, nullable=False)
    articles_per_week = Column(Integer, default=0, nullable=False)
    feed_users = relationship(
        'User', secondary=user_feed, back_populates='user_feeds'
    )
    feed_articles = relationship('Article', cascade='all, delete')

    def __init__(self, *args, **kwargs):
        """Initializes the Feed model"""
        super().__init__(*args, **kwargs)
