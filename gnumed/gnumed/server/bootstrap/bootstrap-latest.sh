#!/bin/sh

# should be run as root
# command line options:
#  quiet

VER="9"
PREV_VER="8"
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
#echo_msg "It contains all the currently working parts including"
#echo_msg "localizations for countries you don't live in. This does"
#echo_msg "not disturb the operation of the GNUmed client in your"
#echo_msg "country in any way."


# better safe than sorry
PREV_VER_EXISTS=`sudo -u postgres psql -l | grep gnumed_v${PREV_VER}`
if test "${PREV_VER_EXISTS}" != "" ; then
	echo ""
	echo "There already is a GNUmed database of version v${PREV_VER}."
	echo ""
	echo "Are you sure you want to *bootstrap* to version v${VER} ?"
	echo "If you do so the existing database v${PREV_VER} will be LOST !"
	echo ""
	echo "For *upgrading* from v${PREV_VER} to v${VER} you should"
	echo "run the upgrade script instead."
	echo ""
	read -e -p "Continue bootstrapping ? [yes/NO]: "
	if test "${REPLY}" != "yes" ; then
		echo "Bootstrapping aborted by user."
		exit 1
	fi
fi


# baseline v2
LOG="${GM_LOG_BASE}/bootstrap-v2.log"
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
./upgrade-db.sh 2 3 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v3\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v2 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v2


# v3 -> v4
./upgrade-db.sh 3 4 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v4\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v3 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v3


# v4 -> v5
./upgrade-db.sh 4 5 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v5\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v4 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v4


# v5 -> v6
./upgrade-db.sh 5 6 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v6\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v5 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v5


# v6 -> v7
./upgrade-db.sh 6 7 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v7\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v6 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v6


# v7 -> v8
./upgrade-db.sh 7 8 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v8\" did not finish successfully. Aborting."
	exit 1
fi
echo_msg "Dropping obsoleted staging database gnumed_v7 ..."
echo_msg "(you may need to provide the password for ${USER})"
sudo -u postgres dropdb ${PORT_DEF} gnumed_v7


# v8 -> v9
./upgrade-db.sh 8 9 no-backup
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v9\" did not finish successfully. Aborting."
	exit 1
fi
#echo_msg "Dropping obsoleted staging database gnumed_v8 ..."
#echo_msg "(you may need to provide the password for ${USER})"
#sudo -u postgres dropdb ${PORT_DEF} gnumed_v8
