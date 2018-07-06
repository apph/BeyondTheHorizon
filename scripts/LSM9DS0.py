from datetime import datetime
import time
import ConfigParser
import os
import json
import urllib
import urllib2
import Adafruit_LSM9DS0

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

reportDir = properties.get('general', 'reportDir')


lsm9ds0_name = properties.get('lsm9ds0', 'name')
lsm9ds0_interval = int(properties.get('lsm9ds0', 'interval'))


logDir = properties.get('general', 'logDir')
logFile = "%s%s.log" % (logDir, lsm9s0_name)

# Create new sensor instance
imu = Adafruit_LSM9DS0.LSM9DS0()

logFile = open(logFile, 'a')

timePrev = 0
while True:
  timeNow = int(time.time())
  dateNow = time.strftime('%Y-%m-%dT%H:%M:%S.000000000%z', time.gmtime())
  logDate = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
   
  if timeNow >= timePrev + lsm9ds0_interval:
      # grab data from sensor 
      gyro, mag, accel = imu.read()
       
      sensorValues = [gyro, mag, accel]
      
      gyro_x, gyro_y, gyro_z = gyro
      mag_x, mag_y, mag_z = mag
      accel_x, accel_y, accel_z = accel
      
      sensorValue = "%s; %s; %s; %s; %s; %s; %s; %s; %s" % (gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, accel_x, accel_y, accel_z)
      logFile.write("%s, Gyro: %s %s %s, Mag: %s %s %s, Accel: %s %s %s\n" % (logDate, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, accel_x, accel_y, accel_z))
      print sensorValue
   
      tmpFile= "%s/%s.tmp" % (reportDir,  lsm9ds0_name)
      fs = open(tmpFile, "w") 
      fs.write(sensorReportLine)
      fs.close()
       
      dataFile= "%s/%s" % (reportDir,  lsm9ds0_name)
      os.rename(tmpFile, dataFile) 
      timePrev = timeNow
      time.sleep(lsm9ds0_interval)
      logFile.close()
       

