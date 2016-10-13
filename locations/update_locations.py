# This file uses the experiment-cli tool to genrate the IoTLab motes locations.
# Refere to the Mercator wiki to use it.
# https://github.com/openwsn-berkeley/mercator/wiki

#-----------------------------------------------------------------------------#

import os
import json

#-----------------------------------------------------------------------------#

# get IoTlab infos

os.system("experiment-cli info -l > tmp.json")
jout = ""
with open('tmp.json') as data_file:
    jout = json.load(data_file)
os.remove("tmp.json")

# parse results

results = {}
for mote in jout["items"]:
    if mote["state"] == "Alive":
        # create site if it does not exists
        if mote["site"] not in results.keys():
            results[mote["site"]] = []

        # add mote to site
        res_mote = {
            "network_address": mote["network_address"],
            "x": mote["x"],
            "y": mote["y"],
            "z": mote["z"],
            }
        results[mote["site"]].append(res_mote)

# write out

with open('locations.json', 'w') as fp:
    json.dump([{key:value}for key,value in results.iteritems()], fp, indent=4)

#-----------------------------------------------------------------------------#
