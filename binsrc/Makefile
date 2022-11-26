#
# This Makefile produces all the binary images.
#

#
# default target: build both for installation
#
build: build-wrapper build-imp build-executor build-generator

build-wrapper:
	mkdir -p out
	make -C imp-wrapper

build-imp:
	mkdir -p out
	python3 -m pip install -r imp/requirements.txt --target imp/dp --upgrade
	python3 -m zipapp -o out/imp -p "/usr/bin/env python3" -c imp

build-executor:
	mkdir -p out
	python3 -m pip install -r imp-executor/requirements.txt --target imp-executor/dp --upgrade
	python3 -m zipapp -o out/imp-executor -p "/usr/bin/env python3" -c imp-executor

build-generator:
	mkdir -p out
	python3 -m pip install -r imp-generator/requirements.txt --target imp-generator/dp --upgrade
	python3 -m zipapp -o out/imp-generator -p "/usr/bin/env python3" -c imp-generator

#
# clean: clean up after a build/package
#
clean: clean-wrapper clean-imp clean-executor clean-generator
	rm -rf out

clean-wrapper:
	make -C imp-wrapper clean

clean-imp:
	rm -f out/imp

clean-executor:
	rm -f out/imp-executor

clean-generator:
	rm -f out/imp-generator
