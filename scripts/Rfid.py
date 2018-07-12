import serial
from RfidParser import MyParser
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil

READ_FAILURE = 255
# read mapping
rfidParser = MyParser()
rfidParser.read('/etc/cardMapper.cfg')
cardNumDict = rfidParser.as_dict()
cardNumDict= cardNumDict['CardsNum']

properties = MyParser()
properties.read('/etc/antReader.cfg')

reportDir = properties.get('general', 'reportDir')
logDir = properties.get('general', 'logDir')

name = properties.get('rfid', 'name')
rfid_serial = properties.get('rfid', 'serialPort')
serial = serial.Serial(rfid_serial,baudrate=9600)

#Set Logger
logger = LoggerUtil(logDir,name)

oldRfidCode = 0


def getDictValueIfKeyContainsString( dictionary, partialKey):
    partialKey = partialKey.lower()
    for key in dictionary:
        if partialKey in key:
            return dictionary.get(key)
    return None 

def saveResult(rfidData,dictValue):
    global oldRfidCode
    logger.log("Card: "+rfidData + " mapped to: " + dictValue)
    if (oldRfidCode != dictValue):
        FileUtil.saveToNewFile(reportDir,name,dictValue)
        oldRfidCode=dictValue
    else:
        logger.log("Duplicate read")



while True:
    serial.flushInput()
    rfid_data = serial.readline().strip()
    if len(rfid_data) > 0:
        logger.log("Rfid Data: %s" % (rfid_data)) 
        try:
            #it is a preacheck if the data were correclty read
            rfidData = rfid_data[1:11]
                 
            dictValue = getDictValueIfKeyContainsString(cardNumDict,rfidData)
            if dictValue  is not None: 
                saveResult(rfidData,dictValue)
            else:
                logger.log("Error read")
                rfidData = rfid_data[3:11]
                dictValue = getDictValueIfKeyContainsString(cardNumDict,rfidData)
                if dictValue  is not None: 
                    saveResult(rfidData,dictValue)
                else:
                    FileUtil.saveToNewFile(reportDir,name,READ_FAILURE)
                    logger.log("Read Failure")
                    logger.log(READ_FAILURE)
        except Exception as e:
            FileUtil.saveToNewFile(reportDir,name,READ_FAILURE)
            logger.log("Error has occured:")
            logger.log("Sending error message:")
            logger.log(str(e))
            
        


