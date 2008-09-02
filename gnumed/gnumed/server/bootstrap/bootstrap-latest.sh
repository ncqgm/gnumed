#!/bin/bash

# - should be run as root
# - command line options:
#   - "quiet"

VER="10"
PREV_VER="9"
VERSIONS_TO_DROP="2 3 4 5 6 7 8"
QUIET="$1"


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


# better safe than sorry
TARGET_VER_EXISTS=`sudo -u postgres psql -l | grep gnumed_v${VER}`
PREV_VER_EXISTS=`sudo -u postgres psql -l | grep gnumed_v${PREV_VER}`
if test "${TARGET_VER_EXISTS}" != "" -o  "${PREV_VER_EXISTS}" != "" ; then
	echo ""
	echo "-----------------------------------------------"
	echo "At least one of the GNUmed databases"
	echo "v${PREV_VER} or v${VER} already exists."
	echo ""
	echo "Note that during *bootstrapping* both"
	echo "databases will be OVERWRITTEN !"
	echo ""
	echo "Did you really intend to bootstrap or did you"
	echo "rather want to *upgrade* from v${PREV_VER} to v${VER} ?"
	echo ""
	echo "For upgrading you should run the"
	echo "upgrade script instead."
	echo ""
	echo "Continue bootstrapping (deletes databases) ? "
	echo ""
	read -e -p "[yes / NO]: "
	if test "${REPLY}" != "yes" ; then
		echo "Bootstrapping aborted by user."
		exit 1
	fi
fi


LOG="${GM_LOG_BASE}/bootstrap-latest.log"
CONF="bootstrap-latest.conf"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
if test "$?" != "0" ; then
	echo "Bootstrapping \"gnumed_v${VER}\" did not finish successfully. Aborting."
	exit 1
fi


for DB_VER in ${VERSIONS_TO_DROP} ; do
	echo_msg "Dropping obsoleted staging database gnumed_v${DB_VER} ..."
	echo_msg "(you may need to provide the password for ${USER})"
	sudo -u postgres dropdb ${PORT_DEF} gnumed_v${DB_VER}
done
