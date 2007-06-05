#!/bin/sh

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-move_backups_offsite.sh,v $
# $Id: gm-move_backups_offsite.sh,v 1.3 2007-06-05 15:00:31 ncq Exp $
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

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

if test -z ${MAX_BANDWITH} ; then
	BW_LIMIT=""
else
	BW_LIMIT="--bwlimit=${MAX_BANDWIDTH}"
fi

BACKUP_FILE_GLOB="*.bz2"

HOST=`hostname`
LOG="${BACKUP_DIR}/backup.log"
TS=`date +%Y-%m-%d-%H-%M-%S`

if ping -c 3 -i 2 $TARGET_HOST > /dev/null; then
	if rsync -qac ${BW_LIMIT} ${BACKUP_DIR}/${BACKUP_FILE_GLOB} ${TARGET_HOST}:${TARGET_DIR}; then
		echo "$HOST: $TS: rsynced backups to ${TARGET_HOST}: success" >> $LOG
	else
		echo "$HOST: $TS: rsyncing backups to ${TARGET_HOST}: failure" >> $LOG
	fi;
else
    echo "$HOST: $TS: rsyncing backups to ${TARGET_HOST}: cannot reach target host" >> $LOG
fi;

#==============================================================
# $Log: gm-move_backups_offsite.sh,v $
# Revision 1.3  2007-06-05 15:00:31  ncq
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
