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
#  Add the following line to a crontab file to run a
#  database backup at 12:47 and 19:47 every day:
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
set -o pipefail


# do not run twice
[ "${FLOCKER}" != "$0" ] && exec env FLOCKER="$0" flock --exclusive --nonblock "$0" "$0" "$@" || :


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


# compute host argument and backup filename
if test -z "${GM_HOST}" ; then
	_PG_HOST_ARG=""
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-$(hostname)"
else
	if ping -c 3 -i 2 "${GM_HOST}" > /dev/null; then
		_PG_HOST_ARG="--host=\"${GM_HOST}\""
		BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-${GM_HOST}"
	else
		echo "Cannot ping database host ${GM_HOST}."
		exit 1
	fi
fi


# compute port argument
if test -z "${GM_PORT}" ; then
	_PG_PORT_ARG=""
else
	_PG_PORT_ARG="--port=${GM_PORT}"
fi


# sanity check
# (his does not work on Mac, so you
#  may need to comment this out)
if ! su --login --command "psql --no-psqlrc --tuples-only --list ${_PG_PORT_ARG}" postgres | grep --quiet "^[[:space:]]*${GM_DATABASE}" ; then
	echo "The configuration in ${CONF} is set to backup"
	echo "the GNUmed database ${GM_DATABASE}. This"
	echo "database does not exist, however. Aborting."
	exit 1
fi


# are we backing up the latest DB ?
OUR_VER=$(echo "${GM_DATABASE}" | cut -f 2 -d v)
SQL_COMPARE_VERSIONS="SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname LIKE 'gnumed_v%' AND substring(datname from 9 for 3)::integer > '${OUR_VER}');"
HAS_HIGHER_VER=$(sudo --user=postgres psql --no-psqlrc --no-align --tuples-only --dbname="${GM_DATABASE}" ${_PG_HOST_ARG} ${_PG_PORT_ARG} --command="${SQL_COMPARE_VERSIONS}")
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot sanity check database version (${RESULT}). Aborting."
	exit ${RESULT}
fi
if test "${HAS_HIGHER_VER}" = "t" ; then
	echo "Backing up database ${GM_DATABASE}."
	echo ""
	echo "However, a newer database seems to exist amongst the following:"
	echo ""
	sudo --user=postgres psql --no-psqlrc --list ${_PG_PORT_ARG} | grep gnumed_v
	echo ""
	echo "Make sure you really want to backup the older database !"
fi


# generate backup file name
TS=$(date +%Y-%m-%d-%H-%M-%S)
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"


# generate scratch dir
SCRATCH_DIR="/tmp/${BACKUP_FILENAME}"
mkdir -p "${SCRATCH_DIR}"
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot create backup scratch directory [${SCRATCH_DIR}] (${RESULT}). Aborting."
	exit ${RESULT}
fi
cd "${SCRATCH_DIR}"
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot change into scratch backup directory [${SCRATCH_DIR}] (${RESULT}). Aborting."
	exit ${RESULT}
fi


# create backup timestamp tag file
TS_FILE="${BACKUP_BASENAME}-timestamp.txt"
echo "backup: ${TS}" > "${TS_FILE}"


# create dumps
BACKUP_DATA_DIR="${BACKUP_BASENAME}.dir"
# database
pg_dump --verbose --format=directory --compress=0 --column-inserts --clean --if-exists --serializable-deferrable ${_PG_HOST_ARG} ${_PG_PORT_ARG} --username="${GM_DBO}" --file="${BACKUP_DATA_DIR}" "${GM_DATABASE}" 2> /dev/null
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot dump database content into [${BACKUP_DATA_DIR}] (${RESULT}). Aborting."
	exit ${RESULT}
fi
# roles
ROLES_FILE="${BACKUP_BASENAME}-roles.sql"
ROLES=$(psql --no-psqlrc --no-align --tuples-only --dbname="${GM_DATABASE}" ${_PG_HOST_ARG} ${_PG_PORT_ARG} --username="${GM_DBO}" --command="select gm.get_users('${GM_DATABASE}');")	#"
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot list database roles (${RESULT}). Aborting."
	exit ${RESULT}
fi
{
	echo "-- -----------------------------------------------------"
	echo "-- Below find a list of database roles which were in use"
	echo "-- in the GNUmed database \"${GM_DATABASE}\"."
	echo "--"
	echo "-- Only those need to be restored to create a working"
	echo "-- copy of your original database. All other roles can"
	echo "-- be commented out by prepending '-- ' to the relevant"
	echo "-- lines above."
	echo "-- In particular, you will very very likely want to"
	echo "-- comment out the 'postgres' role."
	echo "-- -----------------------------------------------------"
	echo ""
	echo "-- ${ROLES}"
	echo ""
	echo "-- -----------------------------------------------------"
	echo "-- Below is the result of 'pg_dumpall --roles-only':"
	echo "-- -----------------------------------------------------"
} > "${ROLES_FILE}" 2> /dev/null
# -r -> -g for older versions
sudo --user=postgres pg_dumpall --verbose --roles-only ${_PG_HOST_ARG} ${_PG_PORT_ARG} --username=postgres >> "${ROLES_FILE}" 2> /dev/null
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot dump database roles into [${ROLES_FILE}] (${RESULT}). Aborting."
	exit ${RESULT}
fi


# create tar archive
TAR_FILE="${BACKUP_FILENAME}.tar"
TAR_SCRATCH="${TAR_FILE}.partial"
tar --create --file="${TAR_SCRATCH}" "${ROLES_FILE}" "${BACKUP_DATA_DIR}"/
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Creating backup tar archive [${TAR_SCRATCH}] failed (${RESULT}). Aborting."
	rm --force "${TAR_SCRATCH}"
	exit ${RESULT}
fi


# rename to "untested" tar archive name which
# indicates that tar finished creating the archive
TAR_UNTESTED="${TAR_FILE}.untested"
mv --force "${TAR_SCRATCH}" "${TAR_UNTESTED}"
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "cannot rename TAR archive: ${TAR_SCRATCH} => ${TAR_UNTESTED}"
	exit ${RESULT}
fi


# move "untested" tar archive to final directory
# so the compression script can pick it up if needed
mv --force "${TAR_UNTESTED}" "${BACKUP_DIR}"/
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "cannot move TAR archive: ${TAR_UNTESTED} => ${BACKUP_DIR}/"
	exit ${RESULT}
fi


# taken from config file
cd "${BACKUP_DIR}"
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}] (${RESULT}). Aborting."
	exit ${RESULT}
fi
rm --dir --recursive --one-file-system "${SCRATCH_DIR:?}"/


# test tar archive
tar --extract --to-stdout --file="${TAR_UNTESTED}" > /dev/null
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "Verifying backup tar archive [${TAR_UNTESTED}] failed (${RESULT}). Aborting."
	rm --force "${TAR_UNTESTED}"
	exit ${RESULT}
fi


# rename to final archive name which
# indicates successful testing
mv --force "${TAR_UNTESTED}" "${TAR_FILE}"
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "cannot rename TAR archive: ${TAR_UNTESTED} => ${TAR_FILE}"
	exit ${RESULT}
fi
chown "${BACKUP_OWNER}" "${TAR_FILE}"


exit 0
