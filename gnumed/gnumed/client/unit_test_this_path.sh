#!/bin/bash

# this runs the __main__ functions of each widget.e.g. run 
#
#	sh unit_test_this_path.sh wxpython/gmDemographics.py

# maybe force some locale setting here
#export LANG=fr

python $1 --$0.log --debug
#--profile=$0.prof
