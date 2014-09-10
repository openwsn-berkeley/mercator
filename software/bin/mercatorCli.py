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
        self.motes      = []
        
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
        cli.start()
    
    def quitCallback(self):
        print "quitting!"
    
    def _cli_connect(self,params):
        serialport = params[0]
        
        with self.dataLock:
            self.motes += [MoteHandler.MoteHandler(serialport)]
    
    def _cli_list(self,params):
        print 'poipoi'
    
#============================ main ============================================

def main():
    Mercator()

if __name__=='__main__':
    main()