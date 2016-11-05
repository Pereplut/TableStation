#!/usr/bin/python3.4
import serial
import time
from models import LightTimeStamp, TemperatureTimeStamp, Base
from sqlalchemy.orm import  sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///tableStation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class ArduinoSerial():
    def __init__(self, port, baudrate=115200,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE,timeout=20):
        self.ser=serial.Serial(port=port,baudrate=baudrate,bytesize=bytesize,
                               stopbits=stopbits,parity=parity,timeout=timeout)
    def open(self):
        try:
            self.ser.open()
            print(" connection has been enstablished")
        except (serial.SerialException):
            print("serial is closed")
            exit()

    def close(self):
        self.ser.close()

    def send(self, message):
        thisMessage=message.encode('utf-8')
        self.ser.write(thisMessage)

    def recive(self):
        #self.ser.flush()
        return self.ser.readline().decode('utf-8')

serialCom=ArduinoSerial(port='/dev/ttyACM0')

def readFrom_Serial(serial_instance):
    while True:
        #serial_instance.inWaiting()
        serial_instance.send('1')
        #time.sleep(5)
        responce = serial_instance.recive()
        #time.sleep(5)
        #serial_instance.send("stop")
        #responce.strip(' \t\n\r')
        #print("responce is "+responce)
        if responce !='':
            temperature, light=responce.split(',')
            #print("temperature is "+ temperature)
            Temperature= TemperatureTimeStamp(temper_inC_Value=temperature)
            session.add(Temperature)
            Light =  LightTimeStamp(lightValue=light)
            session.add(Light)
            session.commit()

            #print("i wrote something to the DB")
        time.sleep(40)
    serial_instance.close()
readFrom_Serial(serialCom)

