import serial
from RfidParser import MyParser
from FileUtil import FileUtil
from LoggerUtil import LoggerUtil

READ_FAILURE = 111
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


def getDictValueIfKeyContainsString( dictionary, partialKey):
    partialKey = partialKey.lower()
    for key in dictionary:
        if partialKey in key:
            return dictionary.get(key)
    return None 



while True:
    serial.flushInput()
    rfid_data = serial.readline().strip()
    if len(rfid_data) > 0:
        try:
            #it is a preacheck if the data were correclty read
            rfidData = rfid_data[1:11]      
            dictValue = getDictValueIfKeyContainsString(cardNumDict,rfidData)
            logger.log("Card: "+rfidData + " mapped to: " + dictValue)
            if dictValue  is not None: 
                FileUtil.saveToNewFile(reportDir,name,dictValue)
                logger.log("Read OK")
                logger.log(dictValue)
            else:
                logger.log("Error read")
                rfidData = rfid_data[3:10]
                dictValue = getDictValueIfKeyContainsString(Dict,rfidData)
                logger.log("Card: "+rfidData + " mapped to: " + dictValue)
                if dictValue  is not None: 
                    FileUtil.saveToNewFile(reportDir,name,dictValue)
                    logger.log("Read OK")
                    logger.log(dictValue)
                else:
                    FileUtil.saveToNewFile(reportDir,name,READ_FAILURE)
                    logger.log("Read Failure")
                    logger.log(READ_FAILURE)
        except Exception as e:
            FileUtil.saveToNewFile(reportDir,name,READ_FAILURE)
            logger.log(e)
            logger.log(READ_FAILURE)
        


