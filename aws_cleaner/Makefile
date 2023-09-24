SHELL := /bin/bash

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DOXYGEN := $(realpath ${ROOT_DIR}/../../../homebrew/bin/doxygen)
test := $(whoami)

doxygen:
	${DOXYGEN}
