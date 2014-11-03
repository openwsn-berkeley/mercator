This folder contains:

* a raw dataset file per experiment, of the format `<site>-<timestamp>_raw.csv`.
* a pre-processed dataset directory per experiment, of the format `<site>-<timestamp>/`.
* `datasets.csv`, which lists the dataset files.
* `preprocess.py` which preprocesses the data by
    * generating a `<site>-<timestamp>/` folder for each `<site>-<timestamp>_raw.csv` file.
    * generating a `datasets.csv`.

Each raw dataset file corresponds to one experiment. In an experiment, each mote sends packets while all the others listen. The experiment is driven is such a way that only one motes sends at a given time, and that all the other motes listen to the same channel. A record (line) is written each time a mote receives a packet.

A raw dataset file is a CSV file with the following columns:

column name  | description
-------------|------------
`timestamp`  | Time at which this record was written to the file, in UTC, of the form `YYYY.MM.DD_hh.mm.ss`. Note that this time is _approximate_ only (e.g. buffering delays), and cannot be used to calculate inter-packet durations.
`mac`        | 8-byte MAC address of the mote reporting this record, i.e. the mote which has received the wireless packet. The MAC address is written as hexadecimal bytes separated by `-`. Example:`14-15-92-00-00-12-34-56`.
`frequency`  | Frequency channel the packet was received on, in IEEE notation (`11` for 2.405GHz, `26` for 2.480GHz).
`txpower`    | Transmission power setting of the transmitter, in dBm.
`length`     | Length, in bytes, of the received packet.
`rssi`       | Received signal strength of the packet, in dBm.
`crc`        | `1` if the packet was received with a good CRC, `0` otherwise.
`expected`   | `1` if the packet is expected, `0` otherwise.
`srcmac`     | 8-byte MAC address of the mote sending the received packets, as read from the packet. Set to all `0`'s if `crc` or `expected` is `0`.
`transctr`   | 1-byte transaction counter, read from the packet, in hexadecimal. Example: `0x01`. Set to all `0`'s if `crc` or `expected` is `0`.
`pkctr`      | 2-byte counter read from the packet, in hexadecimal. Example: `0x0123`. Set to all `0`'s if `crc` or `expected` is `0`.
`txnumpk`    | Number of packets the transmitter is configured to transmit.
`txifdur`    | Number of millisecond the transmitter is configured to wait between the beginning of each packet.
`txlength`   | Length, in bytes, of each transmitted packet.
`txfillbyte` | Byte the transmitter uses to fill the packet, in hexadecimal. Example: `0x0a`.
