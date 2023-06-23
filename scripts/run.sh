#!/bin/bash

set -e

REPO_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
LEGO_DIR="${REPO_DIR}/LegoOS"
CONF_DIR="${REPO_DIR}/config"
SIMBRICKS_DIR="${REPO_DIR}/simbricks"
OUT_DIR="${REPO_DIR}/out"
IMG_DIR="${REPO_DIR}/images"

if [ ! -d "$IMG_DIR" ]; then
    mkdir -p $IMG_DIR
fi

function update_image() {
    BUILD_DIR=${OUT_DIR}/$1.build
    if [ ! -d "${BUILD_DIR}" ]; then
        mkdir -p ${BUILD_DIR}/usr
    fi
    cp ${LEGO_DIR}/usr/general.o ${BUILD_DIR}/usr/general.o
    cd ${LEGO_DIR}
    make defconfig O=${BUILD_DIR}
    cp ${CONF_DIR}/$1.config ${BUILD_DIR}/.config
    make O=${BUILD_DIR}
    cd -
    cp ${BUILD_DIR}/arch/x86/boot/bzImage ${REPO_DIR}/images/$1.bzImage
}

cd ${LEGO_DIR}/usr && make -j$(nproc) general.o && cd -

update_image 1p1m_pcomponent
update_image 1p1m_mcomponent

python3 ${SIMBRICKS_DIR}/experiments/run.py --force --verbose \
    --repo=$SIMBRICKS_DIR --workdir=$OUT_DIR --outdir=$OUT_DIR --cpdir=$OUT_DIR \
    --parallel --cores=$(nproc) --runs=0 \
    ${REPO_DIR}/LegoOS_1p1m.py
