from datetime import datetime
from rockBlock import rockBlockException
from rockBlock import rockBlockProtocol
from apscheduler.schedulers.blocking import BlockingScheduler
from LoggerUtil import LoggerUtil
import time
import ConfigParser
import os
import binascii
import rockBlock


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
maxRockMessages = properties.get('rockBLOCK', 'maxMessages')
rockPollInterval = int(properties.get('rockBLOCK', 'pollInterval'))
minInterval = int(properties.get('rockBLOCK', 'minInterval'))
maxInterval = int(properties.get('rockBLOCK', 'maxInterval'))

sensorsList = properties.get('rockBLOCK', 'sensors')
logDir = properties.get('general', 'logDir')

gps_name = properties.get('gps', 'name')
bme280_name = properties.get('bme280', 'name')

rfid_name = properties.get('rfid', 'name')
light_name = properties.get('light', 'name')
water_name = properties.get('waterTemp', 'name')

rfidFile = "%s%s" % (reportDir, rfid_name)

#set Scheduler
#scheduler = BlockingScheduler()

class RockBlockWrapper(rockBlockProtocol):
    logger = LoggerUtil(logDir, modem_name)
    messagesCount = 0

    def sendMessage(self, message, device):
        rb = rockBlock.rockBlock(device, self)
        rb.sendMessage(message)      
	rb.close()
	
    def requestMessages(self, device):
        rb = rockBlock.rockBlock(device, self)
        rb.messageCheck()      
	rb.close()
        
    def rockBlockTxStarted(self):
        self.logger.log("rockBlockTxStarted")
        
    def rockBlockTxFailed(self):
        self.logger.log("rockBlockTxFailed")
        
    def rockBlockTxSuccess(self,momsn):
        self.logger.log("rockBlockTxSuccess " + str(momsn))
        
    def rockBlockRxReceived(self, mtmsn, data):
        self.logger.log("rockBlockRxRecevied, message number %s, data %s " % (str(mtmsn), data))
        if (str(data).startswith("F")):
            newInterval = int(data[1:])
            if (newInterval >= minInterval and newInterval <= maxInterval):
                global modem_interval
                modem_interval = newInterval
                self.logger.log("RockBLOCK - rockBlockRxRecevied - new interval set to %s" % modem_interval)
        else:
            self.logger.log("RockBLOCK - rockBlockRxRecevied - Unknown command %s" % str(data))
            
        
    def rockBlockRxMessageQueue(self, count):
        self.logger.log("rockBlockRxMessageQueue " + str(count))
        messagesCount = count
        
    def floatToInt(self, value, multiplier):
        return int(value * multiplier)

    def convertToHex(self, value, multiplier, precision):
        result = self.floatToInt(value, multiplier)
        return '{:0{precision}x}'.format(result, 'x', precision=precision)
        
    def assembleAndSendData(self):
        timePrev = 0
        sentRockMessages = 0
        forceSendData = False

        while True:
            timeNow = int(time.time())
            dateNow = time.strftime('%Y%m%dT%H%M%S', time.gmtime())
            # init to default values if nothing comes from the sensor files
            latConv = self.convertToHex(0.0, GPS_MULTIPLIER, 8)
            lonConv = self.convertToHex(0.0, GPS_MULTIPLIER, 8)
            airTempConv = self.convertToHex(0.0, TEMPERATURE_MULTIPLIER, 4)
            humidityConv = self.convertToHex(0, 1, 2)
            pressureConv = self.convertToHex(0.0, PRESSURE_MULTIPLIER, 4)
            waterTempConv = self.convertToHex(0.0, TEMPERATURE_MULTIPLIER, 4)
            lightConv = self.convertToHex(0, 1, 6)
            # no swimmer? -> FF
            rfidConv = self.convertToHex(255, 1, 2)
            
            # pre-initialize array with 8 elements
            sensorRawData = [None] * 8

            # check if there was RFID file modification. If yes, it means swimmer has changed
            rfidMTime = 0
            if os.path.isfile(rfidFile):
                rfidMTime = int(os.stat(rfidFile).st_mtime)
            
            # if we have reached maximum number of messages stop sending (will be too expensive)
            if sentRockMessages > maxRockMessages:
                break
          
            # change of swimmer, send data
            if rfidMTime >= timePrev:
                forceSendData = True

            # do we need to poll RockBLOCK for configuration updates
            if (timeNow >= timePrev + rockPollInterval):
                if self.messagesCount > 0:
                    print "Invoke RequestMessages"
                    try:
                        self.requestMessages(rockBLOCKDevice)
                    except rockBlockException as e:
                        print "self.requestMessages(rockBlockException)"
                        self.logger.log("RockBLOCK - requestMessages, exception: %s" % str(e))

            if (timeNow >= timePrev + modem_interval) or forceSendData:
                print "Modem interval: %s" % modem_interval
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
                            latConv = self.convertToHex(latitude, GPS_MULTIPLIER, 8)
                            lonConv = self.convertToHex(longitude, GPS_MULTIPLIER, 8)
                            sensorRawData[0] = latitude
                            sensorRawData[1] = longitude
                        elif sensor == bme280_name:
                            #print "BME280Data: %s" % sensorValues
                            bme280Data = sensorValues.split(';')
                            airTemperature = float(bme280Data[0])
                            humidity = float(bme280Data[1])
                            pressure = float(bme280Data[2])
                            airTempConv = self.convertToHex(airTemperature, TEMPERATURE_MULTIPLIER, 4)
                            humidityConv = self.convertToHex(humidity, 1, 2)
                            pressureConv = self.convertToHex(pressure, PRESSURE_MULTIPLIER, 4)
                            sensorRawData[2] = airTemperature
                            sensorRawData[3] = humidity
                            sensorRawData[4] = pressure
                        elif sensor == light_name:
                            #print "LightData: %s" % sensorValues
                            light = sensorValues
                            lightConv = self.convertToHex(light, 1, 6)
                            sensorRawData[5] = light
                        elif sensor == rfid_name:
                            #print "RFIDData: %s" % sensorValues
                            rfid = sensorValues
                            rfidConv = self.convertToHex(rfid, 1, 2)
                            sensorRawData[6] = rfid
                        elif sensor == water_name:
                            #print "WaterData: %s" % sensorValues
                            water = float(sensorValues)
                            waterTempConv = self.convertToHex(water, TEMPERATURE_MULTIPLIER, 4)
                            sensorRawData[7] = water
                        else:
                            # unknown sensor
                            self.logger.log("%s - unknown sensor: %s" % (dateNow, sensor))
                            pass

                        fs.close()    
                        
                    except IOError as (errno, strerror):
                        self.logger.log("I/O error({0}): {1}".format(errno, strerror))
                    except Exception as e:
                        self.logger.log("Unexpected error: {0}".format(e))
                        
                deviceIdHex = self.convertToHex(deviceId, 1, 2)
                timeNow = int(time.time())
                dateHex = self.convertToHex(timeNow, 1, 8)
                # unknown sensor value
                print "Raw sensor data: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensorRawData[0], sensorRawData[1], timeNow, sensorRawData[5], sensorRawData[2],
                                                                        sensorRawData[3], sensorRawData[4], sensorRawData[7], deviceId, sensorRawData[6])
                self.logger.log("Raw sensor data: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensorRawData[0], sensorRawData[1], timeNow, sensorRawData[5], sensorRawData[2],
                                                                        sensorRawData[3], sensorRawData[4], sensorRawData[7], deviceId, sensorRawData[6]))
                # assemble data
                
                print "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceId, rfidConv)
                assembledDataHex = "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceIdHex, rfidConv)
                self.logger.log("Hex data: %s" % assembledDataHex)
                
                # send data
                try:
                    #rbs = RockBLOCKSend()
                    print "Device: %s" % rockBLOCKDevice
                    self.sendMessage(assembledDataHex, rockBLOCKDevice)
                    sentRockMessages = sentRockMessages + 1
                    self.logger.log("Sent message number: %s" % sentRockMessages)
                except rockBlockException as e:
                    print "rockBlockException %s " % e
                    self.logger.log("RockBLOCK Exception: %s" % str(e))


rbw = RockBlockWrapper()
rbw.assembleAndSendData()
#scheduler.add_job(getGPSCoordinates, 'interval', seconds=modem_interval)
#scheduler.start()
