from apscheduler.schedulers.blocking import BlockingScheduler
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil
import ConfigParser

#adapter specific
import serial
import pynmea2 
 

# read properties
properties = ConfigParser.ConfigParser()
properties.read('/etc/antReader.cfg')
reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')


name = properties.get('gps', 'name')
interval = int(properties.get('gps', 'interval'))
print name
gps_serialPort = properties.get('gps', 'serialPort')
gps_speed = int(properties.get('gps', 'speed'))
gps_timeout = float(properties.get('gps', 'timeout'))

#set Scheduler
#scheduler = BlockingScheduler()

#Set Logger
logger = LoggerUtil(logDir,name)

# Create new sensor instance
print gps_serialPort
serialStream = serial.Serial(gps_serialPort, gps_speed, timeout=gps_timeout)


      
while 1:
    speed = 0.0
    latitude = 0
    longitude = 0
    
    print "Reading Coordinates"

    try:
        sentence = serialStream.readline()   
        logger.log("Sentence: " +sentence)     
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
                latitude = format(gpsData.latitude, '.6f')
                longitude = format(gpsData.longitude, '.6f')
                sensorValue = "%s;%s" % (latitude, longitude)
                sensorValueForLogger = "Sat_num: %s, gps_quality: %s,Lat: %s; Long: %s; Alt: %s; Speed %f" % (gpsData.num_sats,gpsData.gps_qual,gpsData.latitude, gpsData.longitude, gpsData.altitude, speed)
                FileUtil.saveToNewFile(reportDir,name,sensorValue)
                logger.log(sensorValueForLogger)
            except Exception as e:
                print e
                logger.log(e)
    except Exception as e:
        print e
        logger.log(e)

          
        
#scheduler.add_job(getGPSCoordinates, 'interval', seconds=interval)
#scheduler.start()