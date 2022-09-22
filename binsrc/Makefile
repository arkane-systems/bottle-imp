#
# This Makefile produces all the binary images.
#

#
# default target: build both for installation
#
build: build-wrapper build-imp

build-wrapper:
	mkdir -p out
	make -C imp-wrapper

build-imp:
	mkdir -p out
	python3 -m pip install -r imp/requirements.txt --target imp --upgrade
	python3 -m zipapp -o out/imp -p "/usr/bin/env python3" -c imp

#
# clean: clean up after a build/package
#
clean: clean-wrapper clean-imp

clean-wrapper:
	make -C imp-wrapper clean

clean-imp:
	rm -f out/imp
