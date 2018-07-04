from datetime import datetime
import time
import ConfigParser
import os
import json
import urllib
import urllib2
import socket
import ssl
import Adafruit_LSM9DS0

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

owner = properties.get('general', 'owner')

lsm9ds0_devId = properties.get('lsm9ds0', 'devId')
lsm9ds0_profile = properties.get('lsm9ds0', 'profile')
lsm9ds0_name = properties.get('lsm9ds0', 'name')
lsm9ds0_interval = int(properties.get('lsm9ds0', 'interval'))
lsm9ds0_reportDir = properties.get('lsm9ds0', 'reportDir')

gpsSectionName = properties.get('lsm9ds0', 'gps')
gps_name = properties.get(gpsSectionName, 'name')
gps_interval = int(properties.get(gpsSectionName, 'interval'))
gps_reportDir = properties.get(gpsSectionName, 'reportDir')

reporterSectionName = properties.get('lsm9ds0', 'reporter')
reporterURL = properties.get(reporterSectionName, 'URL')
reporterTimeout = float(properties.get(reporterSectionName, 'timeout'))

# Create new sensor instance
imu = Adafruit_LSM9DS0.LSM9DS0()

# prepare SSL context
sslCtx = ssl.create_default_context()
sslCtx.check_hostname = False
sslCtx.verify_mode = ssl.CERT_NONE

timePrev = 0
while True:
  timeNow = int(time.time())
  dateNow = time.strftime('%Y-%m-%dT%H:%M:%S.000000000%z', time.gmtime())
   
  if timeNow >= timePrev + lsm9ds0_interval:
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
             sensorLat = float(gpsData[4].split(';')[0])
             sensorLong = float(gpsData[4].split(';')[1])
             if gpsData[4].split(';')[3] == '':
               sensorSpeed = 0.0
             else: 
               sensorSpeed = float(gpsData[4].split(';')[3])
         else:
             gpsValue="TOO_OLD" 
      except Exception as e:
         gpsValue = "NO_DATA"
         print e
      
      # grab data from sensor 
      gyro, mag, accel = imu.read()
       
      sensorValues = [gyro, mag, accel]
      
      gyro_x, gyro_y, gyro_z = gyro
      mag_x, mag_y, mag_z = mag
      accel_x, accel_y, accel_z = accel
      
      sensorValue = "%s; %s; %s; %s; %s; %s; %s; %s; %s" % (gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, accel_x, accel_y, accel_z)
      sensorReportLine = "%s, %s, %s, %s, %s, %s" % (dateNow, owner, lsm9ds0_name, lsm9ds0_devId, sensorValue, gpsValue)  
      
      print sensorReportLine
   
      tmpFile= "%s/%s.tmp" % (lsm9ds0_reportDir,  lsm9ds0_name)
      fs = open(tmpFile, "w") 
      fs.write(sensorReportLine)
      fs.close()
       
      dataFile= "%s/%s" % (lsm9ds0_reportDir,  lsm9ds0_name)
      os.rename(tmpFile, dataFile) 
      timePrev = timeNow
      time.sleep(lsm9ds0_interval)
       
      # send POST to server - one for each reading
      profiles = lsm9ds0_profile.split('_')
      for cnt in range(0,len(profiles)):
         profile = "%s_%s" % (profiles[cnt], "SENSOR")
         sensorValueRaw = sensorValues[cnt]
          
         #gyro
         if cnt == 0:
            x, y, z = sensorValueRaw
            sensorValue = 0
            sensorValueStr = "%s; %s; %s" % (x, y, z)
 
         #mag
         if cnt == 1:
            x, y, z = sensorValueRaw
            sensorValue = 0 
            sensorValueStr = "%s; %s; %s" % (x, y, z)
 
         #accel
         if cnt == 2:
            x, y, z = sensorValueRaw
            sensorValue = 0
            sensorValueStr = "%s; %s; %s" % (x, y, z)
          
         sensorPayload = {
           u"s_owner_id":  owner, 
           u"s_id":        lsm9ds0_devId,
           u"s_profile":   profile,
           u"e_date":      dateNow,
           u"e_long":      sensorLong,
           u"e_lat":       sensorLat,
           u"e_speed":     sensorSpeed,
           u"v_text":      sensorValueStr, 
           u"v_number":    sensorValue 
         } 
         
         print sensorPayload
         #req = urllib2.Request(reporterURL, json.dumps(sensorPayload), headers={'Content-type': 'application/json', 'Accept': 'application/json'})
         #try: 
         #   response = urllib2.urlopen(req, timeout = reporterTimeout, context=sslCtx)
         #except Exception as e:
         #   print "Error: %r, payload: %s" % (e, json.dumps(sensorPayload))


