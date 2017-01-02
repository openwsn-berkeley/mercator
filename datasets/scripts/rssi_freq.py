#!/usr/bin/python

#============================== description ===================================

# This script generates a new dataset with:
#   X: the 16 channels
#   Y: the PDR
#
# The generated files are located:
#   inside processed/site/pdr_freq/emitter.json

# the format is json:
# {"pdr":{"11":98.5714285714,"12":98.4126984127,...,"26":98.4126984127}}

#=============================== imports ======================================

import os
import argparse
import pandas as pd
import json

from DatasetHelper import DatasetHelper

#=============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../processed"

#=============================== main =========================================


def main():

    # parsing user arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("-o2o", "--one_to_one", help="The name of the testbed data to process", action="store_true")
    parser.add_argument("-e", "--emitter", help="The emitting node", type=str)
    args = parser.parse_args()

    # load the dataset

    df = pd.read_csv("{0}/{1}.csv".format(RAW_PATH, args.testbed))

    dtsh = DatasetHelper(df, args.testbed)

    if args.one_to_one:
        one_to_one(df, dtsh)
    else:
        one_to_many(df, dtsh, args.emitter)


def one_to_many(df, dtsh, emitter=None):

    # select emitters

    if emitter:
        list_emitters = emitter
    else:
        list_emitters = df["srcmac"].drop_duplicates().tolist()

    # compute result

    for emitter in list_emitters:
        df_emitter = df[df.srcmac == emitter]
        grouped = df_emitter.groupby(df_emitter["frequency"])
        frequencies = grouped.size().index.tolist()
        rx_count = grouped.size()
        sum_rssi = grouped.rssi.sum()
        avg_rssi = (sum_rssi / rx_count).values.tolist()

        # write result

        path = "{0}/{1}/rssi_freq/one_to_many/".format(OUT_PATH, dtsh.testbed)
        if not os.path.exists(path):
            os.makedirs(path)
        json_data = {
            "x": map(str, frequencies),
            "y": avg_rssi,
            "xtitle": "Channels",
            "ytitle": "RSSI Average (dBm)"
            }
        with open(path + "{0}.json".format(emitter), 'w') as output_file:
            json.dump(json_data, output_file)


def one_to_one(df, dtsh):

    # get emitter list

    list_emitters = df["srcmac"].drop_duplicates().tolist()

    # compute result

    for emitter in list_emitters:
        df_emitter = df[df.srcmac == emitter].copy()
        group_rcv = df_emitter.groupby(df_emitter["mac"])

        for receiver, df_receiver in group_rcv:
            group_freq = df_receiver.groupby(df_receiver["frequency"])
            rx_count = group_freq.size()
            frequencies = group_freq.size().index.tolist()
            sum_rssi = group_freq.rssi.sum()
            avg_rssi = (sum_rssi / rx_count).values.tolist()

            # write result

            path = "{0}/{1}/rssi_freq/one_to_one/{2}/".format(OUT_PATH, dtsh.testbed, emitter)
            if not os.path.exists(path):
                os.makedirs(path)
            json_data = {
                    "x": map(str,frequencies),
                    "y": avg_rssi,
                    "xtitle": "Channels",
                    "ytitle": "RSSI Average"
                    }
            with open(path+"{0}.json".format(receiver), 'w') as output_file:
                json.dump(json_data, output_file)

if __name__ == '__main__':
    main()
