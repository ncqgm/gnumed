#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-slave-test-from-cvs.sh,v $
# $Revision: 1.5 $

# maybe force some locale setting here
#export LANG=fr

LOG="gm-slave-test.log"
CONF="gm-from-cvs.conf"

# start GnuMed
cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
rm -vf $LOG
cp -vf ${CONF} tmp-${CONF}

python wxpython/gnumed.py --log-file=${LOG} --conf-file=tmp-${CONF} --debug --slave
# clean up
rm -vf tmp-${CONF}
rm -vf tmp-${CONF}.gmCfg.bak
