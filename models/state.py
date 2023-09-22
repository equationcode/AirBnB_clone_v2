#!/usr/bin/python3
"""Defines the State class."""
import models
from os import getenv
from models.base_model import Base
from models.base_model import BaseModel
from models.city import City
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship



class State(BaseModel, Base):

    __tablename__ = 'States'
    name = Column(String(128), nullable=False)
    cities = relationship('City', backref='state',
                              cascade='all, delete, delete-orphan')
