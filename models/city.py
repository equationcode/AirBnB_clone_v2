#!/usr/bin/python3
""" City Module for HBNB project """
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class City(BaseModel, Base):

    __tablename__ = 'City'

    name = Column(String(128), nullable=False)
    state_id = Column(String(60), nullable=False, foreign_key='state.id')
    """ The city class, contains state ID and name """
    state_id = ""
    name = ""
