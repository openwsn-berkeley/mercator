#!/usr/bin/python

#============================ adjust path =====================================

import os
import sys
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here,'..','Mercator'))

#============================ imports =========================================

import threading

import OpenCli
import MoteHandler

#============================ body ============================================

class Mercator(object):
    
    def __init__(self):
        
        self.dataLock   = threading.Lock()
        self.motes      = {}
        
        cli             = OpenCli.OpenCli("Mercator CLI",self.quitCallback)
        cli.registerCommand(
            'connect',
            'c',
            'connect to a mote',
            ['serialport'],
            self._cli_connect
        )
        cli.registerCommand(
            'list',
            'l',
            'list motes',
            [],
            self._cli_list
        )
        cli.registerCommand(
            'state',
            'st',
            'request state',
            ['serialport'],
            self._cli_state
        )
        cli.registerCommand(
            'idle',
            'id',
            'switch radio off',
            ['serialport'],
            self._cli_idle
        )
        cli.registerCommand(
            'tx',
            'tx',
            'transmit a number of packets',
            ['serialport', 'frequency'],
            self._cli_tx
        )
        cli.registerCommand(
            'rx',
            'rx',
            'start receiving',
            ['serialport'],
            self._cli_rx
        )
        cli.start()
    
    def quitCallback(self):
        print "quitting!"
    
    def _cli_connect(self,params):
        serialport = params[0]
        
        if serialport in self.motes:
            print 'already connected to {0}'.format(serialport)
            return
        
        with self.dataLock:
            self.motes[serialport] = MoteHandler.MoteHandler(serialport)
    
    def _cli_list(self,params):
        with self.dataLock:
            for m in self.motes.keys():
                print m
    
    def _cli_state(self,params):
        serialport = params[0]
        
        with self.dataLock:
            self.motes[serialport].send_REQ_ST()
    
    def _cli_idle(self,params):
        serialport = params[0]
        
        with self.dataLock:
            self.motes[serialport].send_REQ_IDLE()
    
    def _cli_tx(self,params):
        serialport = params[0]
        frequency = params[1]

        with self.dataLock:
            self.motes[serialport].send_REQ_TX(
                frequency    = frequency,
                txpower      = 0,
                transctr     = 0x0a,
                txnumpk      = 10,
                txifdur      = 100,
                txlength     = 100,
                txfillbyte   = 0x0b,
            )
    
    def _cli_rx(self,params):
        serialport = params[0]
        
        with self.dataLock:
            self.motes[serialport].send_REQ_RX(
                frequency    = 26,
                srcmac       = [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88],
                transctr     = 0x0a,
                txlength     = 100,
                txfillbyte   = 0x0b,
            )
    
#============================ main ============================================

def main():
    Mercator()

if __name__=='__main__':
    main()