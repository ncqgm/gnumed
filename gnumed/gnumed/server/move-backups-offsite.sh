#!/bin/sh

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/Attic/move-backups-offsite.sh,v $
# $Id: move-backups-offsite.sh,v 1.1 2007-02-16 15:26:21 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#==============================================================

# this needs to be set to a host you can reach via rsync w/o
# need for manually entering a password (say, SSH public key
# authentication)
TARGET_HOST="need to set this"

# this is where your backup files are kept
BACKUP_DIR="need to set this"

# this is where you want the backup files to end up on $TARGET_HOST
TARGET_DIR="need to set this"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

BACKUP_FILE_GLOB="*.bz2"

HOST=`hostname`
LOG="${BACKUP_DIR}/backup.log"
TS=`date +%Y-%m-%d-%H-%M-%S`

if ping -c 3 -i 2 $TARGET_HOST > /dev/null; then
	if rsync -qac ${BACKUP_DIR}/${BACKUP_FILE_GLOB} ${TARGET_HOST}:${TARGET_DIR}; then
		echo "$HOST: $TS: rsynced backups to ${TARGET_HOST}: success" >> $LOG
	else
		echo "$HOST: $TS: rsyncing backups to ${TARGET_HOST}: failure" >> $LOG
	fi;
else
    echo "$HOST: $TS: rsyncing backups to ${TARGET_HOST}: cannot reach target host" >> $LOG
fi;

#==============================================================
# $Log: move-backups-offsite.sh,v $
# Revision 1.1  2007-02-16 15:26:21  ncq
# - first version
#
#
