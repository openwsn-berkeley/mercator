import threading
import serial

class MoteHandler(threading.Thread):
    
    _BAUDRATE = 115200
    
    def __init__(self,serialport):
        
        self.serialport       = serialport
        self.serialLock       = threading.Lock()
        self.lastRxByte       = None
        self.goOn             = True
        self.serial           = serial.Serial(self.serialport,self._BAUDRATE)
        
        threading.Thread.__init__(self)
        self.name = serialport
        
        self.start()
    
    #======================== thread ==========================================
    
    def run(self):
        
        while self.goOn:
            
            rxbyte = self.serial.read(1)
            rxbyte = ord(rxbyte)
            
            print hex(rxbyte)