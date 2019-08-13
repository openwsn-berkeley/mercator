#!/bin/sh

IOTLAB_M3="iot-lab_M3"
OPENMOTE_B="openmote-b-24ghz"

BOARDS="${IOTLAB_M3} ${OPENMOTE_B}"
TOOLCHAIN='armgcc'

# usage
usage() {
    echo "Usage: ./build-firmwares.sh OPENWSN_FW_LOCAL_REPO"
    echo ""
    echo "  OPENWSN_FW_LOCAL_REPO: path to opewsn-fw local repository"
}
if [ $0 != "./build-firmwares.sh" ]; then
    echo "ERROR: build-firmware.sh must be executed at mercator dir"
    echo ""
    usage
    exit 1
fi
if [ $# -ne 1 ]; then
    usage
    exit 1
fi

# identify openwsn-fw directory
OPENWSN_FW_LOCAL_REPO=$1
if [ ! -d ${OPENWSN_FW_LOCAL_REPO} ]; then
   echo "${OPENWSN_FW_LOCAL_REPO} is not found"
   exit 1
fi
echo ${OPENWSN_FW_LOCAL_REPO} | grep -E '^/' > /dev/null
if [ $? -ne 0 ]; then
    # convert it to the absolute path
    WORKING_DIR_PATH=`pwd`
    OPENWSN_FW_LOCAL_REPO="${WORKING_DIR_PATH}/${OPENWSN_FW_LOCAL_REPO}"
fi


# check docker
which docker > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "Need docker installed"
    exit 1
fi

# check git
which git > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "Need git installed"
    exit 1
fi

# identify the commit hash value
COMMIT_HASH=`cd ${OPENWSN_FW_LOCAL_REPO}; \
             git rev-parse --short HEAD 2> /dev/null`
if [ $? -ne 0 ]; then
    echo "Seems $1 is not an openwsn-fw git repository"
    echo "Cannot build firmwares"
    exit 1
fi

# build firmwares and copy them under 'firmware' directory
DOCKER_SCONS_CMD="docker run"
DOCKER_SCONS_CMD+=" --mount type=bind,"
DOCKER_SCONS_CMD+="source=${OPENWSN_FW_LOCAL_REPO},"
DOCKER_SCONS_CMD+="destination=/home/user/openwsn-fw"
DOCKER_SCONS_CMD+=" -ti yatch/openwsn-docker scons"
TIMESTAMP=`date +%Y%m%d-%H%M%S`
BUILD_LOG_FILE="build-firmwares-${TIMESTAMP}.log"

echo "Create ${BUILD_LOG_FILE}"
touch ${BUILD_LOG_FILE}
for board in ${BOARDS}; do
    echo "Build a firmware for ${board}..."
    scons_args="board=${board} toolchain=${TOOLCHAIN} oos_mercator"
    ${DOCKER_SCONS_CMD} --clean ${scons_args} >> ${BUILD_LOG_FILE}
    ${DOCKER_SCONS_CMD}         ${scons_args} >> ${BUILD_LOG_FILE}
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Build failed for ${board}..."
        echo "Check ${BUILD_LOG_FILE}"
        exit 1
    fi

    echo "Copy a firmware..."
    src_path=${OPENWSN_FW_LOCAL_REPO}
    src_path+="/build/${board}_${TOOLCHAIN}/projects/common/03oos_mercator_prog"
    dst_path="./firmwares/openwsn-${board}"
    if [ ${board} = ${IOTLAB_M3} ]; then
        dst_path+=".elf"
    fi
    if [ ${board} = ${OPENMOTE_B} ]; then
        src_path+=".ihex"
        dst_path+=".ihex"
    fi
    cp -p ${src_path} ${dst_path}
done
echo "Build logs can be found in ${BUILD_LOG_FILE}"

# update firmwares/README.md
echo "Update the commit hash value in firmwares/README.md with ${COMMIT_HASH}"
sed -i \
    -E 's/commit hash: `[0-9a-f]\{1,\}`/commit hash: `'${COMMIT_HASH}'`/' \
    firmwares/README.md
