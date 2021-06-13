#!/bin/bash

# ========================================================
# Upgrade GNUmed database from version to version.
#
# usage:
#  upgrade-db.sh vX vX+1 <secret options>
#
# limitations:
#  Only works from version to version sequentially.
#
# prerequisites:
#  update_db-vX_vX+1.conf must exist
#
# "secret" command line options:
#  no-backup
#  - don't create a database backup (you got faith)
#  quiet
#  - display failures only, don't chatter
#
# ========================================================

set -o pipefail

PREV_VER="$1"
NEXT_VER="$2"
SKIP_BACKUP="$3"
QUIET="$3"
LOG_BASE="."
LOG="${LOG_BASE}/update_db-v${PREV_VER}_v${NEXT_VER}.log"
CONF="update_db-v${PREV_VER}_v${NEXT_VER}.conf"
TS=$(date +%Y-%m-%d-%H-%M-%S)
BAK_FILE="backup-upgrade_v${PREV_VER}_to_v${NEXT_VER}-$(hostname)-${TS}.tar"


if test ! -f $CONF ; then
	echo ""
	echo "Trying to upgrade from version <${PREV_VER}> to version <${NEXT_VER}> ..."
	echo ""
	echo "========================================="
	echo "ERROR: The configuration file:"
	echo "ERROR:"
	echo "ERROR:  $CONF"
	echo "ERROR"
	echo "ERROR: does not exist. Aborting."
	echo "========================================="
	echo ""
	echo "USAGE: $0 x x+1"
	echo "   x   - database version to upgrade from"
	echo "   x+1 - database version to upgrade to (sequentially only)"
	exit 1
fi ;


# if you need to adjust the database name to something
# other than what the config file has you can use the
# following environment variable:
#export GM_CORE_DB="gnumed_v${NEXT_VER}"


# if you need to adjust the port you want to use to
# connect to PostgreSQL you can use the environment
# variable below (this may be necessary if your PostgreSQL
# server is running on a port different from the default 5432)
#export GM_DB_PORT="5433"


# tell libpq-based tools about the non-default port, if any
if test -n "${GM_DB_PORT}" ; then
	PORT_DEF="--port=${GM_DB_PORT}"
	export PGPORT="${GM_DB_PORT}"
else
	PORT_DEF=""
fi ;


if test "$QUIET" != "quiet"; then
	QUIET="$4"
fi ;
function echo_msg () {
	if test "$QUIET" == "quiet"; then
		return
	fi ;
	echo $1 ;
}


# Darwin/MacOSX ?
# (MacOSX cannot "su -c" ...)
SYSTEM=`uname -s`
if test "${SYSTEM}" != "Darwin" ; then
	# Does source database exist ?
	TEMPLATE_DB="gnumed_v${PREV_VER}"
	VER_EXISTS=`su -c "psql -l ${PORT_DEF}" -l postgres | grep ${TEMPLATE_DB}`
	if test "${VER_EXISTS}" == "" ; then
		echo ""
		echo "Trying to upgrade from version <${PREV_VER}> to version <${NEXT_VER}> ..."
		echo ""
		echo "========================================="
		echo "ERROR: The template database"
		echo "ERROR:"
		echo "ERROR:  ${TEMPLATE_DB}"
		echo "ERROR:"
		echo "ERROR: does not exist. Aborting."
		echo "========================================="
		read
		exit 1
	fi ;
fi ;


# show what we do
echo_msg ""
echo_msg "==========================================================="
echo_msg "Upgrading GNUmed database: v${PREV_VER} -> v${NEXT_VER}"
echo_msg ""
echo_msg "This will create a new GNUmed v${NEXT_VER} database from an"
echo_msg "existing v${PREV_VER} database. Patient data is transferred and"
echo_msg "transformed as necessary. The old v${PREV_VER} database will"
echo_msg "remain unscathed. For the upgrade to proceed there must"
echo_msg "not be any connections to it by other users, however."
echo_msg ""
echo_msg "The name of the new database will be \"gnumed_v${NEXT_VER}\". Note"
echo_msg "that any pre-existing v${NEXT_VER} database WILL BE DELETED"
echo_msg "during the upgrade !"
echo_msg ""
echo_msg "(this script usually needs to be run as <root>)"
echo_msg "==========================================================="



# check for existing target database
if test "${SYSTEM}" != "Darwin" ; then
	# Does TARGET database exist ?
	VER_EXISTS=`su -c "psql -l ${PORT_DEF}" -l postgres | grep gnumed_v${NEXT_VER}`
	if test "${VER_EXISTS}" != "" ; then
		echo ""
		echo "WARNING: The target database"
		echo "WARNING:"
		echo "WARNING:  gnumed_v${NEXT_VER}"
		echo "WARNING:"
		echo "WARNING: already exists."
		echo "WARNING:"
		echo "WARNING: Note that during the upgrade this"
		echo "WARNING: database will be OVERWRITTEN !"
		echo ""
		echo "Continue upgrading (overwrites gnumed_v${NEXT_VER}) ? "
		echo ""
		read -e -p "[yes / NO]: "
		if test "${REPLY}" != "yes" ; then
			echo "Upgrading aborted by user."
			exit 1
		fi
		echo ""
	fi
fi


# check disk space
DATA_DIR=$(su -c "psql --no-align --tuples-only --quiet -c \"SELECT setting FROM pg_settings WHERE name = 'data_directory' \" " -l postgres)
BYTES_FREE=$(df --block-size=1 --output=avail ${DATA_DIR} | grep --only-matching -E '[[:digit:]]+')
DB_SIZE=$(su -c "psql --no-align --tuples-only --quiet -c \"SELECT pg_database_size('gnumed_v22') \" | grep --only-matching -E '[[:digit:]]+' " -l postgres)	#"
if [ ${DB_SIZE} -gt ${BYTES_FREE} ] ; then
	echo ""
	echo "WARNING: Disk space may be insufficient"
	echo "WARNING:"
	echo "WARNING:  Data directory : ${DATA_DIR}"
	echo "WARNING:  Data directory : ${DB_SIZE}"
	echo "WARNING:  Free disk space: ${BYTES_FREE}"
	echo "WARNING:"
	echo ""
	echo "Continue upgrading (may fail) ? "
	echo ""
	read -e -p "[y / N]: "
	if test "${REPLY}" != "y" ; then
		echo "Upgrading aborted by user."
		exit 1
	fi
fi


# either backup or verify checksums
echo_msg ""
if test "$SKIP_BACKUP" != "no-backup" ; then
	echo_msg "1) creating backup of the database that is to be upgraded ..."
	echo_msg "   This step may take a substantial amount of time and disk space."
	echo_msg "   (you will be prompted if you need to type in the password for gm-dbo)"
	pg_dump ${PORT_DEF} --username=gm-dbo --dbname=gnumed_v${PREV_VER} --format=tar --file=${BAK_FILE}
	ARCHIVED="$?"
	if test "${ARCHIVED}" != "0" ; then
		echo ""
		echo "========================================="
		echo "ERROR: Backing up database"
		echo "ERROR:"
		echo "ERROR:  gnumed_v${PREV_VER}"
		echo "ERROR:"
		echo "ERROR: failed (${ARCHIVED}). Aborting."
		echo "ERROR:"
		echo "ERROR: (${BACKUP_CMD})"
		echo "========================================="
		read
		exit 1
	fi
else
	echo_msg ""
	echo "   !!! SKIPPED backup !!!"
	echo_msg ""
	echo_msg "   This may prevent you from being able to restore your"
	echo_msg "   database from an up-to-date backup should you need to."
	echo_msg ""
	echo_msg "   Be sure you really know what you are doing !"
	echo_msg ""
	echo_msg "1) Verifying checksums in source database (can take a while) ..."
	# dump to /dev/null for checksum verification
	#--no-unlogged-table-data
	#--no-acl
	#--no-comments
	#--no-publications
	#--no-subscriptions
	#--no-security-label
	# --data-only
	#	excluding that would forego detecting problems with disk space
	#	used by unlogged tables (except we don't have any) and would not
	#	exercise some system table columns thereby possibly not detecting
	#	corruption in any of those (slim chance, however)
	#--no-tablespaces
	#	only relevant in plaintext dumps
	#--oids
	#	reading any column of a row (unTOASTED columns, that is)
	#	will effect reading the entire row, including OID, but
	#	there's no need to output that value
	pg_dump ${PORT_DEF} --username=gm-dbo --dbname=gnumed_v${PREV_VER} --compress=0 --no-sync --format=custom --file=/dev/null &> /dev/null
	RETCODE="$?"
	if test "$RETCODE" != "0" ; then
		echo "Verifying checksums on \"gnumed_v${PREV_VER}\" failed (${RETCODE})."
		read
		exit 1
	fi
fi ;


# eventually attempt the upgrade
echo_msg ""
echo_msg "2) upgrading to new database ..."
# fixup for schema hash function
# - cannot be done inside bootstrapper
# - only needed for converting anything below v6 with a v6 bootstrapper
#echo_msg "==> fixup for database hashing (will probably ask for gm-dbo password) ..."
#psql --username=gm-dbo --dbname=gnumed_v${PREV_VER} ${PORT_DEF} -f ../sql/gmConcatTableStructureFutureStub.sql
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Upgrading \"gnumed_v${PREV_VER}\" to \"gnumed_v${NEXT_VER}\" did not finish successfully."
	read
	exit 1
fi


#echo_msg ""
#echo_msg "3) preparing new database for efficient use ..."
#echo_msg "   If the database is large this may take quite a while!"
#echo_msg "   You may need to type in the password for gm-dbo."
#vacuumdb --full --analyze ${PORT_DEF} --username=gm-dbo --dbname=gnumed_v${NEXT_VER}


echo_msg ""
echo_msg "=========================================================="
echo_msg " Make sure to upgrade your database backup procedures to"
echo_msg " appropriately refer to the new database \"gnumed_v${NEXT_VER}\" !"
echo_msg "=========================================================="


exit 0
