This folder contains:

* a raw dataset file per site, of the format `raw/<site>.csv`.
* a pre-processed dataset directory per site, of the format `processed/<site>/`.
* a set of scripts to pre-process the raw dataset.
  * the scripts generate pre-processed datasets under the `processed/` folder.
  * more detail on how to run the pre-process scripts on [the corresponding wiki page](https://github.com/openwsn-berkeley/mercator/wiki/Preprocess-a-dataset)

Each raw dataset file corresponds to one experiment. In an experiment, each mote sends packets while all the others listen. The experiment is driven is such a way that only one motes sends at a given time, and that all the other motes listen to the same channel. A record (line) is written each time a mote receives a packet.

## Raw dataset format

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

## Pre-processed dataset format

A pre-processed dataset file is a JSON file with the folloging fields:
```
  `x`      | a list of x coordinates
  `y`      | a list of y coordinates
  `xtitle` | the title of the x axis
  `ytitle` | the title of the y axis
```

Example:
```
{
  "x": ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"],
  "y": [-57.289855072463766, -57.16290322580645, -57.35322580645161, -57.998387096774195, -57.88244766505636, -57.45645161290322, -58.57419354838709, -59.19838709677419, -59.62258064516129, -59.748387096774195, -59.53225806451613, -59.58957654723127, -59.0258064516129, -58.59324758842444, -59.06774193548387, -59.174193548387095],
  "xtitle": "Frequencies",
  "ytitle": "RSSI average"}
```
