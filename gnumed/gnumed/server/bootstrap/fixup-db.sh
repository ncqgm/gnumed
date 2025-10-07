#!/bin/bash

# ========================================================
# Apply GNUmed database fixups.
#
# usage:
#  fixup-db.sh XX <quiet>
#		XX: the database version to upgrade, such as 15
#
# prerequisites:
#  fixup_db-vX.conf must exist
#
# "secret" command line options:
#  quiet
#  - display failures only, don't chatter
#
# ========================================================

set -o pipefail

VER="$1"
QUIET="$2"
LOG_BASE="."
LOG="${LOG_BASE}/fixup_db-v${VER}.log"
CONF="fixup_db-v${VER}.conf"

GM_DBO="gm-dbo"

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
}

#--------------------------------------------------
function echo_msg () {
	if test "$QUIET" == "quiet"; then
		return
	fi ;
	echo $1 ;
}

#--------------------------------------------------
function verify_database_integrity () {
	echo_msg ""
	echo_msg "1) Verifying data integrity CRCs in database (can take a while) ..."
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
	pg_dump ${HOST_ARG} ${PORT_ARG} --username="${GM_DBO}" --compress=0 --no-sync --format=custom --file=/dev/null gnumed_v${VER} &> /dev/null
	RETCODE="$?"
	if test "$RETCODE" != "0" ; then
		echo "Verifying data integrity CRCs on \"gnumed_v${VER}\" failed (${RETCODE})."
		read
		exit 1
	fi
}

#--------------------------------------------------
function verify_fixup_conf_available () {
	if test ! -f $CONF ; then
		echo ""
		echo "Trying to fix database version <${VER}> ..."
		echo ""
		echo "========================================="
		echo "ERROR: The configuration file:"
		echo "ERROR:"
		echo "ERROR:  $CONF"
		echo "ERROR"
		echo "ERROR: does not exist. Aborting."
		echo "========================================="
		echo ""
		echo "USAGE: $0 xx"
		echo "   xx   - database version to fix"
		exit 1
	fi ;
}

#==================================================
verify_fixup_conf_available

echo_msg ""
echo_msg "==========================================================="
echo_msg "Fixing GNUmed database."
echo_msg ""
echo_msg "This will apply fixups to an existing GNUmed database of"
echo_msg "version ${VER} named \"gnumed_v${VER}\"."
echo_msg "==========================================================="

setup_connection_environment
verify_database_integrity

echo_msg ""
echo_msg "2) Applying fixes to database ..."
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Fixing \"gnumed_v${VER}\" did not finish successfully."
	read
	exit 1
fi

exit 0
