from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil
import ConfigParser
import Adafruit_LSM9DS0


# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')

lsm9ds0_devId = properties.get('general', 'deviceId')
lsm9ds0_name = properties.get('lsm9ds0', 'name')
lsm9ds0_interval = int(properties.get('lsm9ds0', 'interval'))
lsm9ds0_reportDir = properties.get('general', 'reportDir')

logDir = properties.get('general', 'logDir')
logFile = "%s%s.log" % (logDir, lsm9ds0_name)

# Create new sensor instance
imu = Adafruit_LSM9DS0.LSM9DS0()

#set Scheduler
scheduler = BlockingScheduler()

#Set Logger
logger = LoggerUtil(logDir,lsm9ds0_name)

def getLSM9DS0Reading():
      # grab data from sensor 
      gyro, mag, accel = imu.read()
       
      sensorValues = [gyro, mag, accel]
      print sensorValues
      
      gyro_x, gyro_y, gyro_z = gyro
      mag_x, mag_y, mag_z = mag
      accel_x, accel_y, accel_z = accel
      
      sensorValue = "%s; %s; %s; %s; %s; %s; %s; %s; %s" % (gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, accel_x, accel_y, accel_z)
      logger.log("%s, Gyro: %s %s %s, Mag: %s %s %s, Accel: %s %s %s\n" % (logDate, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, accel_x, accel_y, accel_z))
      print sensorValue
   
      FileUtil.saveToNewFile(lsm9ds0_reportDir, lsm9ds0_name,sensorValue)
      

scheduler.add_job(getLSM9DS0Reading, 'interval', seconds=lsm9ds0_interval)
scheduler.start()
       

