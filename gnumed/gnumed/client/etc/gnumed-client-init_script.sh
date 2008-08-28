#!/bin/sh

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/etc/Attic/gnumed-client-init_script.sh,v $
# $Id: gnumed-client-init_script.sh,v 1.1 2008-08-28 18:07:14 ncq Exp $
#
# - copy this to /etc/init.d/gnumed-client
# - only starts the kvk demon if so configured
# - depends on /etc/init.d/libchipcard-tools to have run
# - needs to be converted to a proper init script
#
#==============================================================

CONF="/etc/gnumed/ekg+kvk-demon.conf"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi

if test "${START_DEMON}" != "true" ; then
	echo "Demon disabled in /etc/gnumed/egk+kvk-demon.conf. Aborting."
	exit 1
fi

# for good measure:
#/etc/init.d/libchipcard-tools start

# FIXME: add logging redirection
kvkcard daemon -p "${CARD_SCRIPT}" -a "@cardid@ ${CARD_SCRIPT_ARGS}" &

#==============================================================
# $Log: gnumed-client-init_script.sh,v $
# Revision 1.1  2008-08-28 18:07:14  ncq
# - first version
#
#