#!/bin/bash

set -e

SIMBRICKS_DIR=$(dirname "$0")/simbricks

git submodule init
git submodule update --init --recursive

cd $SIMBRICKS_DIR
make -j$(nproc)
make -j$(nproc) external
make -j$(nproc) build-images
cd -