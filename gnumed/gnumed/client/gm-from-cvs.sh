#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-from-cvs.sh,v $
# $Revision: 1.6 $

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
rm -vf gm-from-cvs.log
python wxpython/gnumed.py --log-file=gm-from-cvs.log --debug
# --layout status_quo
# --layout terry
# --profile=gm-from-cvs.prof
