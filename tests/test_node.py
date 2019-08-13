import logging
import struct
import time
import types

import netaddr
import pytest

from mercator.hdlc import (hdlc_calc_crc, hdlc_verify_crc,
                           hdlc_escape, hdlc_unescape, HDLC_FLAG)
import mercator.node
from mercator.node import MsgType, NodeStatus, RxFlag
import mercator.platforms
from mercator.utils import OSName

TEST_MAC_ADDR = netaddr.EUI('02-01-03-04-05-06-07-08')
TEST_NODE_ID = 1
TEST_CHANNEL = 11
TEST_TX_LEN = 100
TEST_TRANS_CTR = 100
TEST_RSSI = -50

def _hdlcify(in_buf):
    crc = hdlc_calc_crc(in_buf)
    body = hdlc_escape(in_buf + crc)
    return HDLC_FLAG + body + HDLC_FLAG

def _dehdlcify(in_buf):
    body = in_buf[1:-1]
    assert hdlc_verify_crc(body)
    return hdlc_unescape(body[:-2])

class Platform(mercator.platforms.Platform):
    def __init__(self, config):
        self.firmware_os_name = OSName.OpenWSN

    def setup_measurement(self, config):
        pass

class Node(mercator.node.Node):
    def __init__(self, platform):
        super(Node, self).__init__(platform)
        self.id = TEST_NODE_ID
        self.sent_bytes = None
        self.test_recv_bytes = b''
        self.sent_count = 0
        self.retry_count = -1
        self.mac_addr = TEST_MAC_ADDR

    def get_sent_bytes(self):
        ret = self.sent_bytes
        self.sent_bytes = None
        return ret

    def put_test_recv_bytes(self, byte_str):
        self.test_recv_bytes += byte_str

    def set_retry_count(self, count):
        # return self.test_recv_bytes after _platform_send() is called
        # "retry_count+1" times
        self.retry_count = count

    def _platform_send(self, msg):
        self.sent_bytes = msg
        self.sent_count += 1

    def _platform_recv(self):
        if self.sent_count > self.retry_count:
            ret = self.test_recv_bytes
            self.test_recv_bytes = b''
        else:
            ret = b''
        return ret

@pytest.fixture
def node(caplog):
    caplog.set_level(logging.INFO)
    platform = Platform({})
    _node = Node(platform)

    # do some initialization which is done by setup()
    _node.tx_power_dbm = _node.DUMMY_TX_POWER_VALUE
    _node.tx_len = TEST_TX_LEN
    _node.tx_num_pk = 100
    _node.tx_ifdur_ms = 10
    _node.tx_fill_byte = 0x5a
    _node.rssi_records = [None] * _node.tx_num_pk
    _node._status = NodeStatus.IDLE

    return _node

@pytest.fixture
def resp_st():
    TEST_NUMNOTIFICATIONS = 0xabcd
    def _resp_st(status):
        numnotifications = TEST_NUMNOTIFICATIONS
        mac_addr = TEST_MAC_ADDR
        return struct.pack('>BBHQ',
                           MsgType.RESP_ST, status, numnotifications,
                           mac_addr.value)
    return _resp_st

@pytest.fixture
def resp_idle():
    return struct.pack('>B', MsgType.RESP_IDLE)

@pytest.fixture
def resp_tx():
    return struct.pack('>B', MsgType.RESP_TX)

@pytest.fixture
def resp_rx():
    return struct.pack('>B', MsgType.RESP_RX)

@pytest.fixture
def ind_up():
    return struct.pack('>B', MsgType.IND_UP)

@pytest.fixture
def ind_txdone():
    return struct.pack('>B', MsgType.IND_TXDONE)

@pytest.fixture
def ind_rx():
    def _ind_rx(pkctr):
        return struct.pack('>BBbBH',
                           MsgType.IND_RX,
                           TEST_TX_LEN,
                           TEST_RSSI,
                           RxFlag.EXPECTED_FLAGS,
                           pkctr)
    return _ind_rx

def test_request_status(caplog, node, resp_st):
    test_status = NodeStatus.IDLE
    node.put_test_recv_bytes(_hdlcify(resp_st(test_status)))

    status, mac_addr = node.request_status()
    sent_bytes = _dehdlcify(node.get_sent_bytes())
    assert status == test_status
    assert mac_addr == TEST_MAC_ADDR
    assert len(sent_bytes) == 1
    assert sent_bytes[0] == MsgType.REQ_ST

    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_ST from {0}'.format(TEST_NODE_ID)))

def test_request_status_having_ind_up(caplog, node, ind_up, resp_st):
    # put IND_UP before RESP_ST so that they are received at once
    test_status = NodeStatus.IDLE
    node.put_test_recv_bytes(_hdlcify(ind_up)
                             + _hdlcify(resp_st(test_status)))

    # even in this case, node should identify RESP_ST and process it
    # properly. IND_UP should be ignored
    status, mac_addr = node.request_status()
    assert status == test_status
    assert mac_addr == TEST_MAC_ADDR

    assert len(caplog.record_tuples) == 4
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv IND_UP from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Ignore IND_UP from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[3]
            == ('root',
                logging.INFO,
                'Recv RESP_ST from {0}'.format(TEST_NODE_ID)))

def test_request_status_duplicate_response(caplog, node, resp_st):
    # put two RESP_ST
    test_status_1 = NodeStatus.RX
    test_status_2 = NodeStatus.IDLE
    node.put_test_recv_bytes(_hdlcify(resp_st(test_status_1))
                             + _hdlcify(resp_st(test_status_2)))

    status, mac_addr = node.request_status()
    assert status == test_status_1
    assert mac_addr == TEST_MAC_ADDR

    # in this case, the second RESP_ST should not be processed. the
    # second RESP_ST should be kept in serial_leftover
    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_ST from {0}'.format(TEST_NODE_ID)))
    assert node.serial_leftover == _hdlcify(resp_st(test_status_2))

def test_request_status_with_retries(caplog, node, resp_st):
    retry_count = 1
    test_status = NodeStatus.IDLE
    node.put_test_recv_bytes(_hdlcify(resp_st(test_status)))
    node.set_retry_count(retry_count)

    status, mac_addr = node.request_status()
    assert status == test_status
    assert mac_addr == TEST_MAC_ADDR

    # we should have one retry
    assert len(caplog.record_tuples) == 4
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Retry REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Send REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[3]
            == ('root',
                logging.INFO,
                'Recv RESP_ST from {0}'.format(TEST_NODE_ID)))

def test_request_status_timeout(caplog, node):
    with pytest.raises(RuntimeError):
        status, mac_addr = node.request_status()

    # we should have one more 'Send' log than 'Retry'; and at the end,
    # we should have CRITICAL log
    assert len(caplog.record_tuples) == node.MAX_REQUEST_RETRIES * 2 + 1 + 1
    assert (caplog.record_tuples[-1] ==
            ('root',
             logging.CRITICAL,
             'Node {0} doesn\'t respond to REQ_ST'.format(TEST_NODE_ID)))

def test_request_idle(caplog, node, resp_idle):
    node.status = NodeStatus.RX
    node.put_test_recv_bytes(_hdlcify(resp_idle))
    node.request_idle()

    assert node.status == NodeStatus.IDLE
    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_IDLE to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_IDLE from {0}'.format(TEST_NODE_ID)))

def test_request_idle_timeout(caplog, node, resp_idle):
    with pytest.raises(RuntimeError):
        node.request_idle()
    assert len(caplog.record_tuples) == node.MAX_REQUEST_RETRIES * 2 + 1 + 1
    assert (caplog.record_tuples[-1] ==
            ('root',
             logging.CRITICAL,
             'Node {0} doesn\'t respond to REQ_IDLE'.format(TEST_NODE_ID)))

def test_wait_ind_up(caplog, node, ind_up):
    node.put_test_recv_bytes(_hdlcify(ind_up))
    node.wait_ind_up()

    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Wait for IND_UP from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv IND_UP from {0}'.format(TEST_NODE_ID)))

def test_wait_ind_up_timeout(caplog, node, ind_up):
    node.wait_ind_up()

    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Wait for IND_UP from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'No IND_UP from {0}'.format(TEST_NODE_ID)))

def test_start_tx(caplog, node, resp_tx):
    node.put_test_recv_bytes(_hdlcify(resp_tx))
    node.start_tx(TEST_CHANNEL, TEST_TRANS_CTR)

    assert node.status == NodeStatus.TX
    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_TX to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_TX from {0}'.format(TEST_NODE_ID)))

def test_start_tx_having_ind_txdone(caplog, node, resp_tx, ind_txdone):
    # IND_TXDONE may follow RESP_TX especially when using opentestbed
    node.put_test_recv_bytes(_hdlcify(resp_tx)
                             +_hdlcify(ind_txdone))
    node.start_tx(TEST_CHANNEL, TEST_TRANS_CTR)

    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_TX to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_TX from {0}'.format(TEST_NODE_ID)))

    # IND_TXDONE should be ignored and saved in serial_leftover
    assert node.serial_leftover == _hdlcify(ind_txdone)

def test_start_tx_timeout(caplog, node, resp_st):
    def _platform_recv(self):
        if not hasattr(self, 'req_count'):
            self.req_count = 1
        else:
            self.req_count += 1
        if self.req_count % 2:  # odd, RESP_TX is expected
            return b''  # return nothing
        else:
            return _hdlcify(resp_st(NodeStatus.IDLE))

    node._platform_recv = types.MethodType(_platform_recv, node)
    with pytest.raises(RuntimeError):
        node.start_tx(TEST_CHANNEL, TEST_TRANS_CTR)
    assert len(caplog.record_tuples) == (
        (node.MAX_REQUEST_RETRIES + 1)       # REQ_TX
        + (node.MAX_REQUEST_RETRIES + 1) * 2 # REQ_ST + RESP_ST
        + node.MAX_REQUEST_RETRIES           # Retry log
        + 1                                  # error log
    )
    assert (caplog.record_tuples[-1] ==
            ('root',
             logging.CRITICAL,
             'Node {0} doesn\'t respond to REQ_TX'.format(TEST_NODE_ID)))

def test_start_tx_delayed_resp_tx(caplog, node, resp_tx, resp_st):
    def _platform_recv(self):
        if not hasattr(self, 'req_count'):
            self.req_count = 1
        else:
            self.req_count += 1
        if self.req_count == 1:
            # return nothing for the first REQ_TX
            return b''
        elif self.req_count == 2:
            return _hdlcify(resp_tx)
        else:
            assert False # shouldn't come

    node._platform_recv = types.MethodType(_platform_recv, node)
    node.start_tx(TEST_CHANNEL, TEST_TRANS_CTR)
    assert len(caplog.record_tuples) == 3
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_TX to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Send REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Recv RESP_TX from {0}'.format(TEST_NODE_ID)))

def test_start_tx_recv_ind_txdone(caplog, node, ind_txdone):
    def _platform_recv(self):
        if not hasattr(self, 'req_count'):
            self.req_count = 1
        else:
            self.req_count += 1
        if self.req_count == 1:
            # return nothing for the first REQ_TX
            return b''
        elif self.req_count == 2:
            return _hdlcify(ind_txdone)
        else:
            assert False # shouldn't come

    node._platform_recv = types.MethodType(_platform_recv, node)
    node.start_tx(TEST_CHANNEL, TEST_TRANS_CTR)
    assert len(caplog.record_tuples) == 3
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_TX to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Send REQ_ST to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Recv IND_TXDONE from {0}'.format(TEST_NODE_ID)))

def test_wait_tx_done(caplog, node, ind_txdone, resp_idle):
    node.status = NodeStatus.TX
    node.put_test_recv_bytes(_hdlcify(ind_txdone) + _hdlcify(resp_idle))
    node.wait_tx_done()
    assert node.status == NodeStatus.IDLE

    assert len(caplog.record_tuples) == 4
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Wait for IND_TXDONE from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv IND_TXDONE from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Send REQ_IDLE to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[3]
            == ('root',
                logging.INFO,
                'Recv RESP_IDLE from {0}'.format(TEST_NODE_ID)))

def test_wait_tx_done_resp_st(caplog, node, resp_st, ind_txdone, resp_idle):
    # RESP_TX may be followed by IND_TXDONE when REQ_TX is re-sent
    node.put_test_recv_bytes(_hdlcify(resp_st(NodeStatus.TX))
                             + _hdlcify(ind_txdone)
                             + _hdlcify(resp_idle))
    node.wait_tx_done()

    # RESP_TX should be ignored
    assert len(caplog.record_tuples) == 6
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Wait for IND_TXDONE from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_ST from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Ignore RESP_ST from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[3]
            == ('root',
                logging.INFO,
                'Recv IND_TXDONE from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[4]
            == ('root',
                logging.INFO,
                'Send REQ_IDLE to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[5]
            == ('root',
                logging.INFO,
                'Recv RESP_IDLE from {0}'.format(TEST_NODE_ID)))

def test_wait_tx_done_timeout(caplog, node, resp_idle):
    with pytest.raises(RuntimeError):
        node.wait_tx_done()
    assert len(caplog.record_tuples) == 10
    assert (caplog.record_tuples[0] ==
            ('root',
             logging.INFO,
             'Wait for IND_TXDONE from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1] ==
            ('root',
             logging.ERROR,
             'IND_TXDONE from {0} may be dropped'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[-1] ==
            ('root',
             logging.CRITICAL,
             'Node {0} doesn\'t respond to REQ_IDLE'.format(TEST_NODE_ID)))
    assert node.current_channel is None
    assert node.current_trans_ctr is None
    assert node.current_tx_mac_addr is None

def test_start_rx(caplog, node, resp_rx):
    node.put_test_recv_bytes(_hdlcify(resp_rx))
    node.start_rx(TEST_CHANNEL, TEST_MAC_ADDR, TEST_TRANS_CTR)
    assert node.status == NodeStatus.RX

    assert len(caplog.record_tuples) == 2
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_RX to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_RX from {0}'.format(TEST_NODE_ID)))

    # stop the thread directly
    node.status = NodeStatus.IDLE
    node.keep_receiving_thread.join()

def test_start_rx_done_duplicate_response(caplog, node, resp_rx):
    # two RESP_RX are received at once
    node.put_test_recv_bytes(_hdlcify(resp_rx)
                             + _hdlcify(resp_rx))
    node.start_rx(TEST_CHANNEL, TEST_MAC_ADDR, TEST_TRANS_CTR)
    # stop the thread directly
    node.status = NodeStatus.IDLE
    node.keep_receiving_thread.join()

    assert len(caplog.record_tuples) == 4
    assert (caplog.record_tuples[0]
            == ('root',
                logging.INFO,
                'Send REQ_RX to {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[1]
            == ('root',
                logging.INFO,
                'Recv RESP_RX from {0}'.format(TEST_NODE_ID)))
    # the second RESP_RX should be handled in _store_rx_records() and
    # ignored
    assert node.serial_leftover == HDLC_FLAG
    assert (caplog.record_tuples[2]
            == ('root',
                logging.INFO,
                'Recv RESP_RX from {0}'.format(TEST_NODE_ID)))
    assert (caplog.record_tuples[3]
            == ('root',
                logging.INFO,
                'Ignore RESP_RX from {0}'.format(TEST_NODE_ID)))

def test_start_rx_timeout(caplog, node):
    with pytest.raises(RuntimeError):
        node.start_rx(TEST_CHANNEL, TEST_MAC_ADDR, TEST_TRANS_CTR)
    assert len(caplog.record_tuples) == node.MAX_REQUEST_RETRIES * 2 + 1 + 1
    assert (caplog.record_tuples[-1] ==
            ('root',
             logging.CRITICAL,
             'Node {0} doesn\'t respond to REQ_RX'.format(TEST_NODE_ID)))

def test_recv_corrupt_resp_rx_1(caplog, node):
    # there are two HDLC frames of RESP_RX, but the first one has two
    # missing bytes: 0x3a and 0x7e
    test_bytes = b'\x7e\x0c\x14\x7e\x0c\x14\x3a\x7e'
    node.current_channel = TEST_CHANNEL
    node.current_trans_ctr = TEST_TRANS_CTR
    node.current_tx_mac_addr = TEST_MAC_ADDR

    caplog.set_level(logging.DEBUG)
    node.put_test_recv_bytes(test_bytes)
    result = node._issue_command(node._send_req_rx, node._recv_resp_rx,
                                 retry=False)
    # the first one is corrupted
    assert not result
    result = node._issue_command(node._send_req_rx, node._recv_resp_rx,
                                 retry=False)
    # the second one is fine
    assert result and result[0]

def test_recv_corrupt_resp_rx_2(caplog, node):
    # there are two HDLC frames of RESP_RX, but the first one doesn't
    # have the leading 0x7e (HDLC_FLAG)
    test_bytes = b'\x0c\x14\x3a\x7e\x7e\x0c\x14\x3a\x7e'
    node.current_channel = TEST_CHANNEL
    node.current_trans_ctr = TEST_TRANS_CTR
    node.current_tx_mac_addr = TEST_MAC_ADDR

    caplog.set_level(logging.DEBUG)
    node.put_test_recv_bytes(test_bytes)
    result = node._issue_command(node._send_req_rx, node._recv_resp_rx,
                                 retry=False)
    # the first part of the recv bytes is dropped in node._recv_msg()
    assert result and result[0]

def test_recv_corrupt_resp_rx_3(caplog, node):
    # there are two HDLC frames of RESP_RX, but the first one lost its
    # content, which is msg_type 0xc0
    test_bytes = b'\x7e\x14\x3a\x7e\x0c\x14\x3a\x7e'
    node.current_channel = TEST_CHANNEL
    node.current_trans_ctr = TEST_TRANS_CTR
    node.current_tx_mac_addr = TEST_MAC_ADDR

    caplog.set_level(logging.DEBUG)
    node.put_test_recv_bytes(test_bytes)
    result = node._issue_command(node._send_req_rx, node._recv_resp_rx,
                                 retry=False)
    # the first one is corrupted
    assert not result
    result = node._issue_command(node._send_req_rx, node._recv_resp_rx,
                                 retry=False)
    # the second one is fine
    assert result and result[0]

def test_keep_receiving(caplog, node, resp_rx, ind_rx, resp_idle):
    def _platform_recv_ind_rx(self):
        if self.get_sent_bytes():  # expect this is REQ_RX
            ret = _hdlcify(resp_rx)
        else:
            time.sleep(0.10)
            if hasattr(self, 'pkctr'):
                self.pkctr += 1
            else:
                self.pkctr = 0

            # this test should be done before pkctr goes beyond the
            # boundary
            assert self.pkctr < 2**16

            # incomplete rx_record which doesn't have msg_type
            rx_record = _hdlcify(ind_rx(self.pkctr))

            if self.pkctr == 0:
                ret = rx_record + HDLC_FLAG
            else:
                self.serial_leftover == HDLC_FLAG[0]
                ret = rx_record[1:] + HDLC_FLAG

        return ret

    def _platform_recv_empty(self):
        return b''

    caplog.set_level(logging.WARNING)
    node._platform_recv = types.MethodType(_platform_recv_ind_rx, node)
    node.start_rx(TEST_CHANNEL, TEST_MAC_ADDR, TEST_TRANS_CTR)
    assert node.status == NodeStatus.RX

    assert len(caplog.record_tuples) == 0
    caplog.set_level(logging.DEBUG)
    time.sleep(1)

    # stop the thread by changing the node's status to STOPPING_RX
    node.status = NodeStatus.STOPPING_RX
    time.sleep(1)
    # the thread should be still alive since it keeps receiving something
    assert node.keep_receiving_thread.is_alive()
    # make _platform_recv() return nothing
    node._platform_recv = types.MethodType(_platform_recv_empty, node)
    node.keep_receiving_thread.join()
    assert not node.keep_receiving_thread.is_alive()

def test_duplicate_ind_rx(caplog, node, ind_rx):
    test_pkctr = 2
    prev_pkctr = 1

    prev_pkctr = node._store_rx_record(TEST_RSSI, 2, prev_pkctr)
    assert prev_pkctr == 2
    assert len(caplog.record_tuples) == 0

    # duplicate
    assert node._store_rx_record(TEST_RSSI, 2, prev_pkctr) == 2
    assert len(caplog.record_tuples) == 1
    assert (caplog.record_tuples[0] ==
            ('root',
             logging.ERROR,
             'Node {0} received a duplicate packet '.format(TEST_NODE_ID)
             + '(pkctr:{0})'.format(test_pkctr)))

def test_stop_rx(caplog, node, resp_rx, resp_idle):
    node.put_test_recv_bytes(_hdlcify(resp_rx))
    node.start_rx(TEST_CHANNEL, TEST_MAC_ADDR, TEST_TRANS_CTR)

    def _platform_recv(self):
        if self.sent_bytes and (self.sent_bytes[1] == MsgType.REQ_IDLE):
            self.sent_bytes = b''
            return _hdlcify(resp_idle)
        else:
            self.sent_bytes = b''
            return b''
    node._platform_recv = types.MethodType(_platform_recv, node)
    node.stop_rx()
    assert node.status == NodeStatus.IDLE
    assert node.current_channel is None
    assert node.current_trans_ctr is None
    assert node.current_tx_mac_addr is None
