#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/Attic/gm-Medica2004-from-cvs.sh,v $
# $Revision: 1.1 $

# start kvkd
# FIXME: needs logic to prevent more than one kvkd from running

# maybe force some locale setting here
#export LANG=de_DE

# since we are read-only (CD) we need to make sure the
# link is there before burning the CD image
#cd ../
#ln -vfsn client Gnumed
#cd -
export PYTHONPATH="${PYTHONPATH}:../"

# please point the log file to somewhere on the RAM disk !
LOG="gm-Medica2004.log"
rm -vf ${LOG}

# likewise for the config file - it needs to be writable !
CONF="gm-Medica2004.conf"

python wxpython/gnumed.py --log-file=${LOG} --conf-file=${CONF}
#--debug
#--profile=gm-from-cvs.prof
