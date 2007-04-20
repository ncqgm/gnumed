#!/bin/sh

# should be run as root

cd ../../
ln -vsn client Gnumed
cd -
export PYTHONPATH="../../:${PYTHONPATH}"

VER="6"
DROPDB_PORT=""

# uncomment and set if your PostgreSQL server is running
# on a port different from the default port 5432, such as
# 5433 for PostgreSQL 8.1 running on Debian alongside
# a 7.4 server
#export GM_DB_PORT="5433"
#DROPDB_PORT="-p ${GM_DB_PORT}"

echo "==========================================================="
echo "Bootstrapping latest GNUmed database."
echo ""
echo "This will set up a GNUmed database of version v${VER}"
echo "with the name \"gnumed_v${VER}\"."
echo "It contains all the currently working parts including"
echo "localizations for countries you don't live in. This does"
echo "not disturb the operation of the GNUmed client in your"
echo "country in any way."
echo "==========================================================="
echo "1) Dropping old baseline gnumed_v2 database if there is any."
sudo -u postgres dropdb ${DROPDB_PORT} -i gnumed_v2
rm -rf ${LOG}

echo "=========================="
echo "2) bootstrapping databases"

LOG="bootstrap-latest-v2.log"
CONF="redo-v2.conf"
export GM_CORE_DB="gnumed_v2"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
unset GM_CORE_DB

LOG="bootstrap-latest-v3.log"
CONF="update_db-v2_v3.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
sudo -u postgres dropdb ${DROPDB_PORT} gnumed_v2

LOG="bootstrap-latest-v4.log"
CONF="update_db-v3_v4.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
sudo -u postgres dropdb ${DROPDB_PORT} gnumed_v3

LOG="bootstrap-latest-v5.log"
CONF="update_db-v4_v5.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
sudo -u postgres dropdb ${DROPDB_PORT} gnumed_v4

LOG="bootstrap-latest-v6.log"
CONF="update_db-v5_v6.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
sudo -u postgres dropdb ${DROPDB_PORT} gnumed_v5
