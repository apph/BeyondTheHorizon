import os

class  FileUtil:

    @staticmethod
    def saveToNewFile( dir,name, sensorValue):
      tmpFile= "%s/%s.tmp" % (dir,  name)
      fs = open(tmpFile, "w") 
      #fs.write(sensorReportLine)
      fs.write(str(sensorValue))
      fs.close()
      
      dataFile= "%s/%s" % (dir,  name)
      # Rename removes the file
      os.rename(tmpFile, dataFile) 
      

      