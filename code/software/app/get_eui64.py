#!/usr/bin/python

#============================ adjust path =====================================

import os
import sys
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'lib'))

#============================ imports =========================================

import argparse
import threading
import json
import datetime
import logging.config
import serial
import socket

# Mercator
import MoteHandler
import MercatorDefines as d

# IoT-lab
import iotlabcli as iotlab
from iotlabcli import experiment

#============================ logging =========================================

logging.config.fileConfig('logging.conf')

logconsole  = logging.getLogger("console")
logfile     = logging.getLogger()  #root logger

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
    _BAUDRATE      = 500000

    def __init__(self, serialports, site="local"):

        # local variables
        self.dataLock        = threading.Lock()
        self.transctr        = 0
        self.motes           = {}
        self.isTransmitting  = False
        self.site            = site
        self.transmitterPort = ""
        address_list    = []

        # connect to motes
        for ser_port in serialports:
            ser = None

            logfile.debug("connecting to %s", ser_port)

            try:
                if site != "local":
                    ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ser.connect((ser_port, 20000))
                else:
                    ser  = serial.Serial(ser_port, self._BAUDRATE)
            except Exception as err:
                msg = 'could not connect to {0}, reason: {1}'.format(ser_port, err)
                raise SystemError(msg)

            logfile.debug("reading %s address", ser_port)
            addr = ""
            if site != "local":
                goOn = True
                while len(addr)<23:
                    c = ser.recv(1)
                    if len(c) > 0:
                        if (c != '\n') and (c != '\r') and (ord(c) < 103):
                            addr += c
                        elif c == '\n':
                            goOn = False
            else:
                addr = ser.readline() # remove unfinished line
                addr = ser.readline().rstrip('\r\n')

            address_list.append((addr,ser_port))
            logconsole.info("{0},{1}".format(addr, ser_port))

        address_list.sort(key=lambda tup: tup[1])
        with open("mac_list.csv",'w') as f:
            for address in address_list:
              f.write("{0},{1}\n".format(address[0],address[1]))

        # print all OK
        raw_input('\nExperiment ended normally. Press Enter to close.')

    def _quit_callback(self):
        print "quitting!"

#=========================== helpers ==========================================


def get_motes(expid):
    # use the file created by auth-cli command
    usr, pwd    = iotlab.get_user_credentials()

    # authenticate through the REST interface
    api = iotlab.rest.Api(usr, pwd)

    # get experiment resources
    data = experiment.get_experiment(api, expid, 'resources')

    return (map(lambda x: x["network_address"].split('.')[0], data["items"]),
            data["items"][0]["network_address"].split('.')[1])


def submit_experiment(testbed_name, board, firmware, duration):
    """
    Reserve nodes in the given site.
    The function uses the json experiment file corresponding to the site.
    :param str firmware: the name of the firmware as it is in the code/firmware/ folder
    :param str board: the type of board (ex: m3)
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
    nodes       = [x for x in tb_json[testbed_name] if board in x]
    firmware    = FIRMWARE_PATH + firmware
    profile     = "mercator"
    resources   = [experiment.exp_resources(nodes, firmware, profile)]

    # submit experiment
    logconsole.info("Submitting experiment.")
    expid       = experiment.submit_experiment(
                    api, "mercatorExp", duration,
                    resources)["id"]

    logconsole.info("Experiment submited with id: %u", expid)
    logconsole.info("Waiting for experiment to be running.")
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
    parser.add_argument("-b", "--board", help="The type of board to use", type=str, default="m3")
    args = parser.parse_args()

    if args.testbed == "local":
        MercatorRunExperiment(
            serialports = ['/dev/ttyUSB1']
        )
    else:
        if args.expid is None:
            expid = submit_experiment(args.testbed, args.board, args.firmware, args.duration)
        else:
            expid = args.expid
        (serialports, site) = get_motes(expid)
        MercatorRunExperiment(
            serialports = serialports,
            site = site
        )

if __name__ == '__main__':
    main()

