#!/bin/sh

#this runs the __main__ functions of each widget.e.g. run 
#	
#	sh unit_test_this_path.sh wxpython/gmDemographics.py

# start kvkd
# FIXME: needs logic to prevent more than one kvkd from running

# maybe force some locale setting here
#export LANG=fr

cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
rm -vf gm-from-cvs.log
python $1 --log-file=gm-from-cvs.log --debug
#--profile=gm-from-cvs.prof
