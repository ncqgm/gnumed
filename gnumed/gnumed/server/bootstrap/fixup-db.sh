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
	exit
fi ;


# if you need to adjust the database name to something
# other than what the config file has you can use the
# following environment variable:
#export GM_CORE_DB="gnumed_v${VER}"


# if you need to adjust the port you want to use to
# connect to PostgreSQL you can use the environment
# variable below (this may be necessary if your PostgreSQL
# server is running on a port different from the default 5432)
#export GM_DB_PORT="5433"


# tell libpq-based tools about the non-default port, if any
if test -n "${GM_DB_PORT}" ; then
	PORT_DEF="-p ${GM_DB_PORT}"
	export PGPORT="${GM_DB_PORT}"
else
	PORT_DEF=""
fi ;


function echo_msg () {
	if test "$QUIET" == "quiet"; then
		return
	fi ;
	echo $1 ;
}


echo_msg ""
echo_msg "==========================================================="
echo_msg "Fixing GNUmed database."
echo_msg ""
echo_msg "This will apply fixups to an existing GNUmed database of"
echo_msg "version ${VER} named \"gnumed_v${VER}\"."
echo_msg "==========================================================="


echo_msg ""
echo_msg "1) Verifying checksums in database (can take a while) ..."
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
pg_dump ${PORT_DEF} --username=gm-dbo --dbname=gnumed_v${VER} --compress=0 --no-sync --format=custom --file=/dev/null &> /dev/null
RETCODE="$?"
if test "$RETCODE" != "0" ; then
	echo "Verifying checksums on \"gnumed_v${VER}\" failed (${RETCODE})."
	read
	exit 1
fi


echo_msg ""
echo_msg "2) Applying fixes to database ..."
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Fixing \"gnumed_v${VER}\" did not finish successfully."
	read
	exit 1
fi


exit 0
