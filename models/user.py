#!/usr/bin/python3
""" "
Holds the representation of a User
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from models.article import disliked_article, liked_article, read_article
from models.base_model import Base, BaseModel

user_feed = Table(
    "user_feed",
    Base.metadata,
    Column("user_id", String(60), ForeignKey("users.id"), primary_key=True),
    Column("feed_id", String(60), ForeignKey("feeds.id"), primary_key=True),
)


class User(BaseModel, Base):
    """Representation of a User"""

    __tablename__ = "users"
    email = Column(String(128), nullable=False)
    name = Column(String(128), nullable=True)
    profile_pic = Column(String(256), nullable=True)
    last_read_date = Column(DateTime, nullable=True)
    last_scoring_date = Column(DateTime, nullable=True)
    user_feeds = relationship(
        "Feed", secondary=user_feed, back_populates="feed_users"
    )
    liked_articles = relationship(
        "Article",
        secondary=liked_article,
        back_populates="article_liked_by",
        cascade="all, delete",
    )
    disliked_articles = relationship(
        "Article",
        secondary=disliked_article,
        back_populates="article_disliked_by",
        cascade="all, delete",
    )
    read_articles = relationship("Article", secondary=read_article)
    user_tag_like_associations = relationship(
        "TagLikeAssociation", back_populates="user", cascade="all, delete"
    )
    user_tag_dislike_associations = relationship(
        "TagDislikeAssociation", back_populates="user", cascade="all, delete"
    )
    user_article_score_associations = relationship(
        "ArticleUserScoreAssociation",
        back_populates="user",
        cascade="all, delete",
    )

    def __init__(self, *args, **kwargs):
        """Initializes the User model"""
        super().__init__(*args, **kwargs)
