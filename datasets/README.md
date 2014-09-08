This folder contains:

* a dataset per experiment. These files have the format `<site>-<timestamp>.csv`.
* `datasets.csv` which lists the dataset files. This file is needed by the web interface.
* `gen_datasets.py` which generates `datasets.csv` based on the current dataset files.

Each dataset file corresponds to one experiment. It is a CSV file with the following columns:

* `timestamp`: TODO
* `mac`: TODO
* `frequency`: TODO
* `sourcemac`: TODO
* `counter`: TODO
* `length`: TODO
* `interfraneduration`: TODO
* `fillbyte`: TODO
* `nummine`: TODO
* `rssimine`: TODO
* `numother`: TODO
* `rssiother`: TODO
* `numbadcrc`: TODO
* `rssibadcrc`: TODO
