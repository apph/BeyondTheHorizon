from datetime import datetime
from rockBlock import rockBlockException
from rockBlock import rockBlockProtocol
from apscheduler.schedulers.blocking import BlockingScheduler
from LoggerUtil import LoggerUtil
from subprocess import call
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
songsRepo = properties.get('rockBLOCK', 'songsRepo')

sensorsList = properties.get('rockBLOCK', 'sensors')
logDir = properties.get('general', 'logDir')

gps_name = properties.get('gps', 'name')
bme280_name = properties.get('bme280', 'name')

rfid_name = properties.get('rfid', 'name')
light_name = properties.get('light', 'name')
water_name = properties.get('waterTemp', 'name')

rfidFile = "%s%s" % (reportDir, rfid_name)

rockSendMessages = True


class RockBlockWrapper(rockBlockProtocol):
    logger = LoggerUtil(logDir, modem_name)
    messagesCount = 0
    sentRockMessages = 0

    def returnNetworkTime(self, device):
       rb = rockBlock.rockBlock(device, self)
       self.logger.log("returnNetworkTime - calling for time to the satellite.")
       networkTime = rb.networkTime()
       rb.close()
       return networkTime

    def sendMessage(self, message, device):
        rb = rockBlock.rockBlock(device, self)
        self.logger.log("sendMessages - sending a message to the satellite.")
        rb.sendMessage(message)      
	rb.close()
	
    def requestMessages(self, device):
        rb = rockBlock.rockBlock(device, self)
        self.logger.log("requestMessages - checking for new messages from the satellite.")
        rb.messageCheck()      
	rb.close()
        
    def rockBlockTxStarted(self):
        self.logger.log("rockBlockTxStarted")
        
    def rockBlockTxFailed(self):
        self.logger.log("rockBlockTxFailed")
        
    def rockBlockTxSuccess(self,momsn):
        # TODO: save value to a file? What if script is restarted. We are counting from 0
        self.sentRockMessages = self.sentRockMessages + 1
        self.logger.log("Sent message number " + str(momsn))
        
    def rockBlockRxReceived(self, mtmsn, data):
        self.logger.log("rockBlockRxRecevied, message number %s, data %s " % (str(mtmsn), data))
        if (str(data).startswith("F")):
            newInterval = int(data[1:])
            if (newInterval >= minInterval and newInterval <= maxInterval):
                global modem_interval
                modem_interval = newInterval
                self.logger.log("RockBLOCK - rockBlockRxReceived - new interval set to %s" % modem_interval)
        elif (str(data).startswith("S")):
            command = data[1:]
            if command == "reboot":
                self.logger.log("RockBLOCK - rockBlockRxReceived - reboot request!")
                os.system('sudo shutdown -r now')
            elif command == "sendOn":
                global rockSendMessages
                self.logger.log("RockBLOCK - rockBlockRxReceived - sending messages is on!")
                rockSendMessages = True
            elif command == "sendOff":
                global rockSendMessgaes
                self.logger.log("RockBLOCK - rockBlockRxReceived - sending messages is off!")
                rockSendMessages = False
        elif (str(data).startswith("M")):
            songName = data[1:]
            songFile = songsRepo + songName
            call(["omxplayer", songFile])
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
        forceSendData = False

        while True:
            timeNow = int(time.time())
            # init to default values if nothing comes from the sensor files
            latConv = self.convertToHex(0.0, GPS_MULTIPLIER, 8)
            lonConv = self.convertToHex(0.0, GPS_MULTIPLIER, 8)
            airTempConv = self.convertToHex(0.0, TEMPERATURE_MULTIPLIER, 4)
            humidityConv = self.convertToHex(0, 1, 2)
            pressureConv = self.convertToHex(0.0, PRESSURE_MULTIPLIER, 4)
            waterTempConv = self.convertToHex(0.0, TEMPERATURE_MULTIPLIER, 4)
            lightConv = self.convertToHex(0, 1, 6)
            gpsTime = 0
            
            # no swimmer? -> FF
            rfidConv = self.convertToHex(255, 1, 2)
            
            # pre-initialize array with 9 elements
            sensorRawData = [None] * 9

            # check if there was RFID file modification. If yes, it means swimmer has changed
            rfidMTime = 0
            if os.path.isfile(rfidFile):
                rfidMTime = int(os.stat(rfidFile).st_mtime)
            
            # if we have reached maximum number of messages stop sending (will be too expensive)
            if self.sentRockMessages > maxRockMessages:
                self.logger.log("Maximum possible messages sent. Exiting...")
                break
          
            # change of swimmer, send data
            if rfidMTime >= timePrev:
                forceSendData = True

            # do we need to poll RockBLOCK for configuration updates
            if (timeNow >= timePrev + rockPollInterval):
                if self.messagesCount > 0:
                    try:
                        self.requestMessages(rockBLOCKDevice)
                    except rockBlockException as e:
                        self.logger.log("RockBLOCK - requestMessages, exception: %s" % str(e))

            if (timeNow >= timePrev + modem_interval) or forceSendData:
                self.logger.log("Collecting data for process %s" % os.getpid())
                forceSendData = False
                sensors = sensorsList.split(';')
                timePrev = timeNow

                #print "Sensors: %s" % sensors
                timeStart = int(time.time())

                for cnt in range(0, len(sensors)):
                    try: 
                        sensor = sensors[cnt]
                        sensorDataFile = "%s%s" % (reportDir, sensor)
                        fs = open(sensorDataFile, "r")
                        sensorValues = fs.read()

                        if sensor == gps_name:
                            #print "GPSData %s" % sensorValues
                            gpsData = sensorValues.split(';')
                            gpsTime = int(gpsData[0])
                            latitude = float(gpsData[1])
                            longitude = float(gpsData[2])
                            latConv = self.convertToHex(latitude, GPS_MULTIPLIER, 8)
                            lonConv = self.convertToHex(longitude, GPS_MULTIPLIER, 8)
                            sensorRawData[0] = latitude
                            sensorRawData[1] = longitude
                            sensorRawData[8] = gpsTime
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
                            self.logger.log("unknown sensor: %s" % (sensor))
                            pass

                        fs.close()    
                        
                    except IOError as (errno, strerror):
                        self.logger.log("I/O error({0}): {1}".format(errno, strerror))
                    except Exception as e:
                        self.logger.log("Unexpected error: {0}".format(e))

                timeStop = int(time.time())
                timeDiff = timeStop - timeStart

                self.logger.log("Computing data took: %s ms" % str(timeDiff))
                        
                deviceIdHex = self.convertToHex(deviceId, 1, 2)

                networkTime = self.returnNetworkTime(rockBLOCKDevice)
                self.logger.log("networkTime from satellite %s" % networkTime)
                dateHex = self.convertToHex(networkTime, 1, 8)
                # unknown sensor value
                print "Raw sensor data: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensorRawData[0], sensorRawData[1], networkTime, sensorRawData[5], sensorRawData[2],
                                                                        sensorRawData[3], sensorRawData[4], sensorRawData[7], deviceId, sensorRawData[6])
                self.logger.log("Raw sensor data: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (sensorRawData[0], sensorRawData[1], networkTime, sensorRawData[5], sensorRawData[2],
                                                                        sensorRawData[3], sensorRawData[4], sensorRawData[7], deviceId, sensorRawData[6]))
                # assemble data
                
                print "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceId, rfidConv)
                assembledDataHex = "%s%s%s%s%s%s%s%s%s%s" % (latConv, lonConv, dateHex, lightConv, airTempConv, humidityConv, pressureConv, waterTempConv, deviceIdHex, rfidConv)
                self.logger.log("Hex data: %s" % assembledDataHex)
                
                # send data
                try:
                    if rockSendMessages and networkTime != 0:
                        self.sendMessage(assembledDataHex, rockBLOCKDevice)
                except rockBlockException as e:
                    print "rockBlockException %s " % e
                    self.logger.log("RockBLOCK Exception: %s" % str(e))


rbw = RockBlockWrapper()
rbw.assembleAndSendData()

