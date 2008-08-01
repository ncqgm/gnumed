#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-move_backups_offsite.sh,v $
# $Id: gm-move_backups_offsite.sh,v 1.9 2008-08-01 10:34:21 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# This script can be used to move backups to another host, IOW
# storing them "offsite" in the losest sense of the word.
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

LOG="${BACKUP_DIR}/backup.log"
HOST=`hostname`
BACKUP_FILE_GLOB="backup-*.bz2"

# do not run concurrently
if test `ps ax | grep $0 | grep -v grep | grep -v $$` != "" ; then
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
# $Log: gm-move_backups_offsite.sh,v $
# Revision 1.9  2008-08-01 10:34:21  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.8  2007/12/08 15:23:15  ncq
# - minor cleanup
#
# Revision 1.7  2007/12/02 11:46:52  ncq
# - better docs
# - source options from gnumed-backup.conf
# - sharpen up glob regex
#
# Revision 1.6  2007/07/17 13:44:38  ncq
# - fix grep
#
# Revision 1.5  2007/07/13 12:11:42  ncq
# - do not run concurrently
# - missing "" fix
#
# Revision 1.4  2007/07/13 11:32:46  ncq
# - support optional end-to-end checksumming
# - improved logging
#
# Revision 1.3  2007/06/05 15:00:31  ncq
# - support max bandwidth utilization
#
# Revision 1.2  2007/02/19 10:35:14  ncq
# - add some (ana)crontab lines and a few lines of documentation
#
# Revision 1.1  2007/02/16 15:33:37  ncq
# - renamed for smoother compliance into target systems
#
# Revision 1.1  2007/02/16 15:26:21  ncq
# - first version
#
#
