#!/usr/bin/python

#============================ adjust path =====================================

import os
import sys
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here,'..','lib'))

#============================ imports =========================================

import argparse
import threading
import subprocess
import json
import shlex
import time
import datetime
import MoteHandler
import MercatorDefines as d
import iotlabcli as iotlab
from iotlabcli import experiment

#============================ body ============================================

FIRMWARE_PATH   = "../../firmware/"
DATASET_PATH    = "../../../datasets/"
METAS_PATH      = "../../../metas/"

#============================ body ============================================

class MercatorRunExperiment(object):

    FREQUENCIES    = [n+11 for n in range(16)]   # frequencies to measure on, in IEEE notation
    TXPOWER        = 0                           # dBm
    NUMTRANS       = 5                           # number of transactions
    TXNUMPK        = 10                          # number of packets per transaction
    TXIFDUR        = 100                         # inter-frame duration, in ms
    TXLENGTH       = 100                         # number of bytes (PHY payload) in a frame
    TXFILLBYTE     = 0x0a                        # padding byte

    def __init__(self,serialports,site="local"):

        # local variables
        self.dataLock        = threading.Lock()
        self.transctr        = 0
        self.motes           = {}
        self.isTransmitting  = False
        self.site            = site
        self.freq            = self.FREQUENCIES[0]
        self.transmitterPort = ""

        # connect to motes
        for s in serialports:
            print s
            self.motes[s]    = MoteHandler.MoteHandler(s,self._cb)
            if not self.motes[s].isActive:
                print "DELETED", s
                del self.motes[s]

        self.file            = open('{0}{1}-{2}_raw.csv'.format(DATASET_PATH,
                                    self.site,
                                    datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")),
                                    'w')
        self.file.write('timestamp,mac,frequency,length,rssi,crc,expected,srcmac,transctr,'+
                        'pkctr,txnumpk,txpower,txifdur,txlength,txfillbyte\n')

        # do experiments per frequency
        for freq in self.FREQUENCIES:
            self._doExperimentPerFrequency(freq)

        # print all OK
        raw_input('\nExperiment ended normally. Press Enter to close.')
        self.file.close()
    #======================== public ==========================================

    #======================== cli handlers ====================================

    def _doExperimentPerFrequency(self,freq):

        for transmitterPort in self.motes:
            self._doExperimentPerTransmitter(freq,transmitterPort)

    def _doExperimentPerTransmitter(self,freq,transmitterPort):

        self.transmitterPort = transmitterPort
        self.freq            = freq
        print 'freq={0} transmitterPort={1}'.format(freq,transmitterPort)

        # switch all motes to idle
        for (sp,mh) in self.motes.items():
            print '    switch {0} to idle'.format(sp)
            mh.send_REQ_IDLE()

        # check state, assert that all are idle
        for (sp,mh) in self.motes.items():
            status = mh.send_REQ_ST()
            # assert status['status'] == d.ST_IDLE

        # increment transaction counter
        self.transctr += 1

        # switch all motes to rx
        for (sp,mh) in self.motes.items():
            print '    switch {0} to RX'.format(sp)
            mh.send_REQ_RX(
                frequency         = freq,
                srcmac            = self.motes[transmitterPort].getMac(),
                transctr          = self.transctr,
                txlength          = self.TXLENGTH,
                txfillbyte        = self.TXFILLBYTE,
            )

        # check state, assert that all are in rx mode
        for (sp,mh) in self.motes.items():
            status = mh.send_REQ_ST()
            # assert status['status'] == d.ST_RX

        # switch tx mote to tx
        print '    switch {0} to TX'.format(transmitterPort)

        with self.dataLock:
            self.waitTxDone       = threading.Event()
            self.isTransmitting   = True

        self.motes[transmitterPort].send_REQ_TX(
            frequency             = freq,
            txpower               = self.TXPOWER,
            transctr              = self.transctr,
            txnumpk               = self.TXNUMPK,
            txifdur               = self.TXIFDUR,
            txlength              = self.TXLENGTH,
            txfillbyte            = self.TXFILLBYTE,
        )

        # wait to be done
        maxwaittime = 3*self.TXNUMPK*(self.TXIFDUR/1000.0)
        self.waitTxDone.wait(maxwaittime)
        if self.waitTxDone.isSet():
            print 'done.'
        else:
            # raise SystemError('timeout when waiting for transmission to be done (no IND_TXDONE after {0}s)'.format(maxwaittime))
            return

        # check state, assert numnotifications is expected
        for (sp,mh) in self.motes.items():
            status = mh.send_REQ_ST()
            # if sp==transmitterPort:
                # assert status['status'] == d.ST_TXDONE
            # else:
                # assert status['status'] == d.ST_RX

    #======================== private =========================================

    def _cb(self,serialport,notif):

        if isinstance(notif,dict):
            if   notif['type'] == d.TYPE_RESP_ST:
                print 'state {0}'.format(serialport)
            elif notif['type'] == d.TYPE_IND_TXDONE:
                with self.dataLock:
                    # assert self.isTransmitting
                    self.isTransmitting   = False
                    self.waitTxDone.set()
            elif notif['type'] == d.TYPE_IND_RX:
                # print '.', # TODO: log to file
                timestamp  = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
                mac        = d.formatMac(self.motes[serialport].getMac());
                frequency  = self.freq
                length     = notif['length']
                rssi       = notif['rssi']
                crc        = notif['crc']
                expected   = notif['expected']
                srcmac     = d.formatMac(self.motes[self.transmitterPort].getMac());
                transctr   = self.transctr
                pkctr      = notif['pkctr']
                txnumpk    = self.TXNUMPK
                txpower    = self.TXPOWER
                txifdur    = self.TXIFDUR
                txlength   = self.TXLENGTH
                tfb_raw    = hex(self.TXFILLBYTE).split('x')
                txfillbyte = "{0}x{1}".format(tfb_raw[0], tfb_raw[1].zfill(2))
                # if (crc == 1 and expected == 1):
                self.file.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}\n".format(
                        timestamp,
                        mac,
                        frequency,
                        length,
                        rssi,
                        crc,
                        expected,
                        srcmac,
                        transctr,
                        pkctr,
                        txnumpk,
                        txpower,
                        txifdur,
                        txlength,
                        txfillbyte
                    ))

    def _quitCallback(self):
        print "quitting!"

#=========================== helpers ==========================================

def get_motes(expid):
    # use the file created by auth-cli command
    usr, pwd    = iotlab.get_user_credentials()

    # authenticate through the REST interface
    api = iotlab.rest.Api(usr, pwd)

    # get experiment resources
    data = experiment.get_experiment(api, expid, 'resources')

    return (map(lambda x: x["network_address"].split('.')[0], data["items"]), data["items"][0]["network_address"].split('.')[1])

def submit_experiment(testbed_name, firmware, duration):
    """
    Reserve nodes in the given site.
    The function uses the json experiment file corresponding to the site.
    :param str testbed_name: The name of the testbed (ex: grenoble)
    :param int duration: The duration of the experiment in minutes
    :return: The id of the experiment
    """

    # use the file created by auth-cli command
    usr, pwd    = iotlab.get_user_credentials()

    # authenticate through the REST interface
    api         = iotlab.rest.Api(usr, pwd)

    # load the experiment
    tb_file     = open("{0}states.json".format(METAS_PATH))
    tb_json     = json.load(tb_file)
    nodes       = tb_json[testbed_name]
    firmware    = FIRMWARE_PATH + firmware
    profile     = "mercator"
    resources   = [experiment.exp_resources(nodes, firmware, profile)]

    # submit experiment
    print "Submitting experiment."
    expid       = experiment.submit_experiment(
                    api, "mercatorExp", duration,
                    resources)["id"]

    print "Waiting for experiment to be running."
    experiment.wait_experiment(api, expid)

    return expid

#============================ main ============================================

def main():

    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the current testbed")
    parser.add_argument("firmware", help="The firmware to flash", type=str)
    parser.add_argument("-d", "--duration", help="Duration of the experiment in munutes", type=int, default=30)
    parser.add_argument("-e", "--expid", help="The experiment id", type=int, default=None)
    parser.add_argument("-l", "--local", help="Run the experiment locally", action="store_true")
    args = parser.parse_args()

    if args.local:
        MercatorRunExperiment(
            serialports = ['COM4','COM5','COM6']
        )
    else:
        if args.expid is None:
            expid = submit_experiment(args.testbed, args.firmware, args.duration)
            # get the content
            print("Exp submited with id: %u" % expid)
        else:
            expid = args.expid
        (serialports, site) = get_motes(expid);
        MercatorRunExperiment(
            serialports = serialports,
            site = site
        )

if __name__=='__main__':
    main()

