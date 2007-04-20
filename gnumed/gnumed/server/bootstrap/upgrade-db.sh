#!/bin/sh

# ========================================================
# Upgrade GNUmed database from version to version.
#
# usage:
#  upgrade-db.sh vX vX+1
#
# limitation:
#  Only works from version to version sequentially.
#
# prerequisites:
#  update_db-vX_vX+1.conf must exist
#
# ========================================================

cd ../../
ln -vsn client Gnumed
cd -
export PYTHONPATH="../../:${PYTHONPATH}"

PREV_VER="$1"
NEXT_VER="$2"
LOG="update_db-v${PREV_VER}_v${NEXT_VER}.log"
CONF="update_db-v${PREV_VER}_v${NEXT_VER}.conf"
BAK_FILE="backup-upgrade-v${PREV_VER}-to-v${NEXT_VER}-"`hostname`".sql.bz2"
PG_PORT=""

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

# only uncomment if needed and you know what you are doing
#export GM_CORE_DB="gnumed_v${NEXT_VER}"

# uncomment and set if your PostgreSQL server is running
# on a port different from the default port 5432, such as
# 5433 for PostgreSQL 8.1 running on Debian alongside
# a 7.4 server
#export GM_DB_PORT="5433"
#PG_PORT="-p ${GM_DB_PORT}"

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
echo "   Note that this may take a substantial amount of time and disk space!"
echo "   You may need to type in the password for gm-dbo."
pg_dump ${PG_PORT} -d gnumed_v${PREV_VER} -U gm-dbo | bzip2 -z9 > ${BAK_FILE}
echo ""
echo "2) upgrading to new database ..."
rm -rf ${LOG}
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
