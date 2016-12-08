#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from sqlalchemy import Column,Integer,String, DateTime, DDL, event
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine

Base = declarative_base()
class DHT11Table(Base):
    __tablename__ = 'dht11'
    id = Column(Integer,primary_key=True,autoincrement=True)
    temperature = Column(String)
    humidity = Column(String)
    timeStamp = Column(DateTime,default=datetime.datetime.now())

    @property
    def getHumidity(self):
        return self.humidity

    @property
    def getTemperature(self):
        return self.temperature

    @property
    def getHumidity(self):
        return self.timeStamp

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
    @property
    def getSensors(self):
        return self.lightValue
    @property
    def getTime(self):
        return self.id    # TODO make wrapper for timeStamp value and remove the ID from this row

class TemperatureTimeStamp(Base):
    __tablename__ = 'thermometer'
    id = Column(Integer,primary_key=True,autoincrement=True)
    temper_inC_Value = Column(Integer)
    timeStamp =Column(DateTime, default=datetime.datetime.now)

    @property
    def serialize(self):
        return {
            'temper_inC_Value': self.temper_inC_Value,
            'timeStamp': self.timeStamp,
            'id': self.id
        }

    @property
    def getSensors(self):
        return self.temper_inC_Value

    @property
    def getTime(self):
        return self.id  # TODO make wrapper for timeStamp value and remove the ID from this row

engine = create_engine('sqlite:///tableStation.db')
Base.metadata.create_all(engine)
