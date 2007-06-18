#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/Attic/gm-restore_from_backup.sh,v $
# $Id: gm-restore_from_backup.sh,v 1.3 2007-06-18 20:36:39 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# This script tries to restore a GNUmed database from a
# backup. It tries to be very conservative. It is intended
# for interactive use and will have to be adjusted to your
# needs.
#==============================================================


BACKUP="$1"
if test -z ${BACKUP} ; then
	echo "====================================================="
	echo "usage: $0 <backup file>"
	echo ""
	echo " <backup file>: a backup-gnumed_vX-*.tar.bz2 file"
	echo "====================================================="
	exit 1
fi


echo ""
echo "==> Trying to restore GNUmed backup ..."
echo "    file: ${BACKUP}"
if test ! -r ${BACKUP} ; then
	echo "    ERROR: Cannot read backup file:"
	echo " ${BACKUP}"
	exit 1
fi


echo ""
echo "==> Testing backup file integrity ..."
bzip2 -tvv $BACKUP
if test $? -ne 0 ; then
	echo "    ERROR: integrity check failed, aborting"
	exit 1
fi



echo ""
echo "==> Reading configuration ..."
CONF="/etc/gnumed/gnumed-restore.conf"
echo "    file: $CONF"
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "    ERROR: Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


echo ""
echo "==> Setting up workspace ..."
TS=`date +%Y-%m-%d-%H-%M-%S`
WORK_DIR="${HOME}/gnumed/gm-restore-${TS}/"
mkdir -p -v ${WORK_DIR}
cd ${WORK_DIR}


echo ""
echo "==> Creating copy of backup file ..."
cp -v ${BACKUP} ${WORK_DIR}


echo ""
echo "==> Unpacking backup file ..."
BACKUP=${WORK_DIR}/`basename ${BACKUP} .tar.bz2`
bunzip2 -vv ${BACKUP}.tar.bz2
tar -xvvf ${BACKUP}.tar


echo ""
echo "==> Adjusting GNUmed roles ..."
echo ""
echo "   You will now be shown the roles backup file."
echo "   Please edit it to only include the roles you need for GNUmed."
echo ""
read -e -p "   Press <ENTER> to continue."
editor ${BACKUP}-roles.sql


echo ""
TARGET_DB=`head -n 40 ${BACKUP}-database.sql | grep -i "create database gnumed_v" | cut -f 3 -d " "`
echo "==> Checking for existence of target database ${TARGET_DB} ..."
if test -z ${TARGET_DB} ; then
	echo "    ERROR: backup does not create target database, aborting"
	exit 1
fi
if test `sudo -u postgres psql -l | grep ${TARGET_DB} | wc -l` -ne 0 ; then
	echo "    ERROR: database ${TARGET_DB} already exists, aborting"
	exit 1
fi


echo ""
echo "==> Restoring GNUmed roles ..."
touch restoring-roles.log
chmod 0666 restoring-roles.log
# FIXME: when 8.2 becomes standard use --single-transaction
sudo -u postgres psql -e -E -p ${GM_PORT} -f ${BACKUP}-roles.sql &> restoring-roles.log
if test $? -ne 0 ; then
	echo "    ERROR: failed to restore roles, aborting"
	exit 1
fi


echo ""
echo "==> Restoring GNUmed database ${TARGET_DB} ..."
touch restoring-database.log
chmod 0666 restoring-database.log
# FIXME: when 8.2 becomes standard use --single-transaction
sudo -u postgres psql -e -E -p ${GM_PORT} -f ${BACKUP}-database.sql &> restoring-database.log
if test $? -ne 0 ; then
	echo "    ERROR: failed to restore database, aborting"
	exit 1
fi


echo ""
echo "==> Analyzing database ${TARGET_DB} ..."
# --full doesn't make sense since there are no
# deleted rows in a freshly restored database
sudo -u postgres vacuumdb -v -z -d ${TARGET_DB} -p ${GM_PORT} &> analyzing-database.log


echo ""
echo "==> Cleaning up ..."
rm -vf ${WORK_DIR}/*
rmdir -v ${WORK_DIR}
cd -


exit 0

#==============================================================
# $Log: gm-restore_from_backup.sh,v $
# Revision 1.3  2007-06-18 20:36:39  ncq
# - improved output
# - vacuum analyze after restoration
#
# Revision 1.2  2007/05/17 15:21:04  ncq
# - speed up grepping for create database
#
# Revision 1.1  2007/05/08 11:11:21  ncq
# - a tested restore script
#
#