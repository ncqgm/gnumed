#!/bin/sh

# should be run as root
# command line options:
#  quiet

VER="9"
QUIET="$1"

cd ../../
ln -vsn client Gnumed
cd -
export PYTHONPATH="../../:${PYTHONPATH}"

if test ! -n "${GM_LOG_BASE}" ; then
	GM_LOG_BASE="."
fi ;


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


function echo_msg () {
	if test "$QUIET" == "quiet"; then
		return
	fi ;
	echo $1 ;
}


echo_msg "==========================================================="
echo_msg "Bootstrapping latest GNUmed database."
echo_msg ""
echo_msg "This will set up a GNUmed database of version v${VER}"
echo_msg "with the name \"gnumed_v${VER}\"."
echo_msg "It contains all the currently working parts including"
echo_msg "localizations for countries you don't live in. This does"
echo_msg "not disturb the operation of the GNUmed client in your"
echo_msg "country in any way."
echo_msg "==========================================================="
echo_msg "1) Dropping old baseline gnumed_v2 database if there is any."
echo_msg "   (you may need to provide the password for ${USER})"
sudo -u postgres dropdb -i ${PORT_DEF} gnumed_v2


echo_msg "=========================="
echo_msg "2) bootstrapping databases"


# baseline v2
LOG="${GM_LOG_BASE}/bootstrap-latest-v2.log"
rm -rf ${LOG}
CONF="redo-v2.conf"
export GM_CORE_DB="gnumed_v2"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v2\" did not finish successfully. Aborting."
	exit 1
fi
unset GM_CORE_DB


# v2 -> v3
LOG="${GM_LOG_BASE}/bootstrap-latest-v3.log"
rm -rf ${LOG}
CONF="update_db-v2_v3.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v3\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v2 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v2


# v3 -> v4
LOG="${GM_LOG_BASE}/bootstrap-latest-v4.log"
rm -rf ${LOG}
CONF="update_db-v3_v4.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v4\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v3 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v3


# v4 -> v5
LOG="${GM_LOG_BASE}/bootstrap-latest-v5.log"
rm -rf ${LOG}
CONF="update_db-v4_v5.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v5\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v4 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v4


# v5 -> v6
LOG="${GM_LOG_BASE}/bootstrap-latest-v6.log"
rm -rf ${LOG}
CONF="update_db-v5_v6.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v6\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v5 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v5


# v6 -> v7
LOG="${GM_LOG_BASE}/bootstrap-latest-v7.log"
rm -rf ${LOG}
CONF="update_db-v6_v7.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v7\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v6 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v6


# v7 -> v8
LOG="${GM_LOG_BASE}/bootstrap-latest-v8.log"
rm -rf ${LOG}
CONF="update_db-v7_v8.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v8\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v7 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v7


# v8 -> v9
LOG="${GM_LOG_BASE}/bootstrap-latest-v9.log"
rm -rf ${LOG}
CONF="update_db-v8_v9.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v9\" did not finish successfully. Aborting."
	exit 1
fi
#echo_msg "Dropping obsoleted staging database gnumed_v8 ..."
#echo_msg "(you may need to provide the password for ${USER})"
#sudo -u postgres dropdb ${PORT_DEF} gnumed_v8
