from apscheduler.schedulers.blocking import BlockingScheduler
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil
import w1thermsensor 
import ConfigParser

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/home/pi/sensorScripts/config/antReader.cfg')

reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')

name = properties.get('waterTemp', 'name')
interval = int(properties.get('waterTemp', 'interval'))

#set Scheduler
scheduler = BlockingScheduler()

#Set Sensor
sensor = w1thermsensor.W1ThermSensor()

#Set Logger
logger = LoggerUtil(logDir,name)


def measureTmeperature():
    temperature = sensor.get_temperature()
    temperature = format(temperature, '.2f')
    #print("The temperature is %s celsius" % temperature)
    try:
        FileUtil.saveToNewFile(reportDir,name,temperature)
        logger.log(temperature)
    except Exception as e:
        print e
    

scheduler.add_job(measureTmeperature, 'interval', seconds=1)
scheduler.start()


