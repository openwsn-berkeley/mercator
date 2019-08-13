# Pre-built OpenWSN firmwares for Mercator

They are distributed under OpenWSN's [LICENSE](./LICENSE.md).

| file name                                                      | board            | toolchain | project      |
|----------------------------------------------------------------|------------------|-----------|--------------|
| [openwsn-iot-lab_M3.elf](openwsn-iot-lab_M3.elf)               | iot-lab_M3       | armgcc    | oos_mercator |
| [openwsn-openmote-b-24ghz.ihex](openwsn-openmote-b-24ghz.ihex) | openmote-b-24ghz | armgcc    | oos_mercator |


## Source Code

* repository: https://github.com/openwsn-berkeley/openwsn-fw
* commit hash: `4e959776`

## How to Build

If you have all the tools installed on your machine, you can build the
firmwares by yourself:

``` shell
$ mkdir openwsn-fw; cd openwsn-fw
$ git clone -b develop https://github.com/openwsn-berkeley/openwsn-fw .
$ git checkout (commit_hash)
$ scons board=iot-lab_M3 toolchain=armgcc oos_mercator
$ cp -p build/iot-lab_M3_armgcc/projects/common/03oos_mercator_prog openwsn-iot-lab_M3.elf
$ scons board=openmote-b-24ghz toolchain=armgcc oos_mercator
$ cp -p build/openmote-b-24ghz_armgcc/projects/common/03oos_mercator_prog.ihex openwsn-openmote-b-24ghz.ihex
```

Or, if you have Docker available on your machine, you can use
`build-firmwares.sh`, which is located at the top directory:

``` shell
$ git clone https://github.com/yatch/mercator.git
$ git clone https://github.com/openwsn-berkeley/openwsn-fw
$ cd mercator
$ ./build-firmwares.sh ../openwsn-fw
```
