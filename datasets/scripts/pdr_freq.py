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
    parser.add_argument("emitter", help="The emitting node", type=str)
    args = parser.parse_args()

    # load the dataset

    df = pd.read_csv("{0}/{1}.csv".format(RAW_PATH, args.testbed))\

    # remove wrong values

    df.drop_duplicates(inplace=True)
    df = df[(df.crc == 1) & (df.expected == 1)]

    # get number of nodes and number of packet per transmission

    nbr_of_nodes = len(df.groupby(df["mac"]))
    nbr_of_pkts = df["txnumpk"].iloc[0]

    # compute result

    df_emitter = df[df.srcmac == args.emitter]
    grouped = df_emitter.groupby(df_emitter["frequency"])
    sizes = grouped.size()
    ser = pd.Series(sizes*100/((nbr_of_nodes-1)*nbr_of_pkts), sizes.index)
    result = ser.to_frame(name="pdr")

    # write result

    result.to_csv("{0}/{1}/{2}.csv".format(OUT_PATH, args.testbed, args.emitter))

if __name__ == '__main__':
    main()
