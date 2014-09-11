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
    
#============================ main ============================================

def main():
    Mercator()

if __name__=='__main__':
    main()