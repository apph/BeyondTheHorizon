import rockBlock
 
from rockBlock import rockBlockProtocol
 
class RockBLOCKSend(rockBlockProtocol):
    
    def sendMessage(self, message, device):
        rb = rockBlock.rockBlock(device, self)
        rb.sendMessage(message)      
	rb.close()
        
    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"
        
    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"
        
    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)
        