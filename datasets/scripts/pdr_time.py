#!/usr/bin/python

#============================== description ===================================

# This script generates a new dataset with:
#   X: the time
#   Y: the PDR
#
# The generated files are located:
#   inside processed/<site>/pdr_time/one_to_one/emitter.csv
#   inside processed/<site>/pdr_time/one_to_many/emitter.csv

# the format is json:
#  TODO

#=============================== imports ======================================

import os
import argparse
import json
import pandas as pd

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
        df_emitter['timestamp'] = pd.to_datetime(df_emitter['timestamp'], format='%Y-%m-%d_%H.%M.%S')
        df_emitter.set_index('timestamp', inplace=True)
        for n, g in df_emitter.groupby(df_emitter["transctr"]):
            gg = g.groupby(pd.TimeGrouper(freq='3S'))
            rx_count = gg.size()
            #times = gg.size().index.tolist()
            times = gg.size().index.get_level_values('timestamp').strftime("%Y-%m-%d %H:%M:%S")
            #print rx_count
            #print times
            pdr = (rx_count * 100 / ((dtsh.node_count - 1) * dtsh.tx_count)).sum()
            print pdr



        # write result

        path = "{0}/{1}/pdr_time/one_to_many/".format(OUT_PATH, dtsh.testbed)
        if not os.path.exists(path):
            os.makedirs(path)
        json_data = {
              "x": map(str, times),
              "y": pdr,
              "xtitle": "Time",
              "ytitle": "PDR"
        }
        with open(path + "{0}.json".format(emitter), 'w') as output_file:
            json.dump(json_data, output_file)


def one_to_one(df, dtsh):

    # get emitter list

    list_emitters = df["srcmac"].drop_duplicates().tolist()

    # compute result

    for emitter in list_emitters:
        df_emitter = df[df.srcmac == emitter].copy()
        dtsh_emt = DatasetHelper(df_emitter)
        group_rcv = df_emitter.groupby(df_emitter["mac"])

        for receiver, df_receiver in group_rcv:
            group_freq = df_receiver.groupby(df_receiver["frequency"])
            rx_count = group_freq.size()
            frequencies = group_freq.size().index.tolist()
            pdr = (rx_count * 100 / dtsh_emt.tx_count).tolist()

            # write result

            path = "{0}/{1}/pdr_freq/one_to_one/{2}/".format(OUT_PATH, dtsh.testbed, emitter)
            if not os.path.exists(path):
                os.makedirs(path)
            json_data = {
                "x": map(str, frequencies),
                "y": pdr,
                "xtitle": "Channels",
                "ytitle": "PDR"
            }
            with open(path + "{0}.json".format(receiver), 'w') as output_file:
                json.dump(json_data, output_file)


if __name__ == '__main__':
    main()
