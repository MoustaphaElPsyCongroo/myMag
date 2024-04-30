#!/usr/bin/python3
"""General API Blueprint"""

from flask import Blueprint

app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

from api.v1.auth import *
from api.v1.views.feed_articles import *
from api.v1.views.feeds import *
from api.v1.views.index import *
from api.v1.views.user_articles import *
from api.v1.views.user_feeds import *
from api.v1.views.user_tag_articles import *
from api.v1.views.user_tags import *
from api.v1.views.users import *
