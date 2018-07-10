from datetime import datetime
from RockBLOCKSend import RockBLOCKSend
from apscheduler.schedulers.blocking import BlockingScheduler
from LoggerUtil import LoggerUtil
import time
import ConfigParser
import os
import binascii


GPS_MULTIPLIER = 1000000
PRESSURE_MULTIPLIER = 10
TEMPERATURE_MULTIPLIER = 100


# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

deviceId = int(properties.get('general', 'deviceId'))
modem_interval = int(properties.get('rockBLOCK', 'interval'))
reportDir = properties.get('general', 'reportDir')
modem_name = properties.get('rockBLOCK', 'name')
rockBLOCKDevice = properties.get('rockBLOCK', 'device')

sensorsList = properties.get('rockBLOCK', 'sensors')
logDir = properties.get('general', 'logDir')

gps_name = properties.get('gps', 'name')
bme280_name = properties.get('bme280', 'name')

rfid_name = properties.get('rfid', 'name')
light_name = properties.get('light', 'name')
water_name = properties.get('waterTemp', 'name')

rfidFile = "%s%s" % (reportDir, rfid_name)

logPath = "%s%s.log" % (logDir, modem_name)
#set Scheduler
#scheduler = BlockingScheduler()

#Set Logger
#logger = LoggerUtil(logDir, modem_name)

# TODO: count number of sends
# default values if nothing from file

timePrev = 0
forceSendData = False

def floatToInt(value, multiplier):
    return int(value * multiplier)

#def assembleAndSendData():
while True:
    timeNow = int(time.time())
    dateNow = time.strftime('%Y%m%dT%H%M%S', time.gmtime())
    latConv = []
    lonConv = []
    airTempConv = []
    humidityConv = []
    pressureConv = []
    waterTempConv = []
    lightConv = []
    rfidConv = []

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
                sensorValues = fs.read()

                if sensor == gps_name:
                    print "GPSData %s" % sensorValues
                    gpsData = sensorValues.split(';')
                    latitude = float(gpsData[0])
                    longitude = float(gpsData[1])
                    latConv = '{:08x}'.format(floatToInt(latitude, GPS_MULTIPLIER), 'x')
                    lonConv = '{:08x}'.format(floatToInt(longitude, GPS_MULTIPLIER), 'x')
                elif sensor == bme280_name:
                    print "BME280Data: %s" % sensorValues
                    bme280Data = sensorValues.split(';')
                    airTemperature = float(bme280Data[0])
                    humidity = float(bme280Data[1])
                    pressure = float(bme280Data[2])
                    airTempConv = '{:04x}'.format(floatToInt(airTemperature, TEMPERATURE_MULTIPLIER), 'x')
                    humidityConv = '{:02x}'.format(floatToInt(humidity, 1), 'x')
                    pressureConv = '{:04x}'.format(floatToInt(pressure, PRESSURE_MULTIPLIER), 'x')
                    print "AirTemp: %s" % airTempConv
                elif sensor == light_name:
                    print "LightData: %s" % sensorValues
                    light = sensorValues
                    lightConv = '{:06x}'.format(floatToInt(light, 1), 'x')
                elif sensor == rfid_name:
                    print "RFIDData: %s" % sensorValues
                    rfid = sensorValues
                    rfidConv = '{:02x}'.format(floatToInt(rfid, 1), 'x')
                elif sensor == water_name:
                    print "WaterData: %s" % sensorValues
                    water = float(sensorValues)
                    waterTempConv = '{:04x}'.format(floatToInt(water, TEMPERATURE_MULTIPLIER), 'x')
                else:
                    # unknown sensor
                    logFile.write("%s - unknown sensor: %s\n" % (dateNow, sensor))
		    pass

                fs.close()
                
                
                
            except IOError as (errno, strerror):
                logFile.write("I/O error({0}): {1}".format(errno, strerror))
            except Exception as e:
                logFile.write("Unexpected error: {0}".format(e))
                
        print "Convert device and date"
        deviceIdHex = '{:02x}'.format(deviceId, 'x')
        timeNow = int(time.time())
        dateHex = '{:08x}'.format(timeNow, 'x')
        # unknown sensor value
        # assemble data
        
        print "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceId, rfidConv)
        assembledDataHex = "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceIdHex, rfidConv)
        # send data
        print "Invoke RockBLOCKSend"
        rbs = RockBLOCKSend()
        rbs.sendMessage(message=assembledDataHex, device=rockBLOCKDevice)


#scheduler.add_job(getGPSCoordinates, 'interval', seconds=modem_interval)
#scheduler.start()