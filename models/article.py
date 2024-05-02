#!/usr/bin/python3
"""
Holds the representation of an Article
"""
from models.base_model import BaseModel, Base
from datetime import datetime
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
    image = Column(String(2083), nullable=True)
    link = Column(String(2083), nullable=False)
    description = Column(String(2000), default='', nullable=False)
    publish_date = Column(DateTime, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    article_feed = relationship('Feed', back_populates='feed_articles')
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
        cascade='all, delete')
    article_user_score_associations = relationship(
        'ArticleUserScoreAssociation',
        back_populates='article',
        cascade='all, delete'
    )

    def __init__(self, *args, **kwargs):
        """Initializes the Article model"""
        super().__init__(*args, **kwargs)


class ArticleUserScoreAssociation(Base):
    """Association of an Article to a User, with extra data
    (here score and subsection membership)"""
    __tablename__ = 'article_score'
    user_id = Column(ForeignKey('users.id'), primary_key=True)
    article_id = Column(ForeignKey('articles.id'), primary_key=True)
    score_from_tags = Column(Integer, default=0, nullable=False)
    total_score = Column(Integer, default=100, nullable=False)
    last_scoring_date = Column(DateTime, default=datetime.now, nullable=False)
    user = relationship(
        'User', back_populates='user_article_score_associations')
    article = relationship(
        'Article', back_populates='article_user_score_associations')
