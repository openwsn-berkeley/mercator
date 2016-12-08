#=== type

TYPE_REQ_ST        = 1
TYPE_RESP_ST       = 2
TYPE_REQ_IDLE      = 3
TYPE_REQ_TX        = 4
TYPE_IND_TXDONE    = 5
TYPE_REQ_RX        = 6
TYPE_IND_RX        = 7
TYPE_IND_UP        = 8
TYPE_ALL = [
    TYPE_REQ_ST,
    TYPE_RESP_ST,
    TYPE_REQ_IDLE,
    TYPE_REQ_TX,
    TYPE_IND_TXDONE,
    TYPE_REQ_RX,
    TYPE_IND_RX,
    TYPE_IND_UP
]


def type_num2text(num):
    if   num == TYPE_REQ_ST:
        returnval = 'REQ_ST'
    elif num == TYPE_RESP_ST:
        returnval = 'RESP_ST'
    elif num == TYPE_REQ_IDLE:
        returnval = 'REQ_IDLE'
    elif num == TYPE_REQ_TX:
        returnval = 'REQ_TX'
    elif num == TYPE_IND_TXDONE:
        returnval = 'IND_TXDONE'
    elif num == TYPE_REQ_RX:
        returnval = 'REQ_RX'
    elif num == TYPE_IND_RX:
        returnval = 'IND_RX'
    elif num == TYPE_IND_UP:
        returnval = 'IND_UP'
    else:
        returnval = '<unknown>'
    return returnval

#=== status

ST_IDLE            = 1
ST_TX              = 2
ST_TXDONE          = 3
ST_RX              = 4
ST_ALL = [
    ST_IDLE,
    ST_TX,
    ST_TXDONE,
    ST_RX,
]


def status_num2text(num):
    if   num == ST_IDLE:
        returnval = 'IDLE'
    elif num == ST_TX:
        returnval = 'TX'
    elif num == ST_TXDONE:
        returnval = 'TXDONE'
    elif num == ST_RX:
        returnval = 'RX'
    else:
        returnval = '<unknown>'
    return returnval

#=== helper


def format_mac(mac):
    return '-'.join(['%02x' % b for b in mac])
