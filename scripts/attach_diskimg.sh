#!/bin/bash

path="$(realpath $(dirname $BASH_SOURCE[0]))"
img_path="${path}/../images/disk/ubuntu-14.04"

if [[ "$1" == 'a' ]]; then
    sudo modprobe nbd
    sudo qemu-nbd -c /dev/nbd0 "$img_path"
    sudo mount /dev/nbd0p1 /mnt
elif [[ "$1" == "d" ]]; then
    sudo umount /mnt
    sudo qemu-nbd -d /dev/nbd0
fi



