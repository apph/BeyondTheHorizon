from datetime import datetime
import time
import ConfigParser
import os
import json
import urllib
import urllib2
import socket

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

modem_interval = int(properties.get('rockBLOCK', 'interval'))
reportDir = properties.get('rockBLOCK', 'reportDir')
modem_name = properties.get('rockBLOCK', 'name')

sensorsList = properties.get('rockBLOCK', 'sensors')
logDir = properties.get('rockBLOCK', 'logDir')

gps_name = properties.get('gps', 'name')
bme280_name = properties.get('bme280', 'name')

rfid_name = properties.get('rfid', 'name')

logPath = "%s%s.log" % (logDir, modem_name)
rfidFile = "%s%s" % (reportDir, rfid_name)

# TODO: get current timestamp
# TODO: count number of sends

timePrev = 0
forceSendData = False

while True:
    timeNow = int(time.time())
    dateNow = time.strftime('%Y%m%dT%H%M%S', time.gmtime())
    latitude = 0.0
    longitude = 0.0
    airTemperature = 0.0
    humidity = 0
    pressure = 0   

    logFile = open(logPath, 'a')

    rfidMTime = int(os.stat(rfidFile).st_mtime)
  
    # change of swimmer, send data
    if rfidMTime >= timePrev:
        forceSendData = True

    if (timeNow >= timePrev + modem_interval) or forceSendData:
        forceSendData = False
        sensors = sensorsList.split(';')
        timePrev = timeNow

        print "Sensors: %s" % sensors
        for cnt in range(0, len(sensors)):
            try: 
                sensor = sensors[cnt]
                sensorDataFile = "%s%s" % (reportDir, sensor)
                fs = open(sensorDataFile, "r")

                if sensor == gps_name:
                    gpsValue=fs.read()
                    print "GPSData %s" % gpsValue
                    gpsData = gpsValue.split(';')
                    latitude = float(gpsData[0])
                    longitude = float(gpsData[1])
                elif sensor == bme280_name:
                    bme280Values = fs.read()
                    print "BME280Data: %s" % bme280Values
                    bme280Data = bme280Values.split(';')
                    airTemperature = bme280Data[0]
                    humidity = bme280Data[1]
                    pressure = bme280Data[2]
                else:
		    pass

                fs.close()
                # unknown sensor value
                # assemble data
                # send data
            except IOError as (errno, strerror):
                logFile.write("I/O error({0}): {1}".format(errno, strerror))
            except:
                logFile.write("Unexpected erro: ", sys.exc_info()[0])


        print "Data: %s, %s, %s, %s, %s, %s" % (dateNow, latitude, longitude, airTemperature, humidity, pressure)

      


