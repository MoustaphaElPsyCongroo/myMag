#!/usr/bin/python3
"""
Holds the representation of a Tag
"""

from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship


class Tag(BaseModel, Base):
    """Representation of a Tag"""
    __tablename__ = 'tags'
    name = Column(String(128), nullable=False)
    type = Column(String(10), nullable=False)
    tag_article_associations = relationship(
        'TagArticleAssociation',
        back_populates='tag')
    tag_like_associations = relationship(
        'TagLikeAssociation',
        back_populates='tag'
    )
    tag_dislike_associations = relationship(
        'TagDislikeAssociation',
        back_populates='tag'
    )

    def __init__(self, *args, **kwargs):
        """Initializes the Tag model"""
        super().__init__(*args, **kwargs)


class TagArticleAssociation(Base):
    """Association of a Tag to an Article, with extra data (here confidence)"""
    __tablename__ = 'article_tag'
    tag_id = Column(ForeignKey('tags.id'), primary_key=True)
    article_id = Column(ForeignKey('articles.id'), primary_key=True)
    confidence = Column(Float, default=0)
    tag = relationship(
        'Tag', back_populates='tag_article_associations')
    article = relationship(
        'Article', back_populates='article_tag_associations')


class TagLikeAssociation(Base):
    """Association of a Tag to a User, with extra data
    (here like count from the user and like count from the article)"""
    __tablename__ = 'tag_like'
    tag_id = Column(ForeignKey('tags.id'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)
    like_count_from_user = Column(Integer, default=0, nullable=False)
    like_count_from_article = Column(Integer, default=0, nullable=False)
    tag = relationship('Tag', back_populates='tag_like_associations')
    user = relationship(
        'User', back_populates='user_tag_like_associations')


class TagDislikeAssociation(Base):
    """Association of a Tag to a User, with extra data
    (here dislike count from the user and dislike count from the article)"""
    __tablename__ = 'tag_dislike'
    tag_id = Column(ForeignKey('tags.id'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)
    dislike_count_from_user = Column(Integer, default=0, nullable=False)
    dislike_count_from_article = Column(Integer, default=0, nullable=False)
    tag = relationship('Tag', back_populates='tag_dislike_associations')
    user = relationship(
        'User', back_populates='user_tag_dislike_associations')
