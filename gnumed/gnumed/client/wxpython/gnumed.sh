#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gnumed.sh,v $
# $Revision: 1.3 $

# start kvkd
# FIXME: needs logic to prevent more than one kvkd from running

# maybe force some locale setting here
#export LANG=fr

# start GnuMed
python gnumed.py
