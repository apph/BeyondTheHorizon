from datetime import datetime
import time
import ConfigParser
import os

#adapter specific
import serial
import pynmea2


# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')
reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')


gps_name = properties.get('gps', 'name')
gps_interval = int(properties.get('gps', 'interval'))

gps_serialPort = properties.get('gps', 'serialPort')
gps_speed = int(properties.get('gps', 'speed'))
gps_timeout = float(properties.get('gps', 'timeout'))


logFile = "%s%s.log" % (logDir, gps_name)


# Create new sensor instance
print gps_serialPort
serialStream = serial.Serial(gps_serialPort, gps_speed, timeout=gps_timeout)

print "Stream: %s" % serialStream

logFile = open(logFile, 'a')

speed = 0.0
timePrev = 0
while True:
  timeNow = int(time.time())
  dateNow = time.strftime('%Y-%m-%dT%H:%M:%S.000000000%z', time.gmtime())
  logDate = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())

  if timeNow >= timePrev + gps_interval:
      
      gpsFile="%s/%s" % (reportDir,  gps_name)

      gpsValue = "UNKNOWN"

      try:
         gpsMtime=int(os.stat(gpsFile).st_mtime)
      
         if gpsMtime >= timeNow - gps_interval:
             fs = open(gpsFile,"r")
             gpsValue=fs.read()
             fs.close()
         else:
             gpsValue="TOO_OLD" 
      except:
         print "Exception"
         gpsValue = "NO_DATA"
	 pass

      # grab data from sensor     
      sentence = serialStream.readline()
      print sentence
      if sentence.find('VTG') > 0:
         # $GPVTG,,T,,M,1.751,N,3.243,K,A*27
         VTGdata = sentence.split(',')
         #//print VTGdata
         if VTGdata[7] == '':
           speed = 0.0
         else:
           speed = float(VTGdata[7])
      elif sentence.find('GGA') > 0:
         try:
             gpsData = pynmea2.parse(sentence)
             logFile.write("%s, GPSData: %s\n" % (logDate, gpsData))
             print "GPSData: %s " % (gpsData)
         except Exception as e:
             logFile.write("%s, pynmea2.parse exception %s\n" % (logDate, e))
             print e

         sensorValue = "%s;%s;%s;%f" % (gpsData.latitude, gpsData.longitude, gpsData.altitude, speed)

          
         #print sensorReportLine
          
         tmpFile= "%s/%s.tmp" % (reportDir,  gps_name)
         fs = open(tmpFile, "w") 

         fs.write(sensorValue)
         logFile.write("%s, Sensor data: %s\n" % (logDate, sensorValue))

         fs.close()
         
         dataFile= "%s/%s" % (reportDir,  gps_name)
         os.rename(tmpFile, dataFile) 
         timePrev = timeNow
         time.sleep(gps_interval)
         #logFile.close()



