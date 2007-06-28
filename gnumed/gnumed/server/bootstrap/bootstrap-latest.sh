#!/bin/sh

# should be run as root

cd ../../
ln -vsn client Gnumed
cd -
export PYTHONPATH="../../:${PYTHONPATH}"

VER="7"
LOG_BASE="."

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
sudo -u postgres dropdb -i ${PORT_DEF} gnumed_v2


echo "=========================="
echo "2) bootstrapping databases"

# baseline v2
LOG="${LOG_BASE}/bootstrap-latest-v2.log"
rm -rf ${LOG}
CONF="redo-v2.conf"
export GM_CORE_DB="gnumed_v2"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
unset GM_CORE_DB

# v2 -> v3
LOG="${LOG_BASE}/bootstrap-latest-v3.log"
rm -rf ${LOG}
CONF="update_db-v2_v3.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
echo "Dropping obsoleted staging database gnumed_v2 ..."
sudo -u postgres dropdb ${PORT_DEF} gnumed_v2

# v3 -> v4
LOG="${LOG_BASE}/bootstrap-latest-v4.log"
rm -rf ${LOG}
CONF="update_db-v3_v4.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
echo "Dropping obsoleted staging database gnumed_v3 ..."
sudo -u postgres dropdb ${PORT_DEF} gnumed_v3

# v4 -> v5
LOG="${LOG_BASE}/bootstrap-latest-v5.log"
rm -rf ${LOG}
CONF="update_db-v4_v5.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
echo "Dropping obsoleted staging database gnumed_v4 ..."
sudo -u postgres dropdb ${PORT_DEF} gnumed_v4

# v5 -> v6
LOG="${LOG_BASE}/bootstrap-latest-v6.log"
rm -rf ${LOG}
CONF="update_db-v5_v6.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
echo "Dropping obsoleted staging database gnumed_v5 ..."
sudo -u postgres dropdb ${PORT_DEF} gnumed_v5

# v6 -> v7
LOG="${LOG_BASE}/bootstrap-latest-v7.log"
rm -rf ${LOG}
CONF="update_db-v6_v7.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
