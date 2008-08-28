#!/bin/bash

# ========================================================
# Upgrade GNUmed database from version to version.
#
# usage:
#  upgrade-db.sh vX vX+1 <secrets>
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
#  no-compression
#  - create a backup but don't compress it (you got plenty of disk but run low on cycles)
#  quiet
#  - display failures only, don't chatter
#
# ========================================================

PREV_VER="$1"
NEXT_VER="$2"
SKIP_BACKUP="$3"
BZIP_BACKUP="$3"
QUIET="$3"
LOG_BASE="."
LOG="${LOG_BASE}/update_db-v${PREV_VER}_v${NEXT_VER}.log"
CONF="update_db-v${PREV_VER}_v${NEXT_VER}.conf"
BAK_FILE="backup-upgrade-v${PREV_VER}-to-v${NEXT_VER}-"`hostname`".sql"


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
	exit
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
	PORT_DEF="-p ${GM_DB_PORT}"
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


echo_msg ""
echo_msg "==========================================================="
echo_msg "Upgrading GNUmed database."
echo_msg ""
echo_msg "This will *non-destructively* create a new GNUmed database"
echo_msg "of version v${NEXT_VER} from an existing v${PREV_VER} database."
echo_msg "Existing data is transferred and transformed as necessary."
echo_msg ""
echo_msg "The name of the new database will be \"gnumed_v${NEXT_VER}\"."
echo_msg "==========================================================="


echo_msg ""
echo_msg "1) creating backup of existing database ..."
if test "$SKIP_BACKUP" != "no-backup" ; then
	echo_msg "   Note that this may take a substantial amount of time and disk space!"
	echo_msg "   You may need to type in the password for gm-dbo."
	if test "$BZIP_BACKUP" != "no-compression" ; then
		pg_dump -C -U gm-dbo -d gnumed_v${PREV_VER} ${PORT_DEF} | bzip2 -z9 > ${BAK_FILE}.bz2
	else
		pg_dump -C -U gm-dbo -d gnumed_v${PREV_VER} ${PORT_DEF} -f ${BAK_FILE}
	fi ;
else
	echo_msg ""
	echo "   !!! SKIPPED backup !!!"
	echo_msg ""
	echo_msg "   This may prevent you from being able to restore your"
	echo_msg "   database from an up-to-date backup should you need to."
	echo_msg ""
	echo_msg "   Be sure you really know what you are doing !"
fi ;


echo_msg ""
echo_msg "2) upgrading to new database ..."
# fixup for schema hash function
# - cannot be done inside bootstrapper
# - only needed for converting anything below v6 with a v6 bootstrapper
#echo_msg "==> fixup for database hashing (will probably ask for gm-dbo password) ..."
#psql -U gm-dbo -d gnumed_v${PREV_VER} ${PORT_DEF} -f ../sql/gmConcatTableStructureFutureStub.sql
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Upgrading \"gnumed_v${PREV_VER}\" to \"gnumed_v${NEXT_VER}\" did not finish successfully."
	exit 1
fi


#echo_msg ""
#echo_msg "3) preparing new database for efficient use ..."
#echo_msg "   If the database is large this may take quite a while!"
#echo_msg "   You may need to type in the password for gm-dbo."
#vacuumdb --full --analyze ${PORT_DEF} -U gm-dbo -d gnumed_v${NEXT_VER}

exit 0
