#!/usr/bin/python3
"""
The common skeleton of our Database models
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

import models

Base = declarative_base()


class BaseModel:
    """Our baseline Database model from which all models will be derived"""

    id = Column(String(60), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        """Base model initialization"""
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    setattr(self, key, value)

            if kwargs.get("id", None) is None:
                self.id = str(uuid.uuid4())
        else:
            self.id = str(uuid.uuid4())

    def __str__(self):
        """Basemodel's string representation"""
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"

    def save(self):
        """Creates and saves current instance in storage"""
        # self.updated_at = datetime.now()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Returns a dictionary containing all key/values of the instance
        Excludes _sa_instance_state and all list instances (sqlalchemy
        relationship objects) to make it jsonifyable
        """
        new_dict = {
            key: val
            for key, val in self.__dict__.items()
            if key != "_sa_instance_state" and not isinstance(val, list)
        }
        new_dict["__class__"] = self.__class__.__name__
        return new_dict

    def delete(self):
        """Delete the current instance from the storage"""
        models.storage.delete(self)
