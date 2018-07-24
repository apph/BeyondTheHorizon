#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0 
import os
from gps import *
from time import *
import time
import threading

from FileUtil import FileUtil
from LoggerUtil import LoggerUtil
import ConfigParser
import time

#adapter specific
import serial
import pynmea2 
 

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')
reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')


name = properties.get('gps', 'name')
interval = int(properties.get('gps', 'interval'))
print name
gps_serialPort = properties.get('gps', 'serialPort')
gps_speed = int(properties.get('gps', 'speed'))
gps_timeout = float(properties.get('gps', 'timeout'))

#set Scheduler
#scheduler = BlockingScheduler()

#Set Logger
logger = LoggerUtil(logDir,name)

gpsd = None #seting the global variable

os.system('clear') #clear the terminal (optional)

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:

        #need confersion to timestamp
        timestamp = gpsd.utc

        latitude = format(gpsd.fix.latitude, '.6f')
        longitude = format(gpsd.fix.longitude, '.6f')
        sensorValue = "%s;%s;%s" % (timestamp,latitude, longitude)
        sensorValueForLogger = "Sat_num: %s ,Lat: %s; Long: %s; Alt: %s; Speed %f; Timestamp %s" % (gpsd.satellites, latitude, longitude, gpsd.fix.altitude, gpsd.fix.speed, timestamp)
        FileUtil.saveToNewFile(reportDir,name,sensorValue)
        logger.log(sensorValueForLogger)


        time.sleep(5) #set to whatever

  except Exception as e:
    print e
    logger.log(e)
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."