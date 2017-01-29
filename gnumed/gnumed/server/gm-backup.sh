#!/bin/bash

#==============================================================
# This script creates an uncompressed, directory-style backup
# of the database schema, data, and roles which can be used to
# restore a GNUmed database from scratch with pg_restore.
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
#  1       15      backup-gnumed-<your-company>    /usr/bin/gm-backup.sh
#
#
# cron
# ----
#  add the following line to a crontab file to run a
#  database backup at 12:47 and 19:47 every day
#
#  47 12,19 * * * * /usr/bin/gm-backup.sh
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
fi

if test "${HAS_HIGHER_VER}" = "t" ; then
	echo "Backing up database ${GM_DATABASE}."
	echo ""
	echo "However, a newer database seems to exist:"
	echo ""
	sudo -u postgres psql -l -p ${GM_PORT} | grep gnumed_v
	echo ""
	echo "Make sure you really want to backup the older database !"
fi


# generate backup file name
TS=`date +%Y-%m-%d-%H-%M-%S`
if test -z ${GM_HOST} ; then
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-"`hostname`
else
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-${GM_HOST}"
fi
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"


cd ${BACKUP_DIR}
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}] (${RESULT}). Aborting."
	exit ${RESULT}
fi


# create dumps
BACKUP_DATA_DIR="${BACKUP_FILENAME}.dir"
ROLES_FILE="${BACKUP_FILENAME}-roles.sql"
if test -z ${GM_HOST} ; then
	# locally

	# database
	pg_dump -v --format=directory --compress=0 --column-inserts --clean --if-exists --serializable-deferrable -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_DATA_DIR} ${GM_DATABASE} 2> /dev/null

	# roles
	# -r -> -g for older versions
	sudo -u postgres pg_dumpall -v --roles-only -p ${GM_PORT} > ${ROLES_FILE} 2> /dev/null

	echo "" >> ${ROLES_FILE} 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${ROLES_FILE} 2> /dev/null
	echo "-- Below find a list of database roles which were in use" >> ${ROLES_FILE} 2> /dev/null
	echo "-- in the GNUmed database \"${GM_DATABASE}\"."            >> ${ROLES_FILE} 2> /dev/null
	echo "--" >> ${ROLES_FILE} 2> /dev/null
	echo "-- Only those need to be restored to create a working"    >> ${ROLES_FILE} 2> /dev/null
	echo "-- copy of your original database. All other roles can"   >> ${ROLES_FILE} 2> /dev/null
	echo "-- be commented out by prepending '-- ' to the relevant"  >> ${ROLES_FILE} 2> /dev/null
	echo "-- lines above."                                          >> ${ROLES_FILE} 2> /dev/null
	echo "-- In particular, you will very very likely want to"      >> ${ROLES_FILE} 2> /dev/null
	echo "-- comment out the 'postgres' role."                      >> ${ROLES_FILE} 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${ROLES_FILE} 2> /dev/null
	echo "" >> ${ROLES_FILE} 2> /dev/null
	ROLES=`psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${GM_DATABASE}');"`
	echo "-- ${ROLES}" >> ${ROLES_FILE} 2> /dev/null

else
	# remotely
	if ping -c 3 -i 2 ${GM_HOST} > /dev/null; then

		# database
		pg_dump -v --format=directory --compress=0 --column-inserts --clean --if-exists --serializable-deferrable -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_DATA_DIR} -h ${GM_HOST} ${GM_DATABASE} 2> /dev/null

		# roles
		# -r -> -g for older versions
		pg_dumpall -v --roles-only -h ${GM_HOST} -p ${GM_PORT} -U postgres > ${ROLES_FILE} 2> /dev/null

		echo "" >> ${ROLES_FILE} 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${ROLES_FILE} 2> /dev/null
		echo "-- Below find a list of database roles which were in use" >> ${ROLES_FILE} 2> /dev/null
		echo "-- in the GNUmed database \"${GM_DATABASE}\"."            >> ${ROLES_FILE} 2> /dev/null
		echo "--" >> ${ROLES_FILE} 2> /dev/null
		echo "-- Only those need to be restored to create a working"    >> ${ROLES_FILE} 2> /dev/null
		echo "-- copy of your original database. All other roles can"   >> ${ROLES_FILE} 2> /dev/null
		echo "-- be commented out by prepending '-- ' to the relevant"  >> ${ROLES_FILE} 2> /dev/null
		echo "-- lines above."                                          >> ${ROLES_FILE} 2> /dev/null
		echo "-- In particular, you will very very likely want to"      >> ${ROLES_FILE} 2> /dev/null
		echo "-- comment out the 'postgres' role."                      >> ${ROLES_FILE} 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${ROLES_FILE} 2> /dev/null
		echo "" >> ${ROLES_FILE} 2> /dev/null
		ROLES=`psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${GM_DATABASE}');"`
		echo "-- ${ROLES}" >> ${ROLES_FILE} 2> /dev/null

	else
		echo "Cannot ping database host ${GM_HOST}."
		exit 1
	fi
fi


# create tar archive
TAR_FILE="${BACKUP_FILENAME}.tar"
TAR_SCRATCHFILE="${TAR_FILE}.untested"
TAR_CMD="tar -cf ${TAR_SCRATCHFILE} ${ROLES_FILE} ${BACKUP_DATA_DIR}/"
${TAR_CMD}
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Creating backup tar archive [${TAR_SCRATCHFILE}] failed (${RESULT}). Aborting."
	echo "Command: ${TAR_CMD}"
	exit ${RESULT}
fi


# test tar archive
TEST_CMD="tar -xOf ${TAR_SCRATCHFILE} > /dev/null"
${TEST_CMD}
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Verifying backup tar archive [${TAR_SCRATCHFILE}] failed (${RESULT}). Aborting."
	echo "Command: ${TEST_CMD}"
	exit ${RESULT}
fi
rm --dir --recursive --one-file-system ${BACKUP_DATA_DIR}/
rm -f ${ROLES_FILE}


# rename to final archive name which
# indicates successful testing
mv -f ${TAR_SCRATCHFILE} ${TAR_FILE}
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "cannot rename TAR archive: ${TAR_SCRATCHFILE} => ${TAR_FILE}"
	exit ${RESULT}
fi
chown ${BACKUP_OWNER} ${TAR_FILE}


# find any leftover, untested tar files
# and test them so they can be compressed
shopt -s -q nullglob				# no matches -> ""
SCRATCH_FILES=${BACKUP_BASENAME}-*.tar.untested
for SCRATCH_FILE in ${SCRATCH_FILES} ; do

	# test
	TEST_CMD="tar -xOf ${SCRATCH_FILE} > /dev/null"
	${TEST_CMD}
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Verifying backup tar archive [${SCRATCH_FILE}] failed (${RESULT}). Skipping."
		echo "Command: ${TEST_CMD}"
		continue
	fi

	# rename to final archive name
	TAR_FILE=`basename ${SCRATCH_FILE} .untested`
	mv -f ${SCRATCH_FILE} ${TAR_FILE}
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Cannot rename tar archive (${RESULT}). Skipping."
		echo "FILES: ${TAR_SCRATCHFILE} => ${TAR_FILE}"
		continue
	fi
	chown ${BACKUP_OWNER} ${TAR_FILE}

done

exit 0
