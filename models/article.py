#!/usr/bin/python3
"""
Holds the representation of an Article
"""

from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

liked_article = Table('liked_article', Base.metadata,
                      Column('user_id', String(60),
                             ForeignKey('users.id'), primary_key=True),
                      Column('article_id', String(60),
                             ForeignKey('articles.id'), primary_key=True))

disliked_article = Table('disliked_article', Base.metadata,
                         Column('user_id', String(60),
                                ForeignKey('users.id'), primary_key=True),
                         Column('article_id', String(60),
                                ForeignKey('articles.id'), primary_key=True))

read_article = Table('read_article', Base.metadata,
                     Column('user_id', String(60),
                            ForeignKey('users.id'), primary_key=True),
                     Column('article_id', String(60),
                            ForeignKey('articles.id'), primary_key=True))


class Article(BaseModel, Base):
    """Representation of an Article"""
    __tablename__ = 'articles'
    feed_id = Column(String(60), ForeignKey('feeds.id'), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(String(2000), default='', nullable=False)
    publish_date = Column(DateTime, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    article_liked_by = relationship(
        'User', secondary=liked_article, back_populates='liked_articles')
    article_disliked_by = relationship(
        'User', secondary=disliked_article, back_populates='disliked_articles')
    article_read_by = relationship(
        'User', secondary=read_article, back_populates='read_articles'
    )
    article_tag_associations = relationship(
        'TagArticleAssociation',
        back_populates='article',
        cascade='delete')

    def __init__(self, *args, **kwargs):
        """Initializes the Article model"""
        super().__init__(*args, **kwargs)
