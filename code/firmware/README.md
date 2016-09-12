This folder contains the pre-compiled firmware to run on the IoT-LAB motes.

More details in [the Mercator Firmware wiki page](https://github.com/openwsn-berkeley/mercator/wiki/Mercator-Firmware)

## Building the firmware

#### M3 boards:

To build the mercator firmware for the M3 board, run the following:  
`sudo scons board=iot-lab_M3 toolchain=armgcc oos_mercator`

The resulting file is located at:  
*THE_openwsn-fw_DIR/build/iot-lab_M3_armgcc/projects/common/03oos_mercator_prog*

--Note: For the M3 mote, you need to copy the *03oos_mercator_prog* and not the .ihex file.

The file *03oos_mercator_prog* is an ELF file and can be renammed as *03oos_mercator_prog.elf*

#### OpenMote-CC2538 boards:

To build the mercator firmware for the OpenMote-CC2538 board, run the following:  

`sudo scons board=OpenMote-CC2538 toolchain=armgcc oos_mercator`

The resulting file is located at:  
*THE_openwsn-fw_DIR/build/OpenMote-CC2538_armgcc/projects/common/03oos_openwsn_prog.ihex*

