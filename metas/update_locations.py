# This file uses the experiment-cli tool to genrate the IoTLab motes locations.
# Refere to the Mercator wiki to use it.
# https://github.com/openwsn-berkeley/mercator/wiki

#-----------------------------------------------------------------------------#

import os
import json
import csv

#-----------------------------------------------------------------------------#

site_list = ["strasbourg"]

for site in site_list:
    os.system("experiment-cli info -l --site {0} > tmp.json".format(site))
    jout = ""
    with open('tmp.json') as data_file:
        jout = json.load(data_file)
    os.remove("tmp.json")

    # get motes eui64

    mac_list = []
    path = "{0}_eui64.csv".format(site)
    if os.path.isfile(path):
        with open(path, 'r') as f:
            reader = csv.reader(f)
            mac_list = list(reader)

    # parse results

    results = []
    for mote in jout["items"]:
        if mote["state"] == "Alive" and mote["mobile"] == 0:
            # remove useless fields
            del mote["mobile"]
            del mote["mobility_type"]
            del mote["site"]
            del mote["uid"]

            # get mote eui64
            hostname = mote["network_address"].split(".")[0]
            for mac in mac_list:
                if hostname == mac[1]:
                    mote["mac"] = mac[0]
                    break

            # add mote to site
            res_mote = mote
            results.append(res_mote)

    # write out

    with open('{0}.json'.format(site), 'w') as fp:
        json.dump(results, fp, indent=4)

#-----------------------------------------------------------------------------#
