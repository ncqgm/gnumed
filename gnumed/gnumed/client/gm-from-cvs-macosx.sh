#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/Attic/gm-from-cvs-macosx.sh,v $
# $Revision: 1.5 $

# start kvkd
# FIXME: needs logic to prevent more than one kvkd from running

# maybe force some locale setting here
#export LANG=fr

cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"

LOG="~/Library/Logs/gm-from-cvs-macosx.log"
rm -vf $LOG

# run
python wxpython/gnumed.py --log-file=$LOG --conf-file=gm-from-cvs.conf --debug --override-schema-check
# --profile=gm-from-cvs-macosx.prof
