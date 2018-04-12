#!/bin/bash

# maybe force some locale setting here
#export LANG=fr

LOG="gm-slave-test.log"
CONF="gm-from-vcs.conf"

# start GNUmed
cp -vf ${CONF} tmp-${CONF}
python3 gnumed.py --log-file=${LOG} --conf-file=tmp-${CONF} --debug --slave --local-import
rm -vf tmp-${CONF}
