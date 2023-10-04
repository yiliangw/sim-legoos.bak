SHELL := /bin/bash

linux_version := 3.13.1

repo_dir := .
lego_dir := $(repo_dir)/LegoOS
config_dir := $(repo_dir)/config
simbricks_dir := $(repo_dir)/simbricks
out_dir := $(repo_dir)/out
img_dir := $(repo_dir)/images
build_dir := $(img_dir)/lego.build
module_dir := $(img_dir)/modules
kernel_dir := $(img_dir)/kernel/linux-$(linux_version)

usr_dir := $(build_dir)/usr
usr_objs := $(addprefix $(usr_dir)/, general.o)

run_exp_cmd := python3 $(simbricks_dir)/experiments/run.py --force --verbose \
	--repo=$(simbricks_dir) --workdir=$(out_dir) --cpdir=$(out_dir) \
	--runs=0 \
	# --parallel --cores=$(shell nproc)

# 2-pcomponent experiement
2p_images := $(addprefix $(img_dir)/, 2p_node_0.bzImage 2p_node_1.bzImage)
.PHONY: 2p-images
2p-images: $(2p_images)

.PHONY: 2p-run
2p-run:
	LEGOSIM_SYNC=1 LEGOSIM_NODE_0_IMG=$(img_dir)/2p_node_0.bzImage \
	LEGOSIM_NODE_1_IMG=$(img_dir)/2p_node_1.bzImage \
	$(run_exp_cmd) $(abspath $(repo_dir)/LegoOS_2p.py)

# 1-pcomponent-1-mcomponent experiment
1p1m_images := $(addprefix $(img_dir)/, 1p1m_pcomponent.bzImage 1p1m_mcomponent.bzImage)
.PHONY: 1p1m-images
1p1m-images: $(1p1m_images)

.PHONY: 1p1m-run
1p1m-run:
	LEGOSIM_SYNC=1 \
	LEGOSIM_PCOMP_IMG=$(img_dir)/1p1m_pcomponent.bzImage \
	LEGOSIM_MCOMP_IMG=$(img_dir)/1p1m_mcomponent.bzImage \
	LEGOSIM_PCOMP_MAC="52:54:00:12:34:56" \
	LEGOSIM_MCOMP_MAC="52:54:00:12:34:57" \
	$(run_exp_cmd) $(abspath $(repo_dir)/LegoOS_1p1m.py)

# 1-pcomponent-1-mcomponent-1-scomponent experiment
.PHONY: 1p1m1s-images
1p1m1s-images: $(addprefix $(module_dir)/, ethfit.ko storage.ko) \
	$(addprefix $(img_dir)/, 1p1m1s_pcomponent.bzImage 1p1m1s_mcomponent.bzImage)

.PHONY: 1p1m1s-run
1p1m1s-run:
	LEGOSIM_SYNC=1 LEGOSIM_PCOMP_MAC="52:54:00:12:34:56" \
	LEGOSIM_MCOMP_MAC="52:54:00:12:34:57" LEGOSIM_SCOMP_MAC="52:54:00:12:34:58" \
	LEGOSIM_PCOMP_IMG=$(img_dir)/1p1m1s_pcomponent.bzImage \
	LEGOSIM_MCOMP_IMG=$(img_dir)/1p1m1s_mcomponent.bzImage \
	$(run_exp_cmd) $(abspath $(repo_dir)/LegoOS_1p1m1s.py)

# LegoOS bzImage
$(img_dir)/%.bzImage: $(config_dir)/%.config $(lego_dir) $(usr_objs_path) \
		$(usr_dir)
	$(eval img_name := $(basename $(notdir $@)))
	$(eval img_build_dir := $(build_dir)/$(img_name))
	make -C $(lego_dir) mrproper
	@if [[ ! -d $(img_build_dir) ]]; then \
		mkdir $(img_build_dir); \
	fi
	cp $(config_dir)/$(img_name).config $(img_build_dir)/.config
	rm -rf $(img_build_dir)/usr; \
	ln -s $(abspath $(usr_dir)) $(img_build_dir)/usr
	make -C $(lego_dir) O=$(abspath $(img_build_dir)) -j$(shell nproc)
	cp $(build_dir)/$(img_name)/arch/x86/boot/bzImage $@

$(usr_dir): $(usr_objs)
$(usr_objs): $(wildcard $(lego_dir)/usr/*)
	if [[ ! -d $(usr_dir) ]]; then \
		mkdir -p $(usr_dir); \
	fi
	rm -rf $(usr_dir); \
	cp -r $(lego_dir)/usr $(usr_dir)
	make -s -C $(usr_dir) $(notdir $(usr_objs))

# LegoOS kernel module
$(module_dir)/ethfit.ko: $(lego_dir)/linux-modules/fit/eth $(lego_dir)
	mkdir -p $(module_dir)
	KERNEL_PATH=$(abspath $(kernel_dir)) make -C $<
	cp $</ethfit.ko $@

$(module_dir)/storage.ko: $(lego_dir)/linux-modules/storage $(lego_dir)
	mkdir -p $(module_dir)
	KERNEL_PATH=$(abspath $(kernel_dir)) make -C $<
	cp $</storage.ko $@

touch-lego:
	touch $(lego_dir)

# .PHONY: clean-images
# clean-images:
# 	rm -rf $(img_dir)/*


