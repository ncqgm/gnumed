#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-restore_data.sh,v $
# $Id: gm-restore_data.sh,v 1.1 2008-11-03 10:20:13 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# This script tries to restore a GNUmed database from a
# data-only backup. It tries to be very conservative. It is
# intended for interactive use and will have to be adjusted
# to your needs.
#==============================================================


TARGET_DATABASE="$1"
BACKUP="$2"
if test -z ${BACKUP} ; then
	echo "============================================================="
	echo "usage: $0 <target database> <backup file>"
	echo ""
	echo " <target database>: a GNUmed database (such as \"gnumed_v9\")"
	echo " <backup file>: a backup-gnumed_vX-*-data_only.tar[.bz2] file"
	echo "============================================================="
	exit 1
fi


echo ""
echo "==> Trying to restore a GNUmed backup ..."
echo "    file: ${BACKUP}"
if test ! -r ${BACKUP} ; then
	echo "    ERROR: Cannot access backup file. Aborting."
	exit 1
fi


echo ""
echo "==> Reading configuration ..."
CONF="/etc/gnumed/gnumed-restore.conf"
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "    ERROR: Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


echo ""
echo "==> Testing target database status ..."
if test `sudo -u postgres psql -l | grep ${TARGET_DB} | wc -l` -eq 0 ; then
	echo "    ERROR: Target database ${TARGET_DB} does not exist. Aborting."
	echo ""
	echo "    This database must contain the GNUmed schema of the proper"
	echo "    version. It must not contain any data, however."
	echo "    Use the bootstrapper the create an appropriate database"
	echo "    and the gmDBPruningDMLGenerator.py script to empty it."
	exit 1
fi


if [[ "$BACKUP" =~ .*\.bz2 ]] ; then
	echo ""
	echo "==> Testing backup file integrity ..."
	bzip2 -tv $BACKUP
	if test $? -ne 0 ; then
		echo "    ERROR: Integrity check failed. Aborting."
		echo ""
		echo "    You may want to try recovering data with bzip2recover."
		exit 1
	fi
fi


echo ""
echo "==> Setting up workspace ..."
TS=`date +%Y-%m-%d-%H-%M-%S`
WORK_DIR="${WORK_DIR_BASE}/gm-restore-${TS}/"
echo "    ${WORK_DIR}"
mkdir -p ${WORK_DIR}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot create workspace. Aborting."
	exit 1
fi
cd ${WORK_DIR}


echo ""
echo "==> Creating copy of backup file ..."
cp -v ${BACKUP} ${WORK_DIR}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot copy backup file. Aborting."
	exit 1
fi


echo ""
echo "==> Unpacking backup file ..."
BACKUP=${WORK_DIR}/`basename ${BACKUP}`
if [[ "$BACKUP" =~ .*\.bz2 ]] ; then
	bunzip2 -v ${BACKUP}
	if test $? -ne 0 ; then
		echo "    ERROR: Cannot unpack (bzip2) backup file. Aborting."
		exit 1
	fi
	BACKUP=`basename ${BACKUP} .bz2`
fi
tar -xvvf ${BACKUP}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot unpack (tar) backup file. Aborting."
	exit 1
fi
BACKUP=`basename ${BACKUP} .tar`


echo ""
echo "==> Restoring GNUmed data ..."
LOG="${LOG_BASE}/restoring-data-${TARGET_DATABASE}-${TS}.log"
# FIXME: when 8.2 becomes standard use --single-transaction
sudo -u postgres psql -p ${GM_PORT} -d ${TARGET_DATABASE} -f ${BACKUP}-data_only.sql &> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: failed to restore data. Aborting."
	echo "           see: ${LOG}"
	sudo -u postgres chmod 0666 ${LOG}
	exit 1
fi
sudo -u postgres chmod 0666 ${LOG}


echo ""
echo "==> Analyzing database ${TARGET_DB} ..."
# --full doesn't make sense since there are no
# deleted rows in a freshly restored database but
# we need to update statistics to get decent performance
LOG="${LOG_BASE}/analyzing-database-${TS}.log"
sudo -u postgres vacuumdb -v -z -d ${TARGET_DB} -p ${GM_PORT} &> ${LOG}
sudo -u postgres chmod 0666 ${LOG}


echo ""
echo "==> Cleaning up ..."
rm -vf ${WORK_DIR}/*
rmdir -v ${WORK_DIR}
cd -


exit 0

#==============================================================
# $Log: gm-restore_data.sh,v $
# Revision 1.1  2008-11-03 10:20:13  ncq
# - first version trying to restore data only
#
#
