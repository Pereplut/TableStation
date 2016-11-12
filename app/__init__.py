from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import LightTimeStamp, TemperatureTimeStamp, Base

app = Flask(__name__)
app.config.from_object('config')
#db=create_engine(app)
db = create_engine('sqlite:///tableStation.db')
Base.metadata.bind = db
DBSession = sessionmaker(bind=db)
session = DBSession()


from app import models,view
