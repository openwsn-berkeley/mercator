import copy
import threading
import struct
import time

import serial
import socket

import Hdlc
import MercatorDefines as d


class MoteHandler(threading.Thread):

    _BAUDRATE                     = 500000
    TIMEOUT_RESPONSE              = 3

    STAT_UARTNUMRXCRCOK           = 'uartNumRxCrcOk'
    STAT_UARTNUMRXCRCWRONG        = 'uartNumRxCrcWrong'
    STAT_UARTNUMTX                = 'uartNumTx'

    def __init__(self, serialport, cb=None):

        self.serialport           = serialport
        self.cb                   = cb
        self.serialLock           = threading.Lock()
        self.dataLock             = threading.RLock()
        self.mac                  = None
        self.hdlc                 = Hdlc.Hdlc()
        self.busyReceiving        = False
        self.inputBuf             = ''
        self.lastRxByte           = self.hdlc.HDLC_FLAG
        self.goOn                 = True
        self.waitResponse         = None
        self.waitResponseEvent    = None
        self.isActive             = True
        self.response             = None
        self._iotlab              = False
        self._reset_stats()
        try:
            if self.iotlab:
                self.serial       = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.serial.connect((serialport, 20000))
            else:
                self.serial  = serial.Serial(self.serialport, self._BAUDRATE)
        except Exception as err:
            msg = 'could not connect to {0}, reason: {1}'.format(serialport, err)
            print msg
            raise SystemError(msg)

        threading.Thread.__init__(self)
        self.name                 = 'MoteHandler@{0}'.format(serialport)
        self.daemon               = True

        # start reception thread
        self.start()

        # retrieve the state of the mote (to get MAC address)
        self.send_REQ_ST()
        # assert self.mac

    #======================== thread ==========================================

    def run(self):

        while self.goOn:

            if self.iotlab:
                rx_byte = self.serial.recv(1)
            else:
                rx_byte = self.serial.read(1)

            with self.dataLock:
                if      (
                            (not self.busyReceiving)               and
                            self.lastRxByte == self.hdlc.HDLC_FLAG and
                            rx_byte != self.hdlc.HDLC_FLAG
                        ):
                    # start of frame

                    self.busyReceiving       = True
                    self.inputBuf            = self.hdlc.HDLC_FLAG
                    self.inputBuf           += rx_byte
                elif    (
                            self.busyReceiving                     and
                            rx_byte != self.hdlc.HDLC_FLAG
                        ):
                    # middle of frame

                    self.inputBuf           += rx_byte
                elif    (
                            self.busyReceiving                     and
                            rx_byte == self.hdlc.HDLC_FLAG
                        ):
                    # end of frame

                    self.busyReceiving       = False
                    self.inputBuf           += rx_byte

                    try:
                        self.inputBuf        = self.hdlc.dehdlcify(self.inputBuf)
                    except Hdlc.HdlcException:
                        self.stats[self.STAT_UARTNUMRXCRCWRONG] += 1
                    else:
                        self.stats[self.STAT_UARTNUMRXCRCOK] += 1
                        self._handle_inputbuf([ord(b) for b in self.inputBuf])

                self.lastRxByte = rx_byte

        self.serial.close()

    #======================== public ==========================================

    #=== stats

    def get_stats(self):
        with self.dataLock:
            return copy.deepcopy(self.stats)

    #=== requests

    def send_REQ_ST(self):

        with self.dataLock:
            # assert not self.waitResponse
            self.waitResponseEvent     = threading.Event()
            self.waitResponse          = True

        self._send(
            struct.pack(
                '>B',
                d.TYPE_REQ_ST,
            )
        )

        self.waitResponseEvent.wait(self.TIMEOUT_RESPONSE)

        if not self.waitResponseEvent.isSet():
            print "-----------timeout--------------" + self.serialport
            self.isActive = False
            return

        with self.dataLock:
            self.waitResponse          = False
            self.waitResponseEvent     = False
            return_val = copy.deepcopy(self.response)
            self.response              = None

        return return_val

    def send_REQ_IDLE(self):
        self._send(
            struct.pack(
                '>B',
                d.TYPE_REQ_IDLE,
            )
        )

    def send_REQ_TX(self, frequency, txpower, transctr, nbpackets, txifdur, txpksize, txfillbyte):
        self._send(
            struct.pack(
                '>BBbHHHBB',
                d.TYPE_REQ_TX,
                frequency,
                txpower,
                transctr,
                nbpackets,
                txifdur,
                txpksize,
                txfillbyte,
            )
        )

    def send_REQ_RX(self, frequency, srcmac, transctr, txpksize, txfillbyte):
        [m0, m1, m2, m3, m4, m5, m6, m7] = srcmac
        self._send(
            struct.pack(
                '>BBBBBBBBBBHBB',
                d.TYPE_REQ_RX,
                frequency,
                m0, m1, m2, m3, m4, m5, m6, m7,
                transctr,
                txpksize,
                txfillbyte,
            )
        )

    def get_mac(self):
        with self.dataLock:
            return self.mac

    #======================== private =========================================

    #=== stats

    def _reset_stats(self):
        with self.dataLock:
            self.stats = {
                self.STAT_UARTNUMRXCRCOK       : 0,
                self.STAT_UARTNUMRXCRCWRONG    : 0,
                self.STAT_UARTNUMTX            : 0,
            }

    #=== serial rx

    def _handle_inputbuf(self, input_buf):

        try:

            inputtype = input_buf[0]

            if   inputtype == d.TYPE_IND_TXDONE:

                # parse input
                [msg_type] = \
                    struct.unpack(">B", ''.join([chr(b) for b in input_buf]))

                # notify higher layer
                self.cb(
                    serialport = self.serialport,
                    notif      = {
                        'type':             msg_type,
                    }
                )

            elif inputtype == d.TYPE_IND_RX:

                # parse input
                [msg_type, length, rssi, flags, pkctr] = \
                    struct.unpack(">BBbBH", ''.join([chr(b) for b in input_buf]))
                if flags & (1 << 7) != 0:
                    crc = 1
                else:
                    crc = 0

                if flags & (1 << 6) != 0:
                    expected = 1
                else:
                    expected = 0

                if crc == 0 or expected == 0:
                    pkctr = 0

                # notify higher layer
                self.cb(
                    serialport = self.serialport,
                    notif      = {
                        'type':             msg_type,
                        'length':           length,
                        'rssi':             rssi,
                        'crc':              crc,
                        'expected':         expected,
                        'pkctr':            pkctr,
                    }
                )

            elif inputtype == d.TYPE_RESP_ST:

                # parse input
                [msg_type, status, numnotifications, m1, m2, m3, m4, m5, m6, m7, m8] = \
                    struct.unpack(">BBHBBBBBBBB", ''.join([chr(b) for b in input_buf]))

                # remember this mote's MAC address
                with self.dataLock:
                    self.mac = (m1, m2, m3, m4, m5, m6, m7, m8)

                # send response as return code
                with self.dataLock:
                    # assert self.waitResponse
                    self.response = {
                        'type':             msg_type,
                        'status':           status,
                        'numnotifications': numnotifications,
                        'mac':              (m1, m2, m3, m4, m5, m6, m7, m8),
                    }
                    self.waitResponseEvent.set()

            elif inputtype == d.TYPE_IND_UP:

                # parse input
                [msg_type] = \
                    struct.unpack(">B", ''.join([chr(b) for b in input_buf]))

                # notify higher layer
                self.cb(
                    serialport = self.serialport,
                    notif      = {
                        'type':             msg_type,
                        }
                    )

            else:

                raise SystemError('unknown notification type {0}'.format(input_buf[0]))

        except Exception as err:

            print err

            self.cb(
                serialport = self.serialport,
                notif      = err,
            )

    #=== serial tx

    def _send(self, data_to_send):
        with self.dataLock:
            self.stats[self.STAT_UARTNUMTX] += 1
        with self.serialLock:
            hdlc_data = self.hdlc.hdlcify(data_to_send)

            if self.iotlab:
                self.serial.send(hdlc_data)
            else:
                self.serial.write(hdlc_data)
                time.sleep(0.01)

    #=== helpers

    @property
    def iotlab(self):
        if   self.serialport.lower().startswith('com') or self.serialport.count('tty'):
            self._iotlab = False
        else:
            self._iotlab = True

        return self._iotlab
