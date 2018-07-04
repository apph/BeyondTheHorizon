from datetime import datetime
import time
import ConfigParser
import os
import json
import urllib
import urllib2
import socket
import ssl
from Adafruit_BME280 import *

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

owner = properties.get('general', 'owner')

bme280_devId = properties.get('bme280', 'devId')
bme280_profile = properties.get('bme280', 'profile')
bme280_name = properties.get('bme280', 'name')
bme280_interval = int(properties.get('bme280', 'interval'))
bme280_reportDir = properties.get('bme280', 'reportDir')

gpsSectionName = properties.get('bme280', 'gps')
gps_name = properties.get(gpsSectionName, 'name')
gps_interval = int(properties.get(gpsSectionName, 'interval'))
gps_reportDir = properties.get(gpsSectionName, 'reportDir')

reporterSectionName = properties.get('bme280', 'reporter')
reporterURL = properties.get(reporterSectionName, 'URL')
reporterTimeout = float(properties.get(reporterSectionName, 'timeout'))

# Create new sensor instance
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

# prepare SSL context
sslCtx = ssl.create_default_context()
sslCtx.check_hostname = False
sslCtx.verify_mode = ssl.CERT_NONE

timePrev = 0
while True:
  timeNow = int(time.time())
  dateNow = time.strftime('%Y-%m-%dT%H:%M:%S.000000000%z', time.gmtime())
  
  if timeNow >= timePrev + bme280_interval:
       
      gpsFile="%s/%s" % (gps_reportDir,  gps_name)
      gpsValue = "UNKNOWN"
      sensorLong = 0.0 
      sensorLat = 0.0
      try:
         gpsMtime=int(os.stat(gpsFile).st_mtime)
         if gpsMtime >= timeNow - gps_interval: 
             fs = open(gpsFile,"r")
             gpsValue=fs.read()
             fs.close()
             gpsData = gpsValue.split(',')
             sensorLong = gpsData[4].split(';')[1]
             sensorLat = gpsData[4].split(';')[2]
         else:
             gpsValue="TOO_OLD" 
      except Exception as e:
         gpsValue = "NO_DATA"
         print e

      # grab data from sensor     
      sensorValues = [sensor.read_temperature(), sensor.read_humidity(), sensor.read_pressure() / 100]

      sensorValue = "%s; %s; %s" % (sensorValues[0], sensorValues[1], sensorValues[2])
      sensorReportLine = "%s, %s, %s, %s, %s, %s" % (dateNow, owner, bme280_name, bme280_devId, sensorValue, gpsValue)  
      
      print sensorReportLine
   
      tmpFile= "%s/%s.tmp" % (bme280_reportDir,  bme280_name)
      fs = open(tmpFile, "w") 
      fs.write(sensorReportLine)
      fs.close()
      
      dataFile= "%s/%s" % (bme280_reportDir,  bme280_name)
      os.rename(tmpFile, dataFile) 
      timePrev = timeNow
      time.sleep(bme280_interval)
      

      # send POST to server - one for each reading
      profiles = bme280_profile.split('_')
      for cnt in range(0,len(profiles)):
         profile = "%s_%s" % (profiles[cnt], "SENSOR")
         sensorValueRaw = sensorValues[cnt]

         #convert string to number
         sensorValue = float(sensorValueRaw)
         sensorValueStr = str(sensorValueRaw)

         sensorPayload = {
           u"s_id":        bme280_devId,
           u"s_profile":   profile,
           u"e_date":      dateNow,
           u"e_long":      sensorLong,
           u"e_lat":       sensorLat,
           u"v_text":      sensorValueStr,
           u"v_number":    sensorValue 
         } 

         print sensorPayload
         req = urllib2.Request(reporterURL, json.dumps(sensorPayload), headers={'Content-type': 'application/json', 'Accept': 'application/json'})
         try: 
            response = urllib2.urlopen(req, timeout = reporterTimeout, context=sslCtx)
         except Exception as e:
            print "Error: %r, payload: %s" % (e, json.dumps(sensorPayload))
