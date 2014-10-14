TYPE_REQ_ST        = 1
TYPE_RESP_ST       = 2
TYPE_REQ_IDLE      = 3
TYPE_REQ_TX        = 4
TYPE_IND_TXDONE    = 5
TYPE_REQ_RX        = 6 
TYPE_IND_RX        = 7
TYPE_ALL = [
    TYPE_REQ_ST,
    TYPE_RESP_ST,
    TYPE_REQ_IDLE,
    TYPE_REQ_TX,
    TYPE_IND_TXDONE,
    TYPE_REQ_RX,
    TYPE_IND_RX
]

STATUS = {
  1: "IDLE",
  2: "TX",
  3: "TXDONE",
  4: "RX"
}