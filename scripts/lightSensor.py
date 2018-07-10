#BH1750
from apscheduler.schedulers.blocking import BlockingScheduler
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil
import ConfigParser
import smbus
import time


# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')

name = properties.get('light', 'name')
interval = int(properties.get('light', 'interval'))

scheduler = BlockingScheduler()

#Set Logger
logger = LoggerUtil(logDir,name)


# Define some constants from the datasheet
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

 
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
  return convertToNumber(data)
 
def measureLight():

    try:
        lightLevel = readLight()
        intLightLevel = int(lightLevel)
        FileUtil.saveToNewFile(reportDir,name,intLightLevel)
        sensorValueForLogger = ": %s lux" % (lightLevel)
        logger.log(sensorValueForLogger)
    except Exception as e:
        print e
        logger.log("Error "+ e)
     

scheduler.add_job(measureLight, 'interval', seconds=interval)
scheduler.start()


