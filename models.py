#!/usr/bin/python3.4 python
# -*- coding: utf-8 -*-
from sqlalchemy import Column,Integer,String, DateTime, DDL, event
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base
import datetime

from sqlalchemy import create_engine

Base = declarative_base()

class LightTimeStamp(Base):
    __tablename__ = 'photosell'
    id = Column(Integer,primary_key=True,autoincrement=True)
    lightValue = Column(Integer)
    timeStamp = Column(DateTime, default=datetime.datetime.now)

    @property
    def serialize(self):
        return {
            'lightValue':self.lightValue,
            'timeStamp':self.timeStamp,
            'id':self.id
        }


class TemperatureTimeStamp(Base):
    __tablename__ = 'thermometer'
    id = Column(Integer,primary_key=True,autoincrement=True)
    temper_inC_Value = Column(Integer)
    #timeStamp = Column(String(32))
    timeStamp =Column(DateTime, default=datetime.datetime.now)

    @property
    def serialize(self):
        return {
            'temper_inC_Value': self.temper_inC_Value,
            'timeStamp': self.timeStamp,
            'id': self.id
        }

engine = create_engine('sqlite:///tableStation.db')
Base.metadata.create_all(engine)
