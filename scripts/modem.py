from datetime import datetime
from RockBLOCKSend import RockBLOCKSend
from rockBlock import rockBlockException
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

def convertToHex(value, multiplier, precision):
    result = floatToInt(value, multiplier)
    return '{:0{precision}x}'.format(result, 'x', precision=precision)


#def assembleAndSendData():
while True:
    timeNow = int(time.time())
    dateNow = time.strftime('%Y%m%dT%H%M%S', time.gmtime())
    # init to default values if nothing comes from the sensor files
    latConv = convertToHex(0.0, GPS_MULTIPLIER, 8)
    lonConv = convertToHex(0.0, GPS_MULTIPLIER, 8)
    airTempConv = convertToHex(0.0, TEMPERATURE_MULTIPLIER, 4)
    humidityConv = convertToHex(0, 1, 2)
    pressureConv = convertToHex(0.0, PRESSURE_MULTIPLIER, 4)
    waterTempConv = convertToHex(0.0, TEMPERATURE_MULTIPLIER, 4)
    lightConv = convertToHex(0, 1, 6)
    rfidConv = convertToHex(0, 1, 2)
    
    # pre-initialize array with 8 elements
    sensorRawData = [None] * 8

    logFile = open(logPath, 'a')

    rfidMTime = int(os.stat(rfidFile).st_mtime)
  
    # change of swimmer, send data
    if rfidMTime >= timePrev:
        forceSendData = True

    if (timeNow >= timePrev + modem_interval) or forceSendData:
        forceSendData = False
        sensors = sensorsList.split(';')
        timePrev = timeNow

        #print "Sensors: %s" % sensors
        for cnt in range(0, len(sensors)):
            try: 
                sensor = sensors[cnt]
                sensorDataFile = "%s%s" % (reportDir, sensor)
                fs = open(sensorDataFile, "r")
                sensorValues = fs.read()

                if sensor == gps_name:
                    #print "GPSData %s" % sensorValues
                    gpsData = sensorValues.split(';')
                    latitude = float(gpsData[0])
                    longitude = float(gpsData[1])
                    latConv = convertToHex(latitude, GPS_MULTIPLIER, 8)
                    lonConv = convertToHex(longitude, GPS_MULTIPLIER, 8)
                    sensorRawData[0] = latitude
                    sensorRawData[1] = longitude
                elif sensor == bme280_name:
                    #print "BME280Data: %s" % sensorValues
                    bme280Data = sensorValues.split(';')
                    airTemperature = float(bme280Data[0])
                    humidity = float(bme280Data[1])
                    pressure = float(bme280Data[2])
                    airTempConv = convertToHex(airTemperature, TEMPERATURE_MULTIPLIER, 4)
                    humidityConv = convertToHex(humidity, 1, 2)
                    pressureConv = convertToHex(pressure, PRESSURE_MULTIPLIER, 4)
                    sensorRawData[2] = airTemperature
                    sensorRawData[3] = humidity
                    sensorRawData[4] = pressure
                elif sensor == light_name:
                    #print "LightData: %s" % sensorValues
                    light = sensorValues
                    lightConv = convertToHex(light, 1, 6)
                    sensorRawData[5] = light
                elif sensor == rfid_name:
                    #print "RFIDData: %s" % sensorValues
                    rfid = sensorValues
                    rfidConv = convertToHex(rfid, 1, 2)
                    sensorRawData[6] = rfid
                elif sensor == water_name:
                    #print "WaterData: %s" % sensorValues
                    water = float(sensorValues)
                    waterTempConv = convertToHex(water, TEMPERATURE_MULTIPLIER, 4)
                    sensorRawData[7] = water
                else:
                    # unknown sensor
                    logFile.write("%s - unknown sensor: %s\n" % (dateNow, sensor))
		    pass

                fs.close()    
                
            except IOError as (errno, strerror):
                logFile.write("I/O error({0}): {1}\n".format(errno, strerror))
            except Exception as e:
                logFile.write("Unexpected error: {0}\n".format(e))
                
        deviceIdHex = convertToHex(deviceId, 1, 2)
        timeNow = int(time.time())
        dateHex = convertToHex(timeNow, 1, 8)
        # unknown sensor value
        print "Raw sensor data: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensorRawData[0], sensorRawData[1], timeNow, sensorRawData[5], sensorRawData[2],
                                                                sensorRawData[3], sensorRawData[4], sensorRawData[7], deviceId, sensorRawData[6])
        logFile.write("Raw sensor data: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (sensorRawData[0], sensorRawData[1], timeNow, sensorRawData[5], sensorRawData[2],
                                                                sensorRawData[3], sensorRawData[4], sensorRawData[7], deviceId, sensorRawData[6]))
        # assemble data
        
        print "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceId, rfidConv)
        assembledDataHex = "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceIdHex, rfidConv)
        # send data
        try:
            rbs = RockBLOCKSend()
            rbs.sendMessage(assembledDataHex, rockBLOCKDevice)
        except rockBlockException as e:
            print "rockBlockException"
            logFile.write("RockBLOCK Exception: %s\n" % str(e))


#scheduler.add_job(getGPSCoordinates, 'interval', seconds=modem_interval)
#scheduler.start()