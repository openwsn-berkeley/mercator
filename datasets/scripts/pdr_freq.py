#!/usr/bin/python

#============================== description ===================================

# This script generates a new dataset with:
#   X: the 16 channels
#   Y: the PDR
#
# The generated files are located:
#   inside processed/site/pdr_freq/emitter.csv

# the format is csv (16 lines):
#   frequency,pdr

#=============================== imports ======================================

import os
import argparse
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
        grouped = df_emitter.groupby(df_emitter["frequency"])
        rx_count = grouped.size()
        frequencies = grouped.size().index
        ser = pd.Series(rx_count*100/((dtsh.node_count-1)*dtsh.tx_count), frequencies)
        result = ser.to_frame(name="pdr")

        # write result

        result.to_csv("{0}/{1}/pdr_freq/one_to_many/{2}.csv".format(OUT_PATH, dtsh.testbed, emitter))


def one_to_one(df, dtsh):

    # get emitter list

    list_emitters = df["srcmac"].drop_duplicates().tolist()

    # compute result

    for emitter in list_emitters:
        df_emitter = df[df.srcmac == emitter]
        group_rcv = df_emitter.groupby(df_emitter["mac"])

        for receiver,df_receiver in group_rcv:
            group_freq = df_receiver.groupby(df_receiver["frequency"])
            rx_count = group_freq.size()
            frequencies = group_freq.size().index
            ser = pd.Series(rx_count * 100 / ((dtsh.node_count - 1) * dtsh.tx_count), frequencies)
            result = ser.to_frame(name="pdr")

            # write result

            path = "{0}/{1}/pdr_freq/one_to_one/{2}/".format(OUT_PATH, dtsh.testbed, emitter)
            if not os.path.exists(path):
                os.makedirs(path)
            result.to_csv(path+"{0}.csv".format(receiver))

if __name__ == '__main__':
    main()
