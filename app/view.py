#!/usr/bin/python3.4
import pygal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify,render_template
from app.models import LightTimeStamp, TemperatureTimeStamp, Base
from app import  app,session


@app.route('/temp/all',methods=['GET'])
def all_temperature_handler():
    temperatures= session.query(TemperatureTimeStamp).all()
    return jsonify( temperatures = [each.serialize for each in temperatures])

@app.route('/temp/chart')
def get_tempers_view():
    temperatures = session.query(TemperatureTimeStamp).all()
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


@app.route('/charts')
def get_combined_charts():
    graph = pygal.Line()
    graph.title = 'mock title'
    graph.x_labels=['1','2','3','4','5']
    graph.add('value 1',[21,22,23,24,25])
    graph.add('value w',[31,32,33,34,35])
    graph_data= graph.render_data_uri()
    return render_template("graphing.html",graph_data=graph_data)


@app.route('/')
def is_alive():
    respond = ("<html>\n"
               "             <head>\n"
               "                  <title>TitleRoot</title>\n"
               "             </head>\n"
               "              <body>\n"
               "                I'm ok!\n"
               "             </body>\n"
               "        </html>\n"
               "        ")
    return respond


