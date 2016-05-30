This folder contains the pre-compiled firmware to run on the IoT-LAB motes.

### Building the firmware
* for OpenMote-CC2538 boards:
`sudo scons board=OpenMote-CC2538 toolchain=armgcc oos_mercator

The resulting file is located at:
`THE_openwsn-fw_DIR/build/OpenMote-CC2538_armgcc/projects/common/03oos_openwsn_prog.ihex`

More details at:
[[https://github.com/openwsn-berkeley/mercator/wiki/Mercator-Firmware]]
