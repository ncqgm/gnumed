#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-slave-test-from-cvs.sh,v $
# $Revision: 1.1 $

# maybe force some locale setting here
#export LANG=fr

# start GnuMed
cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
python wxpython/gnumed.py --debug --log-file=./gm-slave-test.log --slave=slave-test
