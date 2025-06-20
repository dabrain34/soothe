CONTRIB_DIR=contrib
DECODERS_DIR=decoders
SOOTHE=python3 ./soothe.py
CMAKE_GENERATOR=Unix Makefiles

help:
	@awk -F ':|##' '/^[^\t].+?:.*?##/ { printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF }' $(MAKEFILE_LIST)


check: ## check that very basic tests run
	@echo "Running dummy test..."
	$(SOOTHE) list
	$(SOOTHE) list -c
	$(SOOTHE) download
	$(SOOTHE) run -e dummy


create_dirs=mkdir -p $(CONTRIB_DIR) $(DECODERS_DIR)

all_reference_decoders: h264_reference_decoder h265_reference_decoder av1_reference_decoder vp9_reference_decoder  ## build all reference decoders

h265_reference_decoder: ## build H.265 reference decoder
	$(create_dirs)
	cd $(CONTRIB_DIR) && git clone --branch=HM-18.0 https://vcgit.hhi.fraunhofer.de/jct-vc/HM.git --depth=1 || true
	cd $(CONTRIB_DIR)/HM && git stash && git pull && git stash apply || true
	cd $(CONTRIB_DIR)/HM && cmake -H. -Bbuild -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-Wno-array-bounds" && $(MAKE) -C build TAppDecoder
	find $(CONTRIB_DIR)/HM/bin/umake -name "TAppDecoder" -type f -exec cp {} $(DECODERS_DIR)/ \;

h264_reference_decoder: ## build H.264 reference decoder
	$(create_dirs)
	cd $(CONTRIB_DIR) && git clone --branch=JM-19.1 https://vcgit.hhi.fraunhofer.de/jct-vc/JM.git --depth=1 || true
	cd $(CONTRIB_DIR)/JM && git stash && git pull && git stash apply || true
	cd $(CONTRIB_DIR)/JM && cmake -H. -Bbuild -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-Wno-stringop-truncation -Wno-stringop-overflow" && $(MAKE) -C build ldecod
	find $(CONTRIB_DIR)/JM/bin/umake -name "ldecod" -type f -exec cp {} $(DECODERS_DIR)/ \;

av1_reference_decoder: ## build AV1 reference decoder
	$(create_dirs)
	cd $(CONTRIB_DIR) && git clone --branch=v3.12.1 https://aomedia.googlesource.com/aom --depth=1 || true
	cd $(CONTRIB_DIR)/aom && git stash && git pull && git stash apply || true
	cd $(CONTRIB_DIR)/aom && cmake -H. -Bbuild -DCMAKE_BUILD_TYPE=Release  -Wno-stringop-overflow && $(MAKE) -j -C build aomdec
	find $(CONTRIB_DIR)/ -name "aomdec" -type f -exec cp {} $(DECODERS_DIR)/ \;

vp9_reference_decoder: ## build VP9 reference decoder
	$(create_dirs)
	cd $(CONTRIB_DIR) && git clone --branch=v1.15.2 https://chromium.googlesource.com/webm/libvpx --depth=1 || true
	cd $(CONTRIB_DIR)/libvpx && git stash && git pull && git stash apply || true
	cd $(CONTRIB_DIR)/libvpx && ./configure --disable-unit-tests --enable-vp9 && $(MAKE) -j
	find $(CONTRIB_DIR)/libvpx -name "vpxdec" -type f -exec cp {} $(DECODERS_DIR)/ \;

clean: ## remove contrib temporary folder
	rm -rf $(CONTRIB_DIR)

dbg-%:
	echo "Value of $* = $($*)"

.PHONY: help all_reference_decoders h264_reference_decoder h265_reference_decoder av1_reference_decoder vp9_reference_decoder \
check install_deps clean
