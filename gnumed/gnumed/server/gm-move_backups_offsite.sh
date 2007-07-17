#!/bin/sh

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-move_backups_offsite.sh,v $
# $Id: gm-move_backups_offsite.sh,v 1.6 2007-07-17 13:44:38 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
#
# Assume the following situation:
#
# 1) a laptop running client and database which is
#    taken to the office, to patients, etc
# 2) a desktop at home running just the client
# 3) the laptop is occasionally connected to the
#    home network and thus has access to the
#    desktop machine
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

# this needs to be set to a host you can reach via rsync w/o
# need for manually entering a password (say, SSH public key
# authentication)
TARGET_HOST="need to set this"

# this is where your backup files are kept
BACKUP_DIR="need to set this"

# this is where you want the backup files to end up on $TARGET_HOST
TARGET_DIR="need to set this"

# the maximum bandwith, in KBytes/second, to utilize
MAX_BANDWIDTH=""

# whether or not to use CRC comparison when
# determining whether or not to transfer a file,
# otherwise timestamp/size is used,
# can put quite a bit of load on both machines,
# values: yes/no
CRC="no"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

LOG="${BACKUP_DIR}/backup.log"
HOST=`hostname`
BACKUP_FILE_GLOB="*.bz2"

# do not run concurrently
if test `ps ax | grep $0 | grep -v grep | grep -v $$` != "" ; then
	echo "${HOST}: "`date`": transfer already in progress, exiting" >> ${LOG}
	exit
fi

# setup rsync arguments
ARGS="--quiet --archive --partial"
if test -n ${MAX_BANDWITH} ; then
	ARGS="${ARGS} --bwlimit=${MAX_BANDWIDTH}"
fi
if test "${CRC}" = "yes" ; then
	ARGS="${ARGS} --checksum"
fi

echo "$HOST: "`date`": attempting backup (rsync ${ARGS}) to ${TARGET_HOST}:${TARGET_DIR}" >> $LOG

if ping -c 3 -i 2 $TARGET_HOST > /dev/null; then
	if rsync ${ARGS} ${BACKUP_DIR}/${BACKUP_FILE_GLOB} ${TARGET_HOST}:${TARGET_DIR} ; then
		echo "$HOST: "`date`": success" >> $LOG
	else
		echo "$HOST: "`date`": failure: cannot transfer files" >> $LOG
	fi
else
    echo "$HOST: "`date`": failure: cannot reach target host" >> $LOG
fi

#==============================================================
# $Log: gm-move_backups_offsite.sh,v $
# Revision 1.6  2007-07-17 13:44:38  ncq
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
