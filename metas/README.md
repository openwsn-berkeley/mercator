This folder contains:

* a CSV file per location, listing the location of each mote.
* `sites.csv` which lists the location files. This file is needed by the web interface.
* `gen_sites.py` which generates `sites.csv` based on the current location files.
* `update_states` that generates a states.json file with all the nodes in "Active" state
* `update_locations` that generates a locations.json file with all the nodes location

Each location file corresponds is a CSV file which contains the following columns:

* `mac`: TODO
* `x`: TODO
* `y`: TODO
* `z`: TODO
