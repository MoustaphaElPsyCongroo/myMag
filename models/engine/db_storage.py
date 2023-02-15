#!/usr/bin/python3
"""
Contains the Database storage engine
"""

from decouple import config
import models
from models.article import Article
from models.base_model import Base
from models.feed import Feed
from models.tag import Tag
from models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

classes = {'Article': Article, 'Feed': Feed, 'Tag': Tag, 'User': User}


class DBStorage:
    """Interacts with the MySQL database"""
    __engine = None
    __session = None

    def __init__(self):
        """Instantiate a DBStorage object, initializing the engine"""
        if config('MYSQL_ENV') == 'prod':
            self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                          format(config('MYMAG_MYSQL_USER'),
                                                 config('MYMAG_MYSQL_PWD'),
                                                 config('MYMAG_MYSQL_HOST'),
                                                 config('MYMAG_MYSQL_DB')))

        else:
            self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                          format(config('TEST_MYSQL_USER'),
                                                 config('TEST_MYSQL_PWD'),
                                                 config('TEST_MYSQL_HOST'),
                                                 config('TEST_MYSQL_DB')))
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Returns a dictionary of all objects currently stored in the
        database session, depending on name or not"""
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return new_dict

    def new(self, obj):
        """Adds an object to the current database session"""
        self.__session.add(obj)

    def new_all(self, objs):
        """Add multiple objects to the current database session"""
        self.__session.add_all(objs)

    def save(self):
        """Commits all changes to the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """Deletes an object obj from the current database session"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Creates/Reloads all tables and the session in/to the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def close(self):
        """Closes the database session"""
        self.__session.remove()

    def get(self, cls, id):
        """Retrieves one object"""
        objs = models.storage.all(cls)
        for obj in objs.values():
            if (obj.id == id):
                return obj
        return None

    def count(self, cls=None):
        """Counts the number of objects in storage"""
        if cls is not None:
            objs = models.storage.all(cls)
        else:
            objs = models.storage.all()

        return len(objs.values())
