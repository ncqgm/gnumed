#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gm-slave-test.sh,v $
# $Revision: 1.1 $

# only set this if you really know what you are doing
#export GNUMED_DIR=/foo/bar

# maybe force some locale setting here
#export LANG=fr

# start GnuMed
python gnumed.py --debug --slave=slave-test
