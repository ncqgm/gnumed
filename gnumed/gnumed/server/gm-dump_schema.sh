#!/bin/bash

#==============================================================
#
# This script creates an uncompressed, plain text (SQL) backup
# of the database schema and roles which can be used to
# debug a GNUmed database.
#
# You need to allow root to access the GNUmed database as
# user "gm-dbo" by either editing pg_hba.conf or using a
# .pgpass file.
#
# author: Karsten Hilbert
# license: GPL v2 or later
#==============================================================

CONF="/etc/gnumed/gnumed-backup.conf"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

TARGET_DB="$1"
if test -z ${TARGET_DB} ; then
	echo "============================================================="
	echo "usage: $0 <target database>"
	echo ""
	echo " <target database>: a GNUmed database (such as \"gnumed_vNN\")"
	echo "============================================================="
	exit 1
fi


# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


# FIXME: check PORT/DBO/BACKUP_FILENAME too


# sanity check: database exists ?
#if ! su -c "psql -t -l -p ${GM_PORT}" -l postgres | grep -q "^[[:space:]]*${TARGET_DB}" ; then
#	echo "You attempted to dump the schema of the"
#	echo "GNUmed database ${TARGET_DB}. This"
#	echo "database does not exist, however. Aborting."
#	exit 1
#fi


# generate backup file name
TS=`date +%Y-%m-%d-%H-%M-%S`
if test -z ${GM_HOST} ; then
	BACKUP_BASENAME="backup-${TARGET_DB}-schema_only-${INSTANCE_OWNER}-"`hostname`
else
	BACKUP_BASENAME="backup-${TARGET_DB}-schema_only-${INSTANCE_OWNER}-${GM_HOST}"
fi ;
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"


# create dumps
echo "Dumping ..."
if test -z ${GM_HOST} ; then
	# locally
	# -r -> -g for older versions
	sudo -u postgres pg_dumpall -r -v -p ${GM_PORT} > ${BACKUP_FILENAME}-roles.sql 2> /dev/null

	echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- Below find a list of database roles which were in use" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- in the GNUmed database \"${TARGET_DB}\"."            >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "--" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- Only those need to be restored to create a working"    >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- copy of your original database. All other roles can"   >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- be commented out by prepending '-- ' to the relevant"  >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- lines above."                                          >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	ROLES=`psql -A -d ${TARGET_DB} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${TARGET_DB}');"`
	echo "-- ${ROLES}" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null

	pg_dump -C -v -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-schema.sql ${TARGET_DB} 2> /dev/null
else
	# remotely
	if ping -c 3 -i 2 ${GM_HOST} > /dev/null; then
		# -r -> -g for older versions
		pg_dumpall -r -v -h ${GM_HOST} -p ${GM_PORT} -U postgres > ${BACKUP_FILENAME}-roles.sql 2> /dev/null

		echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- Below find a list of database roles which were in use" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- in the GNUmed database \"${TARGET_DB}\"."            >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "--" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- Only those need to be restored to create a working"    >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- copy of your original database. All other roles can"   >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- be commented out by prepending '-- ' to the relevant"  >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- lines above."                                          >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		ROLES=    `psql -A -d ${TARGET_DB} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${TARGET_DB}');"`
		echo "-- ${ROLES}" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null

		pg_dump -C -v -h ${GM_HOST} -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-schema.sql ${TARGET_DB} 2> /dev/null
	else
		echo "Cannot ping database host ${GM_HOST}."
		exit 1
	fi ;
fi ;


# remove passwords
echo "Removing passwords from dump ..."
sed "s/PASSWORD '.*'/PASSWORD 'md5 ***removed***'/" ${BACKUP_FILENAME}-roles.sql > tmp.sql
mv -f tmp.sql ${BACKUP_FILENAME}-roles.sql


# tar and test it
echo "Compressing ..."
if test -z ${VERIFY_TAR} ; then
	tar -cf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-schema.sql ${BACKUP_FILENAME}-roles.sql
else
	tar -cWf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-schema.sql ${BACKUP_FILENAME}-roles.sql
fi ;
if test "$?" != "0" ; then
	echo "Creating backup tar archive [${BACKUP_FILENAME}.tar] failed. Aborting."
	exit 1
fi
rm -f ${BACKUP_FILENAME}-schema.sql
rm -f ${BACKUP_FILENAME}-roles.sql


# compress and test it
bzip2 -zq9 ${BACKUP_FILENAME}.tar
bzip2 -tq ${BACKUP_FILENAME}.tar.bz2
rm -f ${BACKUP_FILENAME}.tar


echo ""
echo "Dump file: " `pwd`/${BACKUP_FILENAME}.tar.bz2
echo ""


exit 0

#==============================================================
