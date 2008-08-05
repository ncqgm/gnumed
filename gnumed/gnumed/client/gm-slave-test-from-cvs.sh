#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-slave-test-from-cvs.sh,v $
# $Revision: 1.7 $

# maybe force some locale setting here
#export LANG=fr

LOG="gm-slave-test.log"
CONF="gm-from-cvs.conf"

# start GnuMed
cp -vf ${CONF} tmp-${CONF}
python wxpython/gnumed.py --log-file=${LOG} --conf-file=tmp-${CONF} --debug --slave --local-import
rm -vf tmp-${CONF}
