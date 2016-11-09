from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import LightTimeStamp, TemperatureTimeStamp, Base

engine = create_engine('sqlite:///tableStation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

from app import models,view
