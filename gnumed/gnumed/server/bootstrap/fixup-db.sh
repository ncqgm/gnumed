#!/bin/bash

# ========================================================
# Apply GNUmed database fixups.
#
# usage:
#  fixup-db.sh XX <quiet>
#
# prerequisites:
#  fixup_db-vX.conf must exist
#
# "secret" command line options:
#  quiet
#  - display failures only, don't chatter
#
# ========================================================

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
	echo "USAGE: $0 x"
	echo "   x   - database version to fix"
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
echo_msg "1) applying fixes to database ..."
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Fixing \"gnumed_v${VER}\" did not finish successfully."
	exit 1
fi


exit 0
