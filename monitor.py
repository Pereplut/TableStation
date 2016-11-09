#!/usr/bin/python3.4 python
import time

import serial
from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker

from app.models import LightTimeStamp, TemperatureTimeStamp, Base

engine = create_engine('sqlite:///tableStation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class ArduinoSerial():
    def __init__(self, port, baudrate=9600,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE,timeout=20):
        self.ser=serial.Serial(port=port,baudrate=baudrate,bytesize=bytesize,
                               stopbits=stopbits,parity=parity,timeout=timeout)
    def open(self):
        try:
            self.ser.open()
        except (serial.SerialException):
            print("serial is closed")
            exit()

    def close(self):
        self.ser.close()

    def send(self, message):
        messageThis=message.encode('utf-8')
        self.ser.write(messageThis)

    def recive(self):
        self.ser.flush()
        return self.ser.readline().decode('utf-8')

serialCom=ArduinoSerial(port='COM17')

def readFrom_Serial(serial_instance):
    while True:
        #serial_instance.flushInput()
        serial_instance.send("get Data")
        responce = serial_instance.recive()
        responce.strip(' \t\n\r')
        print (responce)
        if responce !='':
            temperature, light=responce.split(',')
            Temperature= TemperatureTimeStamp(temper_inC_Value=temperature)
            session.add(Temperature)
            Light =  LightTimeStamp(lightValue=light)
            session.add(Light)
            session.commit()
        time.sleep(60)
    serial_instance.close()

readFrom_Serial(serialCom)

