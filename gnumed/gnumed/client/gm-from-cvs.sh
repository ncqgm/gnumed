#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/gm-from-cvs.sh,v $
# $Revision: 1.16 $

# maybe force some locale setting here
#export LANGUAGE=fr

# if there are unicode troubles you can force to ASCII with this:
#export LANGUAGE=en


# source systemwide startup extension shell script if it exists
if [ -r /etc/gnumed/gnumed-startup-local.sh ] ; then
	echo "running /etc/gnumed/gnumed-startup-local.sh"
	. /etc/gnumed/gnumed-startup-local.sh
fi


# source local startup extension shell script if it exists
if [ -r ${HOME}/.gnumed/scripts/gnumed-startup-local.sh ] ; then
	echo "running ${HOME}/.gnumed/scripts/gnumed-startup-local.sh"
	. ${HOME}/.gnumed/scripts/gnumed-startup-local.sh
fi


# set options
LOG="--log-file=gm-from-cvs.log"
CONF="--conf-file=gm-from-cvs.conf"
DEV_OPTS="--override-schema-check --skip-update-check --local-import --debug"
# --hipaa
# --profile=gm-from-cvs.prof
PSYCOPG_DEBUG="on"		# should actually be done within gnumed.py based on --debug


# eventually run it
python wxpython/gnumed.py ${LOG} ${CONF} ${DEV_OPTS} $@
