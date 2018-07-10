from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil
import ConfigParser
from Adafruit_BME280 import *

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

logDir = properties.get('general', 'logDir')

bme280_devId = properties.get('general', 'deviceId')
bme280_name = properties.get('bme280', 'name') 
bme280_interval = int(properties.get('bme280', 'interval')) 
bme280_reportDir = properties.get('general', 'reportDir')

#set Scheduler
scheduler = BlockingScheduler()

#Set Logger
logger = LoggerUtil(logDir,bme280_name)

# Create new sensor instance
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

def getBME280Reading():  
      try:   
            # grab data from sensor     
            sensorValues = [sensor.read_temperature(), sensor.read_humidity(), sensor.read_pressure() / 100]

            sensorValue = "%s;%s;%s" % (format(sensorValues[0], '.2f'), sensorValues[1], format(sensorValues[2], '.1f'))
            print sensorValue
      
            #print sensorReportLine
   
            FileUtil.saveToNewFile(bme280_reportDir,bme280_name,sensorValue)
            logger.log(sensorValue)
            print "Loging"
      except Exception as e:
            print e
            logger.log("ERROR" + e)
      
scheduler.add_job(getBME280Reading, 'interval', seconds=bme280_interval)
scheduler.start()
