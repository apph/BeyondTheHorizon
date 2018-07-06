from datetime import datetime
import time
import ConfigParser
import os
import json
import urllib
import urllib2
from Adafruit_BME280 import *

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')



bme280_name = properties.get('bme280', 'name') 
bme280_interval = int(properties.get('bme280', 'interval')) 
reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')

logFile = "%s%s.log" % (logDir, bme280_name)


# Create new sensor instance
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

timePrlogDirev = 0
while True:
  timeNow = int(time.time())
  dateNow = time.strftime('%Y-%m-%dT%H:%M:%S.000000000%z', time.gmtime())
  
  if timeNow >= timePrev + bme280_interval:
       
      # grab data from sensor     
      sensorValues = [sensor.read_temperature(), sensor.read_humidity(), sensor.read_pressure() / 100]

      sensorValue = "%s;%s;%s" % (sensorValues[0], sensorValues[1], sensorValues[2])
      print sensorValue
      
      #print sensorReportLine
   
      tmpFile= "%s/%s.tmp" % (
      reportDir,  bme280_name)
      fs = open(tmpFile, "w") 
      #fs.write(sensorReportLine)
      fs.write(sensorValue)
      fs.close()
      
      dataFile= "%s/%s" % (
      reportDir,  bme280_name)
      os.rename(tmpFile, dataFile) 
      timePrev = timeNow
      time.sleep(bme280_interval)
