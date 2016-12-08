#!/usr/bin/python3.4
import time
import logging
import serial
from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker
from app.models import LightTimeStamp, TemperatureTimeStamp, Base

module_logger = logging.getLogger('app.mon_While')
engine = create_engine('sqlite:///tableStation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class ArduinoSerial():
    def __init__(self, port, baudrate=115200,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE,timeout=5):
        self.ser=serial.Serial(port=port,baudrate=baudrate,bytesize=bytesize,
                               stopbits=stopbits,parity=parity,timeout=timeout)
        self.logger = logging.getLogger('app.mon_While.ArduinoSerial')
        self.logger.info('creating an instance of ArduinoSerial')


    def open(self):
        try:
            self.ser.open()
        except (serial.SerialException):
            print("serial is closed")
            exit()

    def close(self):
        self.ser.close()

    def send(self, message):
        self.logger.info('sent data')
        messageThis=message.encode('utf-8')
        self.ser.write(messageThis)


    def recive(self):
        self.logger.info('receiving...')
        self.ser.flush()
        return self.ser.readline().decode('utf-8')

#serialCom = ArduinoSerial(port='/dev/ttyACM0')

def readFrom_Serial(serial_instance):
    while True:
        #serial_instance.flushInput()
        serial_instance.send("1")
        responce = serial_instance.recive()
        module_logger.info('received data from Arduino, %s')
        responce.strip(' \t\n\r')
        #print (responce)
        if responce != '':
            temperature, light = responce.split(',')
            module_logger.info('sending data to DB')
            Temperature = TemperatureTimeStamp(temper_inC_Value=temperature)
            session.add(Temperature)
            Light = LightTimeStamp(lightValue=light)
            session.add(Light)
            session.commit()
            module_logger.info('commit has been performed')
        time.sleep(60)
    serial_instance.close()

#readFrom_Serial(serialCom)

