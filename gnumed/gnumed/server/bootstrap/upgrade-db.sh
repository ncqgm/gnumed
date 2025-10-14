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
#  no-check
#  - do not use
# ========================================================
# ========================================================
#
# you may want/need to adjust the below:

# if you need to adjust the host name you need to use to
# connect to PostgreSQL you can use the environment
# variable below
# note that bootstrapping a non-local host has
# not been tested to any considerable degree
#
#export GM_CLUSTER_HOSTNAME=""

# if you need to adjust the port you want to use to
# connect to PostgreSQL you can use the environment
# variable below (this may be necessary if your PostgreSQL
# server is running on a port different from the default 5432)
#
#export GM_CLUSTER_PORT="5432"

# if you need to adjust the cluster maintenance database
# you can use the environment variable below (this will only
# very rarely be necessary, typically it is either template1
# or template0)
#
#export GM_CLUSTER_MAINTENANCE_DB="template1"

# if you need to adjust the cluster superuser account
# you can use the environment variable below (this will only
# sometimes be necessary, typically it is "postgres")
#
#export GM_CLUSTER_SUPERUSER="postgres"

# if you need to adjust the OS-level postmaster demon user
# you can use the environment variable below (this will only
# sometimes be necessary, typically it is "postgres")
#
#export GM_POSTMASTER_DEMON_USER="postgres"

# ========================================================
# ========================================================
set -o pipefail

PREV_VER="$1"
NEXT_VER="$2"
SKIP_BACKUP="$3"
QUIET="$3"
SKIP_CHECK="$4"
if test "$QUIET" != "quiet"; then
	QUIET="$4"
fi ;
if test "$QUIET" != "quiet"; then
	QUIET="$5"
fi ;


LOG_BASE="."
FIXUP_LOG="${LOG_BASE}/fixup_db-v${PREV_VER}.log"
FIXUP_CONF="fixup_db-v${PREV_VER}.conf"
UPGRADE_LOG="${LOG_BASE}/upgrade_db-v${PREV_VER}_v${NEXT_VER}.log"
UPGRADE_CONF="upgrade_db-v${PREV_VER}_v${NEXT_VER}.conf"
TS=$(date +%Y-%m-%d-%H-%M-%S)
BAK_FILE="backup-upgrade_v${PREV_VER}_to_v${NEXT_VER}-$(hostname)-${TS}.tar"
GM_DBO="gm-dbo"
SYSTEM=$(uname -s)

#--------------------------------------------------
function perhaps_echo_msg () {
	if test "$QUIET" == "quiet"; then
		return
	fi ;
	echo $1 ;
}

#--------------------------------------------------
function verify_upgrade_conf_available () {
	if test ! -f ${UPGRADE_CONF} ; then
		echo ""
		echo "Trying to upgrade from version <${PREV_VER}> to version <${NEXT_VER}> ..."
		echo ""
		echo "========================================="
		echo "ERROR: The configuration file:"
		echo "ERROR:"
		echo "ERROR:  ${UPGRADE_CONF}"
		echo "ERROR"
		echo "ERROR: does not exist. Aborting."
		echo "========================================="
		echo ""
		echo "USAGE: $0 x x+1"
		echo "   x   - database version to upgrade from"
		echo "   x+1 - database version to upgrade to (sequentially only)"
		exit 1
	fi ;
}

#--------------------------------------------------
function setup_connection_environment () {
	# tell libpq-based tools about the non-default hostname, if any
	if test -n "${GM_CLUSTER_HOSTNAME}" ; then
		declare -g HOST_ARG="--host=${GM_CLUSTER_HOSTNAME}"
		declare -g -x PGHOST="${GM_CLUSTER_HOSTNAME}"
	else
		declare -g HOST_ARG=""
	fi ;
	# tell libpq-based tools about the non-default port, if any
	if test -n "${GM_CLUSTER_PORT}" ; then
		declare -g PORT_ARG="--port=${GM_CLUSTER_PORT}"
		declare -g -x PGPORT="${GM_CLUSTER_PORT}"
	else
		declare -g PORT_ARG=""
	fi ;
	# tell libpq-based tools about the non-default maintenance db, if any
	if test -n "${GM_CLUSTER_MAINTENANCE_DB}" ; then
		declare -g MAINTENANCE_DB_ARG="--dbname=${GM_CLUSTER_MAINTENANCE_DB}"
		declare -g -x PGDATABASE="${GM_CLUSTER_MAINTENANCE_DB}"
	else
		declare -g MAINTENANCE_DB_ARG=""
	fi ;
	# tell libpq-based tools about the non-default superuser, if any
	if test -n "${GM_CLUSTER_SUPERUSER}" ; then
		declare -g SUPERUSER_ARG="--user=${GM_CLUSTER_SUPERUSER}"
		declare -g -x PGUSER="${GM_CLUSTER_SUPERUSER}"
	else
		declare -g SUPERUSER_ARG=""
	fi ;
}

#--------------------------------------------------
function assert_source_database_exists () {
	# Darwin/MacOSX ?
	if test "${SYSTEM}" == "Darwin" ; then
		# (MacOSX cannot "su -c" ...)
		return
	fi ;
	# Does source database exist ?
	TEMPLATE_DB="gnumed_v${PREV_VER}"
	#VER_EXISTS=`su -c "psql --list ${HOST_ARG} ${PORT_ARG} ${MAINTENANCE_DB_ARG} ${SUPERUSER_ARG}" -l postgres | grep ${TEMPLATE_DB}`
	VER_EXISTS=$(su -c "psql --list ${HOST_ARG} ${PORT_ARG} ${MAINTENANCE_DB_ARG} ${SUPERUSER_ARG}" -l postgres | grep ${TEMPLATE_DB})
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
}

#--------------------------------------------------
function warn_on_existing_target_database () {
	# Darwin/MacOSX ?
	if test "${SYSTEM}" == "Darwin" ; then
		# (MacOSX cannot "su -c" ...)
		return
	fi ;
	# Does TARGET database exist ?
	#VER_EXISTS=`su -c "psql --list ${HOST_ARG} ${PORT_ARG} ${MAINTENANCE_DB_ARG} ${SUPERUSER_ARG}" -l postgres | grep gnumed_v${NEXT_VER}`
	VER_EXISTS=$(su -c "psql --list ${HOST_ARG} ${PORT_ARG} ${MAINTENANCE_DB_ARG} ${SUPERUSER_ARG}" -l postgres | grep gnumed_v${NEXT_VER})
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
		fi ;
		echo ""
	fi ;
}

#--------------------------------------------------
function check_disk_space () {
	# Darwin/MacOSX ?
	if test "${SYSTEM}" == "Darwin" ; then
		# (MacOSX cannot "su -c" ...)
		return
	fi ;
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
		echo "Continue and try upgrading anyway (may fail) ? "
		echo ""
		read -e -p "[y / N]: "
		if test "${REPLY}" != "y" ; then
			echo "Upgrading aborted by user."
			exit 1
		fi ;
	fi ;
}

#--------------------------------------------------
function perhaps_backup_source_database () {
	perhaps_echo_msg ""
	if test "$SKIP_BACKUP" == "no-backup" ; then
		echo "   !!! SKIPPED backup !!!"
		perhaps_echo_msg ""
		perhaps_echo_msg "   This may prevent you from being able to restore your"
		perhaps_echo_msg "   database from an up-to-date backup should you need to."
		return ;
	fi;
	perhaps_echo_msg "1) creating backup of the database that is to be upgraded ..."
	perhaps_echo_msg "   This step may take a substantial amount of time and disk space."
	perhaps_echo_msg "   (you will be prompted if you need to type in the password for ${GM_DBO})"
	pg_dump ${HOST_ARG} ${PORT_ARG} --username=${GM_DBO} --format=tar --file=${BAK_FILE} gnumed_v${PREV_VER}
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
	fi ;
	# successfully backed up, no need for integrity checking
	declare -g SKIP_CHECK="no-check" ;
}

#--------------------------------------------------
function perhaps_verify_source_database_integrity () {
	perhaps_echo_msg ""
	if test "$SKIP_CHECK" == "no-check" ; then
		echo "   !!! SKIPPED verification !!!"
		perhaps_echo_msg ""
		perhaps_echo_msg "   Be sure you really know what you are doing !"
		return ;
	fi;
	perhaps_echo_msg "1) Verifying data integrity CRCs in source database (can take a while) ..."
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
	pg_dump ${HOST_ARG} ${PORT_ARG} --username=${GM_DBO} --compress=0 --no-sync --format=custom --file=/dev/null gnumed_v${PREV_VER} &> /dev/null
	RETCODE="$?"
	if test "$RETCODE" != "0" ; then
		echo "Verifying data integrity CRCs on \"gnumed_v${PREV_VER}\" failed (${RETCODE})."
		read
		exit 1
	fi ;
}

#--------------------------------------------------
function explain_planned_upgrade () {
	perhaps_echo_msg ""
	perhaps_echo_msg "==========================================================="
	perhaps_echo_msg "Upgrading GNUmed database: v${PREV_VER} -> v${NEXT_VER}"
	perhaps_echo_msg ""
	perhaps_echo_msg "This will create a new GNUmed v${NEXT_VER} database from an"
	perhaps_echo_msg "existing v${PREV_VER} database. Patient data is transferred and"
	perhaps_echo_msg "transformed as necessary. The old v${PREV_VER} database will"
	perhaps_echo_msg "remain unscathed. For the upgrade to proceed there must"
	perhaps_echo_msg "not be any connections to it by other users, however."
	perhaps_echo_msg ""
	perhaps_echo_msg "The name of the new database will be \"gnumed_v${NEXT_VER}\". Note"
	perhaps_echo_msg "that any pre-existing v${NEXT_VER} database WILL BE DELETED"
	perhaps_echo_msg "during the upgrade !"
	perhaps_echo_msg ""
	perhaps_echo_msg "(this script usually needs to be run as <root>)"
	perhaps_echo_msg "==========================================================="
}

#--------------------------------------------------
function apply_source_database_fixups () {
	perhaps_echo_msg ""
	perhaps_echo_msg "2) applying fixes to existing database"
	./bootstrap_gm_db_system.py --log-file=${FIXUP_LOG} --conf-file=${FIXUP_CONF} --${QUIET}
	if test "$?" != "0" ; then
		echo "Fixing \"gnumed_v${PREV_VER}\" did not finish successfully."
		read
		exit 1
	fi
}

#--------------------------------------------------
function upgrade_source_to_target_database () {
	perhaps_echo_msg ""
	perhaps_echo_msg "2) upgrading to new database ..."
	# fixup for schema hash function
	# - cannot be done inside bootstrapper
	# - only needed for converting anything below v6 with a v6 bootstrapper
	#perhaps_echo_msg "==> fixup for database hashing (will probably ask for ${GM_DBO} password) ..."
	#psql --username=${GM_DBO} --dbname=gnumed_v${PREV_VER} ${HOST_ARG} ${PORT_ARG} -f ../sql/gmConcatTableStructureFutureStub.sql
	./bootstrap_gm_db_system.py --log-file=${UPGRADE_LOG} --conf-file=${UPGRADE_CONF} --${QUIET}
	if test "$?" != "0" ; then
		echo "Upgrading \"gnumed_v${PREV_VER}\" to \"gnumed_v${NEXT_VER}\" did not finish successfully."
		read
		exit 1
	fi
}

#--------------------------------------------------
function vacuum_target_database () {
	perhaps_echo_msg ""
	perhaps_echo_msg "4) preparing new database for efficient use ..."
	perhaps_echo_msg "   If the database is large this may take quite a while!"
	perhaps_echo_msg "   You may need to type in the password for ${GM_DBO}."
	vacuumdb --full --analyze ${HOST_ARG} ${PORT_ARG} ${MAINTENANCE_DB_ARG} --username=${GM_DBO} gnumed_v${NEXT_VER}
}

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
verify_upgrade_conf_available
setup_connection_environment
assert_source_database_exists
explain_planned_upgrade
warn_on_existing_target_database
check_disk_space
perhaps_backup_source_database
perhaps_verify_source_database_integrity
#apply_source_database_fixups
upgrade_source_to_target_database
#vacuum_target_database


perhaps_echo_msg ""
perhaps_echo_msg "=========================================================="
perhaps_echo_msg " Make sure to upgrade your database backup procedures to"
perhaps_echo_msg " appropriately refer to the new database \"gnumed_v${NEXT_VER}\" !"
perhaps_echo_msg "=========================================================="


exit 0
