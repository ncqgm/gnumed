#!/bin/bash

#==============================================================
#
# This script can be used to move backups to another host, IOW
# storing them "offsite" in the loosest sense of the word.
#
#
# Imagine the following situation:
#
# 1) a laptop running client and database which is
#    taken to the office, to patients, etc
# 2) a desktop at home with some spare storage
# 3) the laptop is occasionally connected to the home
#    network and thus has access to the desktop machine
#
# One could add the following two lines to the cron
# script on the laptop to make sure database backups
# are replicated to the desktop whenever the laptop
# has access to it:
#
# @reboot         /usr/bin/gm-move_backups_offsite.sh
# 5 0-23 * * *    /usr/bin/gm-move_backups_offsite.sh
#
# author: Karsten Hilbert
# license: GPL v2 or later
#==============================================================

CONF="/etc/gnumed/gnumed-backup.conf"

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


# sanity check
if [ ! -d "${BACKUP_DIR}" ] ; then
	mkdir "${BACKUP_DIR}"
fi


LOG="${BACKUP_DIR}/backup.log"
HOST=`hostname`
BACKUP_FILE_GLOB="backup-*.bz2"


# do not run concurrently
if test "`ps ax | grep $0 | grep -v grep | grep -v $$`" != "" ; then
	echo "${HOST}: "`date`": transfer already in progress, exiting" >> ${LOG}
	exit
fi


# setup rsync arguments
ARGS="--quiet --archive --partial"
if test -n ${MAX_OFFSITING_BANDWITH} ; then
	ARGS="${ARGS} --bwlimit=${MAX_OFFSITING_BANDWIDTH}"
fi
if test "${OFFSITE_BY_CRC}" = "yes" ; then
	ARGS="${ARGS} --checksum"
fi


echo "$HOST: "`date`": attempting backup (rsync ${ARGS}) to ${OFFSITE_BACKUP_HOST}:${OFFSITE_BACKUP_DIR}" >> $LOG


if ping -c 3 -i 2 $OFFSITE_BACKUP_HOST > /dev/null; then
	if rsync ${ARGS} ${BACKUP_DIR}/${BACKUP_FILE_GLOB} ${OFFSITE_BACKUP_HOST}:${OFFSITE_BACKUP_DIR} ; then
		echo "$HOST: "`date`": success" >> $LOG
	else
		echo "$HOST: "`date`": failure: cannot transfer files" >> $LOG
	fi
else
    echo "$HOST: "`date`": failure: cannot reach target host" >> $LOG
fi

#==============================================================
