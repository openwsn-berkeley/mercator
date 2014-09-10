import threading
import serial

import Hdlc

class MoteHandler(threading.Thread):
    
    _BAUDRATE = 115200
    
    def __init__(self,serialport):
        
        self.serialport       = serialport
        self.serialLock       = threading.Lock()
        self.dataLock         = threading.Lock()
        self.hdlc             = Hdlc.Hdlc()
        self.busyReceiving    = False
        self.inputBuf         = ''
        self.lastRxByte       = self.hdlc.HDLC_FLAG
        self.goOn             = True
        self.serial           = serial.Serial(self.serialport,self._BAUDRATE)
        
        threading.Thread.__init__(self)
        self.name = serialport
        
        self.start()
    
    #======================== thread ==========================================
    
    def run(self):
        
        while self.goOn:
            
            rxByte = self.serial.read(1)
            
            with self.dataLock:
                if      (
                            (not self.busyReceiving)             and 
                            self.lastRxByte==self.hdlc.HDLC_FLAG and
                            rxByte!=self.hdlc.HDLC_FLAG
                        ):
                    # start of frame
                    
                    self.busyReceiving       = True
                    self.inputBuf            = self.hdlc.HDLC_FLAG
                    self.inputBuf           += rxByte
                elif    (
                            self.busyReceiving                   and
                            rxByte!=self.hdlc.HDLC_FLAG
                        ):
                    # middle of frame
                    
                    self.inputBuf           += rxByte
                elif    (
                            self.busyReceiving                   and
                            rxByte==self.hdlc.HDLC_FLAG
                        ):
                    # end of frame
                    
                    self.busyReceiving       = False
                    self.inputBuf           += rxByte
                    
                    try:
                        self.inputBuf        = self.hdlc.dehdlcify(self.inputBuf)
                    except Hdlc.HdlcException as err:
                        print 'invalid serial frame'
                    else:
                        print 'valid!'
                
                self.lastRxByte = rxByte
