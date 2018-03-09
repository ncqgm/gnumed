#!/bin/bash

echo "Using <$0> is discouraged. Please switch to <gm-backup(.sh)>."

exit 1

#==============================================================
#
# This script creates an uncompressed, plain text (SQL) backup
# of the database schema, data, and roles which can be used to
# restore a GNUmed database from scratch with psql.
#
# You need to allow root to access the GNUmed database as
# user "gm-dbo" by either editing pg_hba.conf or using a
# .pgpass file.
#
#
# anacron
# -------
#  The following line could be added to a system's
#  /etc/anacrontab to make sure it creates daily
#  database backups for GNUmed:
#
#  1       15      backup-gnumed-<your-company>    /usr/bin/gm-backup_database.sh
#
#
# cron
# ----
#  add the following line to a crontab file to run a
#  database backup at 12:47 and 19:47 every day
#
#  47 12,19 * * * * /usr/bin/gm-backup_database.sh
#
# author: Karsten Hilbert
# license: GPL v2 or later
#==============================================================

# Keep this properly updated to refer to the
# database you want to currently backup.
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


# switched off ? (database name empty)
if [ "$GM_DATABASE" = "" ] ; then
	exit 0
fi

# FIXME: check PORT/DBO/BACKUP_FILENAME too


# sanity check
# (his does not work on Mac, so you
#  may need to comment this out)
if ! su -c "psql -t -l -p ${GM_PORT}" -l postgres | grep -q "^[[:space:]]*${GM_DATABASE}" ; then
	echo "The configuration in ${CONF} is set to backup"
	echo "the GNUmed database ${GM_DATABASE}. This"
	echo "database does not exist, however. Aborting."
	exit 1
fi


# are we backing up the latest DB ?
OUR_VER=`echo ${GM_DATABASE} | cut -f 2 -d v`
if test -z ${GM_HOST} ; then
	HAS_HIGHER_VER=`sudo -u postgres psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -c "SELECT exists (select 1 from pg_database where datname like 'gnumed_v%' and substring(datname from 9 for 3)::integer > '${OUR_VER}');"`
else
	HAS_HIGHER_VER=`sudo -u postgres psql -A -t -h ${GM_HOST} -d ${GM_DATABASE} -p ${GM_PORT} -c "SELECT exists (select 1 from pg_database where datname like 'gnumed_v%' and substring(datname from 9 for 3)::integer > '${OUR_VER}');"`
fi;

if test "${HAS_HIGHER_VER}" = "t" ; then
	echo "Backing up database ${GM_DATABASE}."
	echo ""
	echo "However, a newer database seems to exist:"
	echo ""
	sudo -u postgres psql -l -p ${GM_PORT} | grep gnumed_v
	echo ""
	echo "Make sure you really want to backup the older database !"
fi ;


# generate backup file name
TS=`date +%Y-%m-%d-%H-%M-%S`
if test -z ${GM_HOST} ; then
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-"`hostname`
else
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-${GM_HOST}"
fi ;
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"


cd ${BACKUP_DIR}
if test "$?" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}]. Aborting."
	exit 1
fi


# create dumps
if test -z ${GM_HOST} ; then
	# locally
	# -r -> -g for older versions
	sudo -u postgres pg_dumpall -r -v -p ${GM_PORT} > ${BACKUP_FILENAME}-roles.sql 2> /dev/null

	echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- Below find a list of database roles which were in use" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- in the GNUmed database \"${GM_DATABASE}\"."            >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "--" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- Only those need to be restored to create a working"    >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- copy of your original database. All other roles can"   >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- be commented out by prepending '-- ' to the relevant"  >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- lines above."                                          >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- In particular, you will very very likely want to"      >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- comment out the 'postgres' role."                      >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	ROLES=`psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${GM_DATABASE}');"`
	echo "-- ${ROLES}" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null

	pg_dump -C -v --column-inserts --disable-triggers -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-database.sql ${GM_DATABASE} 2> /dev/null
else
	# remotely
	if ping -c 3 -i 2 ${GM_HOST} > /dev/null; then
		# -r -> -g for older versions
		pg_dumpall -r -v -h ${GM_HOST} -p ${GM_PORT} -U postgres > ${BACKUP_FILENAME}-roles.sql 2> /dev/null

		echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- Below find a list of database roles which were in use" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- in the GNUmed database \"${GM_DATABASE}\"."            >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "--" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- Only those need to be restored to create a working"    >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- copy of your original database. All other roles can"   >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- be commented out by prepending '-- ' to the relevant"  >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- lines above."                                          >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- In particular, you will very very likely want to"      >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- comment out the 'postgres' role."                      >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		ROLES=`psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${GM_DATABASE}');"`
		echo "-- ${ROLES}" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null

		pg_dump -C -v --column-inserts --disable-triggers -h ${GM_HOST} -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-database.sql ${GM_DATABASE} 2> /dev/null
	else
		echo "Cannot ping database host ${GM_HOST}."
		exit 1
	fi ;
fi ;


# tar and test it
if test -z ${VERIFY_TAR} ; then
	tar -cf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-database.sql ${BACKUP_FILENAME}-roles.sql
else
	tar -cWf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-database.sql ${BACKUP_FILENAME}-roles.sql
fi ;
if test "$?" != "0" ; then
	echo "Creating backup tar archive [${BACKUP_FILENAME}.tar] failed. Aborting."
	exit 1
fi
rm -f ${BACKUP_FILENAME}-database.sql
rm -f ${BACKUP_FILENAME}-roles.sql


chown ${BACKUP_OWNER} ${BACKUP_FILENAME}.tar

exit 0

#==============================================================
