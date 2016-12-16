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

import argparse
import pandas as pd

#=============================== defines ======================================

RAW_PATH = "../raw"
OUT_PATH = "../processed"

#=============================== main =========================================


def main():

    # parsing user arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("testbed", help="The name of the testbed data to process", type=str)
    parser.add_argument("-e", "--emitter", help="The emitting node", type=str)
    args = parser.parse_args()

    # load the dataset

    df = pd.read_csv("{0}/{1}.csv".format(RAW_PATH, args.testbed))

    # remove wrong values

    df.drop_duplicates(inplace=True)
    df = df[(df.crc == 1) & (df.expected == 1)]

    # get number of nodes and number of packet per transmission

    node_count = len(df.groupby(df["mac"]))
    tx_count = df["txnumpk"].iloc[0]

    # select emitters

    if args.emitter:
        list_emmitters = [args.emitter]
    else:
        list_emmitters = df["srcmac"].drop_duplicates().tolist()

    # compute result

    for emitter in list_emmitters:
        df_emitter = df[df.srcmac == emitter]
        grouped = df_emitter.groupby(df_emitter["frequency"])
        rx_count = grouped.size()
        frequencies = grouped.size().index
        ser = pd.Series(rx_count*100/((node_count-1)*tx_count), frequencies)
        result = ser.to_frame(name="pdr")

        # write result

        result.to_csv("{0}/{1}/pdr_freq/{2}.csv".format(OUT_PATH, args.testbed, emitter))

if __name__ == '__main__':
    main()
