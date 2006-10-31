#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-from-cvs.sh,v $
# $Revision: 1.7 $

# start kvkd
# FIXME: needs logic to prevent more than one kvkd from running

# maybe force some locale setting here
#export LANG=fr

# if there are unicode troubles you can force to ASCII with this:
#export LANG=en

cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
LOG="gm-from-cvs.log"
rm -vf $LOG

# prepare
CONF="gm-from-cvs.conf"
cp -vf $CONF tmp-$CONF

# run
python wxpython/gnumed.py --log-file=$LOG --conf-file=tmp-$CONF --debug --override-schema-check
# --profile=gm-from-cvs.prof

# clean up
rm -vf tmp-$CONF
rm -vf tmp-$CONF.gmCfg.bak
