#!/usr/bin/python

#============================== description ===================================

# This script generates a new dataset with:
#   X: the RSSI
#   Y: the PDR
#
# The generated file is located here:
#    processed/<site>/pdr_rssi/waterfall.json

# the format is json:
#  TODO

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
    args = parser.parse_args()

    # load the dataset

    df = pd.read_csv("{0}/{1}.csv".format(RAW_PATH, args.testbed))
    dtsh = DatasetHelper(df, args.testbed)

    # init results

    list_rssi = []
    list_pdr = []

    # compute PDR and average RSSI by transaction

    transaction = dtsh.data.groupby([dtsh.data["transctr"], dtsh.data["srcmac"]])
    for name, group in transaction:
        mean_rssi = group["rssi"].mean().tolist()
        rx_count = len(group)
        pdr = (rx_count * 100) / ((dtsh.node_count - 1) * dtsh.tx_count)
        list_pdr.append(pdr)
        list_rssi.append(mean_rssi)

    # write result

    path = "{0}/{1}/pdr_rssi/".format(OUT_PATH, dtsh.testbed)
    if not os.path.exists(path):
        os.makedirs(path)
    json_data = {
        "x": map(str, list_rssi),
        "y": list_pdr,
        "xtitle": "RSSI (dBm)",
        "ytitle": "PDR (%)"
    }

    with open(path + "waterfall.json", 'w') as output_file:
        json.dump(json_data, output_file)

if __name__ == '__main__':
    main()
