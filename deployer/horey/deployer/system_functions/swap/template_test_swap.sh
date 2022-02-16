#!/bin/bash

set -xe

python check_swapon.py -s STRING_REPLACEMENT_SWAP_SIZE_IN_GB

#collect
#swapon --show

#output
#NAME       TYPE   SIZE USED PRIO
#/swapfile  file 1024M   0B   -2