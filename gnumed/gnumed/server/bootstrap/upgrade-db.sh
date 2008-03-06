#!/bin/sh

# ========================================================
# Upgrade GNUmed database from version to version.
#
# usage:
#  upgrade-db.sh vX vX+1 <secret>
#
# limitations:
#  Only works from version to version sequentially.
#
# prerequisites:
#  update_db-vX_vX+1.conf must exist
#
# "secret" command line options:
#  no-backup
#  no-compression
#
# ========================================================

cd ../../
ln -vsn client Gnumed
cd -
export PYTHONPATH="../../:${PYTHONPATH}"


PREV_VER="$1"
NEXT_VER="$2"
SKIP_BACKUP="$3"
BZIP_BACKUP="$3"
QUIET="$4"
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

echo ""
echo "==========================================================="
echo "Upgrading GNUmed database."
echo ""
echo "This will *non-destructively* create a new GNUmed database"
echo "of version v${NEXT_VER} from an existing v${PREV_VER} database."
echo "Existing data is transferred and transformed as necessary."
echo ""
echo "The name of the new database will be \"gnumed_v${NEXT_VER}\"."
echo "==========================================================="


echo ""
echo "1) creating backup of existing database ..."
if test "$SKIP_BACKUP" != "no-backup" ; then
	echo "   Note that this may take a substantial amount of time and disk space!"
	echo "   You may need to type in the password for gm-dbo."
	if test "$BZIP_BACKUP" != "no-compression" ; then
		pg_dump -C -U gm-dbo -d gnumed_v${PREV_VER} ${PORT_DEF} | bzip2 -z9 > ${BAK_FILE}.bz2
	else
		pg_dump -C -U gm-dbo -d gnumed_v${PREV_VER} ${PORT_DEF} -f ${BAK_FILE}
	fi ;
else
	echo ""
	echo "   !!! SKIPPED backup !!!"
	echo ""
	echo "   This may prevent you from being able to restore your"
	echo "   database from a up-to-date backup should you need to."
	echo ""
	echo "   Be sure you really know what you are doing !"
fi ;


echo ""
echo "2) upgrading to new database ..."
rm -rf ${LOG}
# fixup for schema hash function
# - cannot be done inside bootstrapper
# - only needed for converting anything below v6 with a v6 bootstrapper
#echo "==> fixup for database hashing (will probably ask for gm-dbo password) ..."
#psql -U gm-dbo -d gnumed_v${PREV_VER} ${PORT_DEF} -f ../sql/gmConcatTableStructureFutureStub.sql
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} ${QUIET}
if test "$?" != "0" ; then
	echo "Upgrading \"gnumed_v${PREV_VER}\" to \"gnumed_v${NEXT_VER}\" did not finish successfully."
	exit 1
fi


#echo ""
#echo "3) preparing new database for efficient use ..."
#echo "   If the database is large this may take quite a while!"
#echo "   You may need to type in the password for gm-dbo."
#vacuumdb --full --analyze ${PORT_DEF} -U gm-dbo -d gnumed_v${NEXT_VER}

exit 0
