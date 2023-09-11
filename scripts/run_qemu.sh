#!/bin/bash

path="$(realpath $(dirname $BASH_SOURCE[0]))"
img_path="${path}/../images"

qemu-system-x86_64	\
	-machine q35,accel=kvm -serial mon:stdio -display none \
	-cpu host -smp 4 -m 4G \
	-drive file="${img_path}/disk/ubuntu-14.04",if=ide,index=0,media=disk \
	-drive file="${img_path}/kernel/linux.tar",if=ide,index=2,media=disk,driver=raw \
	# -nic user,model=virtio-net-pci \
	# -drive file="${img_path}/disk/users_data.img",if=ide,index=1,media=disk,driver=raw \

