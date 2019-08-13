import enum
import logging
import socket
import struct
import threading
import time

import netaddr

from mercator.hdlc import (hdlc_calc_crc, hdlc_verify_crc,
                           hdlc_escape, hdlc_unescape,
                           HDLC_FLAG, HDLC_MIN_BODY_LEN)
from mercator.utils import restore_xon_xoff, OSName

class MsgType(enum.IntEnum):
    REQ_ST = 1
    RESP_ST = 2
    REQ_IDLE = 3
    REQ_TX = 4
    IND_TXDONE = 5
    REQ_RX = 6
    IND_RX = 7
    IND_UP = 8
    RESP_IDLE = 10
    RESP_TX = 11
    RESP_RX = 12


class RxFlag(enum.IntFlag):
    GOOD_CRC = 128
    RIGHT_FRAME = 64
    EXPECTED_FLAGS = 192 # GOOD_CRC | RIGHT_FRAME

class NodeStatus(enum.IntEnum):
    STOPPING_RX = 0   # internal use
    IDLE = 1
    TXDONE = 2
    TX = 3
    RX = 4
    UNKNOWN = -1

class Node(object):
    MAX_REQUEST_RETRIES = 3
    STATUS_POLLING_INTERVAL = 0.5
    DUMMY_TX_POWER_VALUE = 0

    def __init__(self, platform):
        self.platform = platform

        # initialize variables for thread
        self.keep_receiving_thread = None
        self.lock = threading.Lock()

        # for serial communication
        self.serial_leftover = b''

        # for measurements
        self._status = NodeStatus.UNKNOWN
        self.tx_node = False
        self.tx_power_dbm = None
        self.tx_len = None
        self.tx_num_pk = None
        self.tx_ifdur_ms = None
        self.tx_fill_byte = None
        self.rssi_records = None
        self.current_channel = None
        self.current_trans_ctr = None
        self.current_tx_mac_addr = None

    def setup(self, config):
        # mercator related
        # Note: OpenWSN doesn't support tx_power_dbm; see
        # 03oos_mercator.c in openwsn-fw repository. set a dummy value
        if self.platform.firmware_os_name == OSName.OpenWSN:
            self.tx_power_dbm = self.DUMMY_TX_POWER_VALUE
        else:
            raise NotImplementedError('{0} is not supported'.format(
                self.platform.firmware_os_name))
        self.tx_node = self._am_i_tx_node(config['tx_nodes'])
        self.tx_len = config['tx_len']
        self.tx_num_pk = config['tx_num_per_transaction']
        self.tx_ifdur_ms = config['tx_interval_ms']
        self.tx_fill_byte = config['tx_fill_byte']
        self.rssi_records = [None] * self.tx_num_pk

        self._setup() # platform-specific setup method

        # make sure to get the node IDLE
        status, self.mac_addr = self.request_status()
        if status != NodeStatus.IDLE:
            self.request_idle()
        self._status = NodeStatus.IDLE

    @property
    def status(self):
        with self.lock:
            return self._status

    @status.setter
    def status(self, status):
        with self.lock:
            self._status = status

    def request_status(self):
        result = self._issue_command(self._send_req_st,
                                     self._recv_resp_st)
        if result:
            node_status = result[0]
            mac_addr = result[1]
        else:
            node_status = None
            mac_addr = None
        return node_status, mac_addr

    def request_idle(self):
        result = self._issue_command(self._send_req_idle,
                                     self._recv_resp_idle)
        # change the status to IDLE as we received RESP_IDLE
        if result:
            assert result[0] is True
            self.status = NodeStatus.IDLE
        else:
            # do nothing
            pass

    def update_status(self):
        self.status, _ = self.request_status()

    def wait_ind_up(self):
        logging.info('Wait for IND_UP from {0}'.format(self.id))
        msg = self._recv_msg()
        if msg and (msg[0] == MsgType.IND_UP):
            # done
            pass
        else:
            # IND_UP is gone somewhere; this is normal especially
            # running on FIT/IoT-LAB where IND_UP may be sent before
            # establishing a WebSocket connection
            logging.info('No IND_UP from {0}'.format(self.id))

    def wait_until_status(self, target_node_status):
        # we assume we have a thread working to change the node status
        while self.status != target_node_status:
            time.sleep(self.STATUS_POLLING_INTERVAL)

    def start_tx(self, channel, trans_ctr):
        assert not self.current_channel
        assert not self.current_trans_ctr
        self.current_channel = channel
        self.current_trans_ctr = trans_ctr
        self.current_tx_mac_addr = self.mac_addr.value

        done = False
        retry_count = 0
        while (not done) and (retry_count <= self.MAX_REQUEST_RETRIES):
            if retry_count > 0:
                logging.info('Retry REQ_TX to {0}'.format(self.id))
            result = self._issue_command(self._send_req_tx,
                                         self._recv_resp_tx,
                                         retry=False)
            if result and (result[0] == MsgType.RESP_TX):
                # we may receive RESP_ST for a retried REQ_ST sent
                # before REQ_TX
                self.status = NodeStatus.TX
                done = True
            else:
                # no RESP_TX is received in time; check status
                result = self._issue_command(self._send_req_st,
                                             self._recv_resp_tx)
                if result:
                    if result[0] == MsgType.RESP_TX:
                        # receive a delayed RESP_TX
                        self.status = NodeStatus.TX
                        done = True
                    elif result[0] == MsgType.IND_TXDONE:
                        # RESP_TX was dropped for some reason; but we
                        # receive an IND_TXDONE, which means the
                        # node's status is TX
                        self.status = NodeStatus.TX
                        done = True
                    else:
                        # RESP_TX was dropped for some reason; but we
                        # receive a RESP_ST
                        assert result[0] == MsgType.RESP_ST
                        if result[1] == NodeStatus.TX:
                            # it's in TX
                            self.status = NodeStatus.TX
                            done = True
                        else:
                            # retry REQ_TX
                            retry_count += 1
                else:
                    err_str = ('Node {0} doesn\'t respond '.format(self.id)
                               + 'to REQ_ST')
                    logging.critical(err_Str)
                    raise RuntimeError(err_str)
        if done:
            # REQ_TX succeeds
            pass
        else:
            err_str = ('Node {0} doesn\'t respond '.format(self.id)
                       + 'to REQ_TX')
            logging.critical(err_str)
            raise RuntimeError(err_str)

    def wait_tx_done (self):
        # a set of transmissions takes (tx_num_pk * tx_ifdur_ms) at
        # least
        logging.info('Wait for IND_TXDONE from {0}'.format(self.id))
        wait_time_seconds = self.tx_num_pk * self.tx_ifdur_ms / 1000
        time.sleep(wait_time_seconds)

        # we may receive RESP_ST, which was sent in start_tx()
        done = False
        while not done:
            msg = self._recv_msg()
            if msg:
                if msg[0] == MsgType.IND_TXDONE:
                    done = True
                elif msg[0] == MsgType.RESP_ST:
                    # we expect IND_TXDONE is come after; continue
                    # receiving
                    logging.info('Ignore RESP_ST from {0}'.format(self.id))
                    pass
                else:
                    err_str = ('Unexpected MsgType '
                               + '{0} '.format(MsgType(msg[0]).name)
                               + 'from {0}'.format(self.id))
                    # shouldn't happen
                    logging.critical(err_str)
                    raise RuntimeError(err_str)
            else:
                # IND_TXDONE seems to have been dropped for some
                # reason... let's forget that response
                logging.error('IND_TXDONE from {0} '.format(self.id)
                              + 'may be dropped')
                done = True

        self.request_idle()
        self.current_channel = None
        self.current_trans_ctr = None
        self.current_tx_mac_addr = None

    def start_rx(self, channel, src_mac, trans_ctr):
        assert not self.current_channel
        assert not self.current_trans_ctr
        assert not self.current_tx_mac_addr
        self.current_channel = channel
        self.current_trans_ctr = trans_ctr
        self.current_tx_mac_addr = src_mac.value

        result = self._issue_command(self._send_req_rx, self._recv_resp_rx)
        if result:
            assert result[0] is True
            # change the node state to RX
            self.status = NodeStatus.RX
        else:
            err_str = ('Node {0} doesn\'t respond '.format(self.id)
                       + 'to REQ_RX')
            logging.critical(err_str)
            raise RuntimeError(err_str)

        # start receiving IND_RX
        thread = threading.Thread(target=self._keep_receiving,
                                  args=(channel, src_mac, trans_ctr))
        thread.start()
        self.keep_receiving_thread = thread

    def stop_rx(self):
        self.status = NodeStatus.STOPPING_RX
        self.keep_receiving_thread.join()
        self.keep_receiving_thread = None
        self.request_idle()

        assert self.status == NodeStatus.IDLE

        self.current_channel = None
        self.current_trans_ctr = None
        self.current_tx_mac_addr = None

    def _setup(self):
        pass

    def _am_i_tx_node(self, tx_nodes):
        raise NotImplementedError()

    def _issue_command(self, send_req, recv_resp, retry=True):
        err = []
        result = []

        def _proces_req_and_resp():
            retry_count = 0
            done = False
            while not done:
                if ((retry_count > 0) and
                    (retry_count <= self.MAX_REQUEST_RETRIES)):
                    logging.info('Retry {0} to {1}'.format(req_type.name,
                                                           self.id))
                elif retry_count > self.MAX_REQUEST_RETRIES:
                    err_str = ('Node {0} doesn\'t '.format(self.id)
                               + 'respond to {0}'.format(req_type.name))
                    logging.critical(err_str)
                    err.append(RuntimeError(err_str))
                    done = True
                    continue
                else:
                    assert retry_count == 0

                try:
                    req_type = send_req()
                    msg = self._recv_msg()

                    while msg:
                        return_values = recv_resp(msg)
                        if return_values:
                            break
                        else:
                            # check if we have another msg in the buffer
                            resp_type = MsgType(msg[0])
                            logging.info('Ignore {0} '.format(resp_type.name)
                                         + 'from {0}'.format(self.id))
                            msg = self._recv_msg()

                    if msg:
                        assert return_values
                        # the request is successfully processed by the node
                        result.extend(return_values)
                        done = True
                    elif retry:
                        # no response from the node in time; try it again
                        assert not msg
                        retry_count += 1
                    else:
                        # we didn't receive a response in time; but don't
                        # retry
                        assert not msg
                        done = True
                except Exception as e:
                    err.append(e)
                    done = True

        thread = threading.Thread(target=_proces_req_and_resp)
        thread.start()
        thread.join()
        if err:
            raise err.pop()
        return tuple(result)


    def _send_req_st(self):
        req = struct.pack('>B', MsgType.REQ_ST)
        self._send_msg(req)
        return MsgType.REQ_ST

    def _recv_resp_st(self, msg):
        assert msg
        if msg[0] == MsgType.RESP_ST:
            _, status, _, mac_addr = struct.unpack('>BBHQ', msg)
            return NodeStatus(status), netaddr.EUI(mac_addr)
        else:
            return None

    def _send_req_idle(self):
        req = struct.pack('>B', MsgType.REQ_IDLE)
        self._send_msg(req)
        return MsgType.REQ_IDLE

    def _recv_resp_idle(self, msg):
        if msg[0] == MsgType.RESP_IDLE:
            return [True]
        else:
            return None

    def _send_req_tx(self):
        req = struct.pack('>BBbHHHBB',
                          MsgType.REQ_TX,
                          self.current_channel,
                          self.tx_power_dbm,
                          self.current_trans_ctr,
                          self.tx_num_pk,
                          self.tx_ifdur_ms,
                          self.tx_len,
                          self.tx_fill_byte)
        self._send_msg(req)
        return MsgType.REQ_TX

    def _recv_resp_tx(self, msg):
        assert msg
        msg_type = MsgType(msg[0])
        # RESP_ST and IND_TX could be received during a REQ_TX process
        if msg_type in [MsgType.RESP_TX, MsgType.IND_TXDONE]:
            return [msg_type]
        elif msg_type == MsgType.RESP_ST:
            node_status, _ = self._recv_resp_st(msg)
            return [MsgType.RESP_ST, node_status]
        else:
            return None

    def _send_req_rx(self):
        req = struct.pack('>BBQHBB',
                          MsgType.REQ_RX,
                          self.current_channel,
                          self.current_tx_mac_addr,
                          self.current_trans_ctr,
                          self.tx_len,
                          self.tx_fill_byte)
        self._send_msg(req)
        return MsgType.REQ_RX

    def _recv_resp_rx(self, msg):
        assert msg
        if msg[0] == MsgType.RESP_RX:
            self.status = NodeStatus.RX
            return [True]
        else:
            return None

    def _recv_ind_rx(self, msg):
        assert msg
        msg_type = MsgType(msg[0])
        if msg_type in [MsgType.RESP_RX, MsgType.RESP_IDLE]:
            # we can ignore RESP_RX, which can be seen if we retried
            # REQ_RX. RESP_IDLE should be received at the end of a
            # measurement
            return [msg_type]
        elif msg_type == MsgType.IND_RX:
            _, length, rssi, flags, pkctr = (struct.unpack('>BBbBH', msg))
            return [msg_type, length, rssi, flags, pkctr]
        else:
            err_str = ('Unexpected MsgType {0} '.format(msg_type.name)
                       + 'from {0}'.format(self.id))
            logging.critical(err_str)
            raise RuntimeError(err_str)

    def _send_msg(self, msg):
        crc = hdlc_calc_crc(msg)
        hdlc_frame = HDLC_FLAG + hdlc_escape(msg+crc) + HDLC_FLAG
        logging.info('Send {0} to {1}'.format(MsgType(msg[0]).name,
                                              self.id))
        logging.debug('Request HDLC frame to {0}: '.format(self.id)
                      + '{0}'.format(hdlc_frame.hex()))
        self._platform_send(hdlc_frame)

    def _recv_msg(self):
        if self.serial_leftover:
            assert self.serial_leftover.startswith(HDLC_FLAG)
            serial_bytes = self.serial_leftover
            hdlc_frame_end_index = serial_bytes.find(HDLC_FLAG, 1)
            self.serial_leftover = b''
        else:
            serial_bytes = b''
            hdlc_frame_end_index = -1

        # recv() until we have a complete message which should be
        # surrounded by HDLC_FLAG, and larger than 2 bytes
        while hdlc_frame_end_index == -1:
            chunk = self._platform_recv()

            if chunk:
                logging.debug('Recv serial bytes from {0}: '.format(self.id)
                              + '{0}'.format(chunk.hex()))
                if serial_bytes or chunk.startswith(HDLC_FLAG):
                    serial_bytes += chunk
                    garbage = b''
                elif chunk.find(HDLC_FLAG) == -1:
                    # no HDLC_FLAG is found
                    garbage = serial_bytes
                else:
                    # found at least one HDLC_FLAG in chunk
                    hdlc_flag_index = chunk.find(HDLC_FLAG)
                    garbage = chunk[:hdlc_flag_index]
                    serial_bytes += chunk[hdlc_flag_index:]

                if garbage:
                    # garbage; recv() again
                    logging.error('Discard chunk from '
                                  + '{0} '.format(self.id)
                                  + 'since it seems garbage: '
                                  + '{0}'.format(chunk.hex()))

                if serial_bytes.find(HDLC_FLAG+HDLC_FLAG) == -1:
                    # do nothing
                    pass
                else:
                    # if we have two HDLC_FLAG side by side, remove
                    # one of them
                    serial_bytes = serial_bytes.replace(HDLC_FLAG+HDLC_FLAG,
                                                        HDLC_FLAG)
            else:
                # no data is received
                self.serial_leftover = serial_bytes
                serial_bytes = b''
                break

            assert serial_bytes.startswith(HDLC_FLAG)
            hdlc_frame_end_index = serial_bytes.find(HDLC_FLAG, 1)

        # returning only a complete message; the rest is set to
        # serial_leftover
        if serial_bytes:
            assert hdlc_frame_end_index > 0
            # we will use the end of HDLC_FLAG as the start of a next
            # frame
            next_hdlc_frame_start_index = hdlc_frame_end_index
            assert next_hdlc_frame_start_index <= len(serial_bytes)
            self.serial_leftover = (
                serial_bytes[next_hdlc_frame_start_index:]
            )
            hdlc_frame = serial_bytes[:next_hdlc_frame_start_index]
            if self.serial_leftover.startswith(HDLC_FLAG):
                _start_index = 0
                garbage = b''  # nothing
            else:
                # we have garbage in serial_leftover
                _start_index = self.serial_leftover.find(HDLC_FLAG)
                assert _start_index != 0

                if _start_index == -1:
                    garbage = self.serial_leftover
                else:
                    garbage = self.serial_leftover[:_start_index]
                    self.serial_leftover = self.serial_leftover[_start_index:]
                    logging.debug('Keep incomplete HDLC frames from '
                                  + '{0}, '.format(self.id)
                                  + '{0} '.format(len(self.serial_leftover))
                                  + 'bytes')
                if garbage:
                    logging.error('Discard serial bytes from '
                                  + '{0} '.format(self.id)
                                  + 'since it seems garbage: '
                                  + '{0}'.format(garbage.hex()))
        else:
            hdlc_frame = b''  # an empty HDLC frame

        # retrieve a Mercator message in the HDLC frame
        if hdlc_frame:
            assert hdlc_frame.startswith(HDLC_FLAG)
            assert not hdlc_frame.endswith(HDLC_FLAG)
            if self.platform.firmware_os_name == OSName.OpenWSN:
                hdlc_frame = restore_xon_xoff(hdlc_frame)
            logging.debug('Recv HDLC frame(s) from {0}: '.format(self.id)
                          + '{0}'.format(hdlc_frame.hex()))
            hdlc_body = hdlc_frame[1:]
            hdlc_body = hdlc_unescape(hdlc_body)
            if len(hdlc_body) < HDLC_MIN_BODY_LEN:
                # invalid length
                msg = b''
            if hdlc_verify_crc(hdlc_body):
                assert len(hdlc_body) > 2
                msg = hdlc_body[:-2]  # remove CRC
            else:
                msg = b''

            if msg:
                msg_type = MsgType(msg[0])
                if msg_type == MsgType.IND_RX:
                    # we don't want to log a reception of IND_RX,
                    # which will be overwhelming
                    pass
                else:
                    assert msg
                    logging.info('Recv {0} from {1}'.format(msg_type.name,
                                                            self.id))
        else:
            msg = b''  # an empty msg

        return msg

    def _platform_send(self, msg):
        raise NotImplementedError()

    def _platform_recv(self):
        raise NotImplementedError()

    def _keep_receiving(self, channel, src_mac, trans_ctr):
        msg = bytearray()
        prev_pkctr = -1
        self.rssi_records = [None] * self.tx_num_pk
        while self.status == NodeStatus.RX:
            msg = self._recv_msg()
            while msg:
                result = self._recv_ind_rx(msg)
                if result[0] == MsgType.IND_RX:
                    length, rssi, flags, pkctr = result[1:]
                    logging.debug('Recv IND_RX from {0}: '.format(self.id)
                                  + 'pkctr {0}, rssi {1}'.format(pkctr, rssi))
                    assert length == self.tx_len
                    assert flags == RxFlag.EXPECTED_FLAGS
                    prev_pkctr = self._store_rx_record(rssi, pkctr, prev_pkctr)
                elif result[0] == MsgType.RESP_RX:
                    logging.info('Ignore RESP_RX from {0}'.format(self.id))
                elif result[0] == MsgType.RESP_IDLE:
                    # end of this measurement
                    logging.info('Recv RESP_IDLE from {0}'.format(self.id))
                    self.status = NodeStatus.IDLE
                else:
                    logging.critical('Recv {0} '.format(MsgType(msg_type).name)
                                     + 'from {0}, '.format(self.id)
                                     + 'which is not expected')
                    assert False
                msg = self._recv_msg()


    def _store_rx_record(self, rssi, pkctr, prev_pkctr):
        if pkctr == prev_pkctr:
            logging.error('Node {0} '.format(self.id)
                          + 'received a duplicate packet '
                          + '(pkctr:{0})'.format(pkctr))
        elif pkctr > prev_pkctr:
            assert prev_pkctr < pkctr

            self.rssi_records[pkctr] = rssi
        else:
            logging.critical('Recv IND_RX from {0} '.format(self.id)
                             + 'having pkctr {0} '.format(pkctr)
                             + '< prev_pkctr {0}'.format(prev_pkctr))
            assert False

        return pkctr
