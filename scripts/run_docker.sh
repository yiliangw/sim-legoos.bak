#!/bin/bash

docker run -it --rm \
    --device /dev/kvm --privileged --user simbricks -w /home/simbricks/sim-lego \
    --mount source=$(pwd),target=/home/simbricks/sim-lego,type=bind \
    --mount source=${HOME}/.ssh,target=/home/simbricks/.ssh,type=bind,consistency=cache \
    simbricks/simbricks-build:latest \

