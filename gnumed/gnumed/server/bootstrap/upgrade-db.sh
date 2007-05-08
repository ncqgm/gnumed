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
	export PGPORT="${GM_DB_PORT}"
fi ;

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
pg_dump -C -U gm-dbo -d gnumed_v${PREV_VER} | bzip2 -z9 > ${BAK_FILE}
echo ""
echo "2) upgrading to new database ..."
rm -rf ${LOG}
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
