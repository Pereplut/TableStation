#!/usr/bin/python3.4
from models import LightTimeStamp, TemperatureTimeStamp, Base
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///tableStation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)



@app.route('/temp/all',methods=['GET'])
def all_temperature_handler():
    temperatures= session.query(TemperatureTimeStamp).all()
    return jsonify( temperatures = [each.serialize for each in temperatures])

@app.route('/light/all',methods=['GET'])
def all_lightValues_handler():
    lumiens= session.query(LightTimeStamp).all()
    return jsonify( lumien_values = [each.serialize for each in lumiens])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
