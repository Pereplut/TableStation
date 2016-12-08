#!/usr/bin/python3.4
import logging
import monitor
# create logger with 'spam_application'
logger = logging.getLogger('Arduino_app')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('serial_monitor.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info('launching serial Monitoring')
monitoring = monitor.ArduinoSerial(port='/dev/ttyACM0')
#serialCom = monitoring(port='/dev/ttyACM0')
logger.info('launched an instance of serial Monitoring')
logger.info('starting monitoring loop')
#monitor.readFrom_Serial(monitoring)
monitor.read_dht11_serial(monitoring)
logger.info('ending monitoring loop')
