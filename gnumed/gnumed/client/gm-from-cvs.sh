#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-from-cvs.sh,v $
# $Revision: 1.10 $

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

# run
python wxpython/gnumed.py --log-file=$LOG --conf-file=gm-from-cvs.conf --override-schema-check --debug
# --slave
# --profile=gm-from-cvs.prof
