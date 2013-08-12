#!/bin/bash

#==============================================================
# This script tries to restore a GNUmed database from a
# backup. It tries to be very conservative. It is intended
# for interactive use and will have to be adjusted to your
# needs.
#
# Note that for some reason it doesn't work when the backup
# file you intend to use is a link to the actual backup.
# Use the full path instead.
#
# Best run as root.
#
# author: Karsten Hilbert
# license: GPL v2 or later
#==============================================================
set -o pipefail


BACKUP="$1"
if test -z ${BACKUP} ; then
	echo "====================================================="
	echo "usage: $0 <backup file>"
	echo ""
	echo " <backup file>: a backup-gnumed_vX-*.tar[.bz2] file"
	echo "====================================================="
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
chmod +rx ${WORK_DIR}
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
	echo " => Decompressing (from bzip2) ..."
	bunzip2 -v ${BACKUP}
	if test $? -ne 0 ; then
		echo "    ERROR: Cannot decompress bzip2 backup file. Aborting."
		exit 1
	fi
	BACKUP=`basename ${BACKUP} .bz2`
fi
echo " => Extracting (from tarball) ..."
tar -xvvf ${BACKUP}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot unpack tarball backup file. Aborting."
	exit 1
fi
BACKUP=`basename ${BACKUP} .tar`
rm ${BACKUP}.tar
# need to give postgres appropriate permissions:
chown -c postgres ${BACKUP}-*.sql


echo ""
echo "==> Adjusting GNUmed roles ..."
echo ""
echo "   You will now be shown the roles backup file. Please"
echo "   edit it to only include the roles you need for GNUmed."
echo ""
echo "   Remember that in PostgreSQL scripts the comment marker is \"--\"."
echo ""
read -e -p "   Press <ENTER> to start editing."
editor ${BACKUP}-roles.sql


echo ""
echo "==> Checking target database status ..."
TARGET_DB=`head -n 40 ${BACKUP}-database.sql | grep -i "create database gnumed_v" | cut -f 3 -d " "`
if test $? -ne 0 ; then
	echo "    ERROR: Cannot determine target database from backup file. Aborting."
	exit 1
fi
if test -z ${TARGET_DB} ; then
	echo "    ERROR: Backup does not create target database ${TARGET_DB}. Aborting."
	exit 1
fi
if test `sudo -u postgres psql -l -p ${GM_PORT} | grep ${TARGET_DB} | wc -l` -ne 0 ; then
	echo "    ERROR: Target database ${TARGET_DB} already exists. Aborting."
	exit 1
fi


echo ""
echo "==> Restoring GNUmed roles ..."
LOG="${LOG_BASE}/restoring-roles-${TS}.log"
sudo -u postgres psql -e -E -p ${GM_PORT} --single-transaction -f ${BACKUP}-roles.sql &> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: Failed to restore roles. Aborting."
	echo "           see: ${LOG}"
	chmod 0666 ${LOG}
	exit 1
fi
chmod 0666 ${LOG}


echo ""
echo "==> Restoring GNUmed database ${TARGET_DB} ..."
LOG="${LOG_BASE}/restoring-database-${TS}.log"
# can't use --single-transaction because CREATE DATABASE does not work inside transaction:
#sudo -u postgres psql -p ${GM_PORT} --single-transaction -f ${BACKUP}-database.sql &> ${LOG}
sudo -u postgres psql -p ${GM_PORT} -f ${BACKUP}-database.sql &> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: failed to restore database. Aborting."
	echo "           see: ${LOG}"
	chmod 0666 ${LOG}
	exit 1
fi
chmod 0666 ${LOG}


echo ""
echo "==> Analyzing database ${TARGET_DB} ..."
# --full doesn't make sense since there are no
# deleted rows in a freshly restored database but
# we need to update statistics to get decent performance
LOG="${LOG_BASE}/analyzing-database-${TS}.log"
sudo -u postgres vacuumdb -v -z -d ${TARGET_DB} -p ${GM_PORT} &> ${LOG}
chmod 0666 ${LOG}


# adjusting settings
gm-adjust_db_settings.sh ${TARGET_DB}


echo ""
echo "==> Cleaning up ..."
rm -vf ${WORK_DIR}/*
rmdir -v ${WORK_DIR}
cd -


echo ""
echo "You may need to adjust the PostgreSQL database access permissions."
echo "Please edit /etc/postgresql/x.y/main/pg_hba.conf as needed."
echo ""
echo "Typically you will need a line like this:"
echo ""
echo " local   samerole    +gm-logins   md5"
echo ""
echo "For details refer to the GNUmed documentation at:"
echo ""
echo " http://wiki.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL"
echo ""


exit 0
