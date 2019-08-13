import enum
import gzip
import json
import logging
import os
import sys

from colored import attr, fg, stylize
from halo import Halo

# from openwsn-fw/bsp/boards/uart.h
UART_XON = b'\x11'
UART_XON_ESCAPED = b'\x01'
UART_XOFF = b'\x13'
UART_XOFF_ESCAPED = b'\x03'
UART_ESCAPE = b'\x12'
UART_ESCAPE_ESCAPED = b'\x02'

class OSName(enum.Enum):
    # concrete values (string) should be in lowercase
    OpenWSN = 'openwsn'

def escape_xon_xoff(message):
    # This function is not used now since OpenWSN doesn't expect a
    # received serial message is escaped (see uart_readByte() in
    # openwsn-fw/bsp/boards/uart.c)
    ret = bytearray(message)
    ret = ret.replace(UART_XON,
                      UART_ESCAPE+UART_XON_ESCAPED)
    ret = ret.replace(UART_XOFF,
                      UART_ESCAPE+UART_XOFF_ESCAPED)
    ret = ret.replace(UART_ESCAPE,
                      UART_ESCAPE+UART_ESCAPE_ESCAPED)
    return ret

def restore_xon_xoff(message):
    ret = bytearray(message)
    ret = ret.replace(UART_ESCAPE+UART_XON_ESCAPED,
                      UART_XON)
    ret = ret.replace(UART_ESCAPE+UART_XOFF_ESCAPED,
                      UART_XOFF)
    ret = ret.replace(UART_ESCAPE+UART_ESCAPE_ESCAPED,
                      UART_ESCAPE)
    return ret

class MercatorHalo(Halo):
    enabled = True

    def __init__(self, text='', color='cyan', text_color=None, spinner=None,
                 animation=None, placement='left', interval=-1,
                 stream=sys.stdout):
        super(MercatorHalo, self).__init__(text, color, text_color, spinner,
                                           animation, placement, interval,
                                           self.enabled, stream)
        self.start()

    @classmethod
    def disable(cls):
        cls.enabled = False

    def stop_success(self, text=None):
        self.succeed(text)
        self.stop()

    def stop_failure(self, text=None):
        self.fail(text)
        self.stop()

def print_bold(message):
    bold_message = stylize(message, attr('bold'))
    print(bold_message)

class Outfile(object):
    def __init__(self, out_file_path, config, overwrite_out_file):
        if not out_file_path.endswith('jsonl.gz'):
            raise ValueError('Filename must end with "jsonl.gz"')
        elif os.path.exists(out_file_path):
            if overwrite_out_file:
                print_bold('{0} will be overwritten'.format(out_file_path))
            else:
                raise ValueError('{0} already exists'.format(out_file_path))

        self.fp = None
        self.out_file_path = out_file_path
        self.config = config

    def open(self):
        self.fp = gzip.open(self.out_file_path, 'wt')
        logging.info('Outfile {0} is opened'.format(self.out_file_path))
        self.write_data('config', self.config)

    def write_data(self, data_type, data):
        json_line = json.dumps({'data_type': data_type, 'data': data})
        self.fp.write(json_line + '\n')

    def close(self):
        self.fp.close()

    def flush(self):
        self.fp.flush()
