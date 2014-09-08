
You are watching the raw data. To visualize it:

#### https://openwsn-berkeley.github.io/aila/ ####

### Overview ###

This repository contains raw connectivity datasets gathered on the IoT-LAB sites. These datasets are:
* **dense in time**, meaning the connectivity is continuously assessed over a long period of time; it allows one to see variation of connectivity over time.
* **dense in space**, meaning the connectivity is assessed over hundreds of measurements points; it allows one to see how connectivity is affected by the location of transmitter and receivers.
* **dense in frequency**, meaning the connectivity is assessed for each of the 16 IEEE802.15.4 frequencies; it allows one to see how connectivity is affected by the communication frequency.

Possible uses for this data:
* get a better of how propagation at in IEEE802.15.4 at 2.4GHz looks like,
* make an informed decision about the motes you will use in your next IoT-LAB experiment,
* develop propagation models taking into account time and frequency,
* use this connectivity traces as the foundation of a simulation,
* etc.

All experiments are run on the [IoT-LAB testbed](https://www.iot-lab.info/). This open testbed comprises 2,728 wireless devices deployed on six sites across France. A RESTful web interface enables a user to remotely reserve a number of devices, reprogram them with custom firmware, and monitor their activity.

### Experiment ###

### Web Interface ###

A web interface allows you to navigate the data in the repository, at https://openwsn-berkeley.github.io/aila/. The web interface is based on [d3js](http://d3js.org/), and a published as a set of [GitHub pages](https://pages.github.com/). The source code is of the web interface is in the `gh-pages` branch of this repository.

### Organization ###

The repository is organized as follows:

* `master` branch
    * `datasets/` contains the datasets, grouped by experiment.
    * `locations/` contains the locations of the motes, grouped by deployment site.
    * `code/` contains the firmware run on the motes, and the scripts to run an experiment.
    * `figures/` contains the figures used in these README files.
* `gh-pages` branch:
    * source code of the web interface at https://openwsn-berkeley.github.io/aila/.

Navigate into each directory for more detailed information.

### License ###

These dataset and associated code is published under the OpenWSN license.

```
/* 
 * Copyright (c) 2010-2014, Regents of the University of California.
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *  - Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *  - Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *  - Neither the name of the Regents of the University of California nor the
 *    names of its contributors may be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */
```

You are welcome to use these datasets in your scientific publication. We do ask that you cite the following paper:

* Thomas Watteyne, Constanza Pérez García, Diego Dujovne. Aila: Dense Wireless Connectivity Datasets for the IoT. in preparation.

### Publications ###

_(feel free to any publications using these datasets to the list below)_

* Thomas Watteyne, Constanza Pérez García, Diego Dujovne. Aila: Dense Wireless Connectivity Datasets for the IoT. in preparation.

### About ###

These datasets are brought to do by the OpenWSN project.

![OpenWSN logo](https://openwsn.atlassian.net/wiki/download/attachments/25231521/openwsn_logo.png?version=1&modificationDate=1396141819100&api=v2)

Contributors

* [Thomas Watteyne](http://www.thomaswatteyne.com/)
* Constanza Perez Garcia
* Diego Dujovne
