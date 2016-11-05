#!/usr/bin/python3.4 python
import pygal
from pygal.style import DarkSolarizedStyle
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

@app.route('/temp/chart')
def get_lights_view():
    temperatures = session.query(LightTimeStamp).all()
    times= [each.getTime for each in temperatures ]
    tempValues=[each.getTemp for each in temperatures ]
    title = 'temperature chart'
    bar_chart = pygal.StackedLine(width=1200, height=600,
                explicit_size=True, title=title, fill=True)
    bar_chart.x_labels = times
    bar_chart.add('degrees in C', tempValues)
    html = """
        <html>
             <head>
                  <title>%s</title>
             </head>
              <body>
                 %s
             </body>
        </html>
        """ % (title, bar_chart.render())
    return html

@app.route('/light/all',methods=['GET'])
def all_lightValues_handler():
    lumiens= session.query(LightTimeStamp).all()
    return jsonify( lumien_values = [each.serialize for each in lumiens])

@app.route('/light/chart')
def get_lights_view():
    lumiens = session.query(LightTimeStamp).all()
    times= [each.getTime for each in lumiens]
    lightValues=[each.getLight for each in lumiens]
    title = 'lumen chart'
    bar_chart = pygal.StackedLine(width=1200, height=600,
                explicit_size=True, title=title, fill=True)
    bar_chart.x_labels = times
    bar_chart.add('lumiens in X', lightValues)
    html = """
        <html>
             <head>
                  <title>%s</title>
             </head>
              <body>
                 %s
             </body>
        </html>
        """ % (title, bar_chart.render())
    return html

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)