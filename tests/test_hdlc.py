import pytest

import mercator
from mercator.hdlc import (hdlc_calc_crc, hdlc_verify_crc,
                           hdlc_escape, hdlc_unescape,
                           HDLC_FLAG, HdlcException)

# test CRC values are calulated manually with
# https://github.com/meetanthony/crcphp using CRC-16/X-25

HDLC_FLAG = b'\x7e'

@pytest.fixture(params=[
    {'data': b'\x01',
     'escaped_data': b'\x01',
     'crc': b'\xf1\xe1'},
    {'data': b'\xde\xad\xbe\xef\xc0\xfe\xc0\x1a\xc0\xff\xee',
     'escaped_data': b'\xde\xad\xbe\xef\xc0\xfe\xc0\x1a\xc0\xff\xee',
     'crc': b'\x35\x3a'},
    {'data': b'\x7e\x7d',
     'escaped_data': b'\x7d\x5e\x7d\x5d',
     'crc': b'\xf1\xcd'}])
def vector(request):
    return request.param

def test_calc_crc(vector):
    assert hdlc_calc_crc(vector['data']) == vector['crc']

def test_verify_crc(vector):
    assert hdlc_verify_crc(vector['data']+vector['crc'])

def test_escape(vector):
    assert hdlc_escape(vector['data']) == vector['escaped_data']

def test_unescape(vector):
    assert hdlc_unescape(vector['escaped_data']) == vector['data']

@pytest.fixture(params=[hdlc_calc_crc, hdlc_verify_crc,
                        hdlc_escape, hdlc_unescape])
def hdlc_api(request):
    return request.param

def test_empty_input(hdlc_api):
    with pytest.raises(HdlcException):
        hdlc_api(b'')

def test_dehdlcify_short_frame():
    pass
    in_buf = HDLC_FLAG
    in_buf += b'\x01\x02'  # garbage byte
    in_buf += HDLC_FLAG

def test_dehdlcify_wrong_crc():
    pass
    data = b'\x01'
    wrong_crc = b'\xf1\xe2'
