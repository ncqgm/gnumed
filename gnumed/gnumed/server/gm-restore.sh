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
echo "    backup file: ${BACKUP}"
if test ! -r ${BACKUP} ; then
	echo "    ERROR: Cannot access backup file. Aborting."
	echo "   "`ls -al ${BACKUP}`
	exit 1
fi


echo ""
echo "==> Reading configuration ..."
CONF="/etc/gnumed/gnumed-restore.conf"
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "    ERROR: Cannot read configuration file ${CONF}. Aborting."
	echo "   "`ls -al ${CONF}`
	exit 1
fi


mkdir -p ${LOG_BASE}
TS=`date +%Y-%m-%d_%H-%M-%S`
LOG="${LOG_BASE}/restore-${TS}.log"
echo "    log: ${LOG}"
echo "restore: ${TS}" &> ${LOG}
chmod 0666 ${LOG}


if [[ "$BACKUP" =~ .*\.bz2 ]] ; then
	echo ""
	echo "==> Testing backup file integrity ..."
	bzip2 -tv $BACKUP &>> ${LOG}
	if test $? -ne 0 ; then
		echo "    ERROR: Integrity check failed. Aborting."
		echo ""
		echo "    You may want to try recovering data with bzip2recover."
		echo ""
		echo "    log: ${LOG}"
		exit 1
	fi
fi


echo ""
echo "==> Setting up workspace ..."
WORK_DIR="${WORK_DIR_BASE}/gm-restore_${TS}/"
echo "    work dir: ${WORK_DIR}"
mkdir -p -v ${WORK_DIR} &>> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot create workspace. Aborting."
	echo "           log: ${LOG}"
	exit 1
fi
chmod +rx ${WORK_DIR}


echo ""
echo "==> Creating copy of backup file ..."
cp -v ${BACKUP} ${WORK_DIR} &>> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot copy backup file. Aborting."
	echo "   "`ls -al ${BACKUP}`
	echo "   log: ${LOG}"
	exit 1
fi


echo ""
echo "==> Unpacking backup file ..."
BACKUP=${WORK_DIR}`basename ${BACKUP}`
if [[ "${BACKUP}" =~ .*\.bz2 ]] ; then
	echo " => Decompressing (from bzip2) ..."
	bunzip2 -v ${BACKUP} &>> ${LOG}
	if test $? -ne 0 ; then
		echo "    ERROR: Cannot decompress bzip2 backup file. Aborting."
		echo "    pwd: "`pwd`
		echo "    file: ${BACKUP}"
		echo "    log: ${LOG}"
		exit 1
	fi
	BACKUP=${WORK_DIR}`basename ${BACKUP} .bz2`
fi


echo " => Extracting (from tarball) ..."
tar -C ${WORK_DIR} -xvf ${BACKUP} &>> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: Cannot unpack tarball backup file. Aborting."
	echo "    pwd: "`pwd`
	echo "    file: ${BACKUP}"
	echo "    log: ${LOG}"
	exit 1
fi
BACKUP=${WORK_DIR}`basename ${BACKUP} .tar`
rm ${BACKUP}.tar &>> ${LOG}


echo ""
echo "==> Checking target database status ..."
TARGET_DB=`pg_restore --create --schema-only ${BACKUP}.dir | head -n 40 | grep -i 'create database gnumed_v' | cut -f 3 -d ' '`
ERROR="$?"
echo "${TARGET_DB}" &>> ${LOG}
#if test ${ERROR} -ne 0 ; then
#	echo "exit code: ${ERROR}" &>> ${LOG}
#	echo "    ERROR: Cannot determine target database from backup file. Aborting."
#	echo "           log: ${LOG}"
#	exit 1
#fi
if test -z ${TARGET_DB} ; then
	echo "    ERROR: Backup does not create target database ${TARGET_DB}. Aborting."
	echo "           log: ${LOG}"
	exit 1
fi
echo "    db: ${TARGET_DB}"
if test `sudo -u postgres psql -l -p ${GM_PORT} | grep ${TARGET_DB} | wc -l` -ne 0 ; then
	echo ""
	echo "    Target database ${TARGET_DB} already exists."
	echo ""
	echo "    Restoring will OVERWRITE the existing database."
	echo "    Are you really positively sure ?"
	echo ""
	read -e -p "    [yes / NO]: "
	if test "${REPLY}" != "yes" ; then
		echo "${REPLY} (!='yes' => aborted by user)" &>> ${LOG}
		echo "    Database restore aborted by user."
		echo "    log: ${LOG}"
		exit 1
	fi
	echo "user requested drop of existing database ${TARGET_DB}" &>> ${LOG}
	sudo -u postgres dropdb -e -i --if-exists ${TARGET_DB} &>> ${LOG}
fi


echo ""
echo "==> Adjusting GNUmed roles ..."
echo ""
echo "   You will now be shown the roles backup file. Please"
echo "   edit it to only include the roles needed for GNUmed."
echo ""
echo "   Remember that in PostgreSQL scripts the comment marker is \"--\"."
echo ""
echo "   There are more instructions inside the file."
echo ""
read -e -p "   Press <ENTER> to start editing."
editor ${BACKUP}-roles.sql


echo ""
echo "==> Setting data file permissions ..."
chmod -c +r ${BACKUP}-roles.sql &>> ${LOG}
chown -c postgres ${BACKUP}-roles.sql &>> ${LOG}
chmod -cR +r ${BACKUP}.dir &>> ${LOG}
chown -cR postgres ${BACKUP}.dir &>> ${LOG}


echo ""
echo "==> Restoring GNUmed roles ..."
sudo -u postgres psql -e -E -p ${GM_PORT} --single-transaction -f ${BACKUP}-roles.sql &>> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: Failed to restore roles. Aborting."
	echo "           log: ${LOG}"
	exit 1
fi


echo ""
echo "==> Restoring GNUmed database ${TARGET_DB} ..."
# we require the database to not exist already above,
# hence we can safely use --create which we need because
# we want to create an empty target database,
# in this case we also do not need --disable-triggers
# (see pg-general list) since the section containing
# constraints is restored after section data,
# cannot use --single-transaction because CREATE DATABASE does not work inside a transaction
# need not use --clean because --create already creates "empty" database and does not apply to things copied by createdb :-(
# need not use --if-exists because --create already creates "empty" database and it does not apply to things copied by createdb :-(
CMD="sudo -u postgres pg_restore --verbose --create --dbname=template1 --exit-on-error -p ${GM_PORT} ${BACKUP}.dir/"
echo "${CMD}" &>> ${LOG}
${CMD} &>> ${LOG}
ERROR="$?"
echo "pg_restore exit code: ${ERROR}" &>> ${LOG}
if test ${ERROR} -ne 0 ; then
	echo "    ERROR: failed to restore database. Aborting."
	echo "           log: ${LOG}"
	exit 1
fi


echo ""
echo "==> Analyzing database ${TARGET_DB} ..."
# --full doesn't make sense since there are no
# deleted rows in a freshly restored database but
# we need to update statistics to get decent performance
sudo -u postgres vacuumdb -v -z -d ${TARGET_DB} -p ${GM_PORT} &>> ${LOG}
sudo -u postgres vacuumdb -v -Z -d ${TARGET_DB} -p ${GM_PORT} &>> ${LOG}


# adjusting settings
gm-adjust_db_settings ${TARGET_DB} &>> ${LOG}


echo ""
echo "==> Cleaning up ..."
echo "    log dir: ${LOG_BASE}"
rm --verbose --dir --recursive --one-file-system ${WORK_DIR} &>> ${LOG}


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
