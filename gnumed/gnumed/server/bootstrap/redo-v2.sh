#!/bin/sh

# *** NOTICE ***
#
# This script is pretty much obsolete these days. Most of the
# time what you need to run is either bootstrap-latest.sh or
# upgrade-db.sh
#
# Only run this script if you know *why* you need to do so.
#
# *** NOTICE ***


cd ../../
ln -vsn client Gnumed
cd -
export PYTHONPATH="../../:${PYTHONPATH}"

VER="2"
LOG="redo-v${VER}.log"
CONF="redo-v${VER}.conf"

export GM_CORE_DB="gnumed_v${VER}"


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


echo "==========================================================="
echo "Bootstrapping GNUmed database."
echo ""
echo "This will set up a GNUmed database of version v${VER}"
echo "with the name \"${GM_CORE_DB}\"."
echo "It contains all the currently working parts including"
echo "localizations for countries you don't live in. This does"
echo "not disturb the operation of the GNUmed client in your"
echo "country in any way."
echo "==========================================================="
echo "Dropping old database if there is any."
dropdb -U gm-dbo -i ${PORT_DEF} $GM_CORE_DB
rm -rf ${LOG}
echo "======================="
echo "bootstrapping database"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
