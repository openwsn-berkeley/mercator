#!/usr/bin/python

#============================ adjust path =====================================

import os
import sys
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'lib'))

#============================ imports =========================================

import threading

import OpenCli
import MoteHandler
import MercatorDefines as d

#============================ body ============================================


class MercatorCli(object):

    ALL = 'all'

    def __init__(self):

        self.dataLock   = threading.Lock()
        self.motes      = {}

        cli             = OpenCli.OpenCli("Mercator CLI", self._quit_callback)
        cli.register_command(
            'connect',
            'c',
            'connect to a mote',
            ['serialport'],
            self._cli_connect
        )
        cli.register_command(
            'list',
            'l',
            'list motes',
            [],
            self._cli_list
        )
        cli.register_command(
            'state',
            'st',
            'request state',
            ['serialport'],
            self._cli_state
        )
        cli.register_command(
            'idle',
            'id',
            'switch radio off',
            ['serialport'],
            self._cli_idle
        )
        cli.register_command(
            'tx',
            'tx',
            'transmit a number of packets',
            ['serialport'],
            self._cli_tx
        )
        cli.register_command(
            'rx',
            'rx',
            'start receiving',
            ['serialport'],
            self._cli_rx
        )
        cli.start()

    #======================== public ==========================================

    #======================== cli handlers ====================================

    def _cli_connect(self, params):
        serialport = params[0]

        if serialport in self.motes:
            print 'already connected to {0}'.format(serialport)
            return

        with self.dataLock:
            self.motes[serialport] = MoteHandler.MoteHandler(serialport, self._cb)
            if not self.motes[serialport].isActive:
                del self.motes[serialport]

    def _cli_list(self):
        output          = []
        with self.dataLock:
            output     += ['connected to {0} motes:'.format(len(self.motes))]
            output     += ['- {0}'.format(m) for m in self.motes.keys()]
        output          = '\n'.join(output)
        print output

    def _cli_state(self, params):
        serialport = params[0]

        if serialport == self.ALL:
            serialports = self.motes.keys()
        else:
            if serialport not in self.motes.keys()+[self.ALL]:
                print 'not serialport to {0}'.format(serialport)
                return
            serialports = [serialport]

        with self.dataLock:
            for s in serialports:
                print self.motes[s].send_REQ_ST()

    def _cli_idle(self, params):
        serialport = params[0]

        if serialport == self.ALL:
            serialports = self.motes.keys()
        else:
            if serialport not in self.motes.keys()+[self.ALL]:
                print 'not serialport to {0}'.format(serialport)
                return
            serialports = [serialport]

        with self.dataLock:
            for s in serialports:
                self.motes[s].send_REQ_IDLE()

    def _cli_tx(self, params):
        serialport = params[0]

        if serialport not in self.motes:
            print 'not serialport to {0}'.format(serialport)
            return

        with self.dataLock:
            self.motes[serialport].send_REQ_TX(
                frequency    = 0x14,
                txpower      = 0,
                transctr     = 0x0a0a,
                nbpackets    = 5,
                txifdur      = 1000,
                txpksize     = 100,
                txfillbyte   = 0x0b,
            )

    def _cli_rx(self, params):
        serialport = params[0]

        if serialport == self.ALL:
            serialports = self.motes.keys()
        else:
            if serialport not in self.motes.keys()+[self.ALL]:
                print 'not serialport to {0}'.format(serialport)
                return
            serialports = [serialport]

        with self.dataLock:
            for s in serialports:
                self.motes[s].send_REQ_RX(
                    frequency    = 0x14,
                    srcmac       = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
                    transctr     = 0x0a0a,
                    txpksize     = 100,
                    txfillbyte   = 0x0b,
                )

    #======================== private =========================================

    def _cb(self, serialport, notif):
        output               = []
        output              += [' - {0}'.format(serialport)]
        if isinstance(notif, dict):
            if 'type' in notif:
                output      += ['    . type             : {0}'.format(d.type_num2text(notif['type']))]
            if 'status' in notif:
                output      += ['    . status           : {0}'.format(d.status_num2text(notif['status']))]
            if 'mac' in notif:
                output      += ['    . mac              : {0}'.format(d.format_mac(notif['mac']))]
            for (k, v) in notif.items():
                if k not in ['type', 'status', 'mac']:
                    output  += ['    . {0:<17}: {1}'.format(k, v)]
        else:
            output          += ['  {0}'.format(notif)]
        output              += ['']
        output               = '\n'.join(output)
        print output

    def _quit_callback(self):
        print "quitting!"

#============================ main ============================================


def main():
    MercatorCli()

if __name__ == '__main__':
    main()
