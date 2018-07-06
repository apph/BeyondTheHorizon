import os
import time

class  LoggerUtil:

  def __init__(self,dir,name):
      self.name = name
      self.dir = dir

  def log(self, sensorValue):
      logDate = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
      tmpFile= "%s/%s.log" % (self.dir,  self.name )
      fs = open(tmpFile, "a") 
      fs.write("%s, %s Data: %s\n" % (logDate,self.name,sensorValue))
      fs.close()