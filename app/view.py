#!/usr/bin/python3.4
import pygal

from flask import Flask, jsonify,render_template
from app.models import LightTimeStamp, TemperatureTimeStamp, Base
from app import  app,session

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route('/<sensor>')
@app.route('/<sensor>/<int:value>')
def all_json_handler(sensor, value=1):
        values = []
        if sensor == 'temp':
            values = session.query(TemperatureTimeStamp).order_by(TemperatureTimeStamp.id.desc()).limit(value)
        elif sensor == 'light':
            values = session.query(LightTimeStamp).order_by(LightTimeStamp.id.desc()).limit(value)
        return jsonify(values=[each.serialize for each in values])



@app.route('/<sensor>/chart')
def get_sensor_view(sensor):
    tableName = Base
    if sensor == 'temp':
        tableName = TemperatureTimeStamp
        measurables = 'degrees in C'
    elif sensor == 'light':
        tableName = LightTimeStamp
        measurables = 'kinda lumiens'
    values = session.query(tableName).order_by(tableName.id.desc()).limit(288)
    times = [each.getTime for each in values]
    sensorValues = [each.getSensors for each in values]
    title = 'chart'
    bar_chart = pygal.StackedLine(width=1200, height=600,
                                  explicit_size=True, title=title, fill=True)
    bar_chart.x_labels = times
    bar_chart.add(measurables, sensorValues)
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
"""
@app.route('/light/all',methods=['GET'])
def all_lightValues_handler():
    lumiens = session.query(LightTimeStamp).all()
    return jsonify( lumien_values = [each.serialize for each in lumiens])

@app.route('/light/chart')
def get_lights_view():
    lumiens = session.query(LightTimeStamp).order_by(LightTimeStamp.id.desc()).limit(288)
    times = [each.getTime for each in lumiens]
    lightValues = [each.getLight for each in lumiens]
    title = 'lumen chart'
    bar_chart = pygal.StackedLine(width=1200, height=600,
                                  explicit_size=True, title=title, fill=True)
    bar_chart.x_labels = times
    bar_chart.add('lumiens in X', lightValues)
    #html = '''
        <html>
             <head>
                  <title>%s</title>
             </head>
              <body>
                 %s
             </body>
        </html>
        ''' % (title, bar_chart.render())
    return html
"""


@app.route('/charts')
def get_combined_charts():
    graph = pygal.Line()
    graph.title = 'mock title'
    graph.x_labels = ['1', '2', '3', '4', '5']
    graph.add('value 1', [21, 22, 29, 24, 25])
    graph.add('value w', [31, 39, 33, 38, 35])
    graph_data = graph.render_data_uri()
    return render_template("graphing.html", graph_data=graph_data)


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
