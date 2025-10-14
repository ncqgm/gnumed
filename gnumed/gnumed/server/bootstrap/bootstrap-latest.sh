#!/bin/bash

# - command line options:
#   - "quiet"

# to be run as root
if test $(id -u) -ne 0 ; then
	echo ""
	echo " >>> This script needs to run as root, using <sudo>, or with sufficient privileges. <<<"
	echo ""
	exit 1
fi


VERSIONS_TO_DROP="2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21"
PREV_VER="22"
VER="23"
QUIET="$1"


if test ! -n "${GM_LOG_BASE}" ; then
	GM_LOG_BASE="."
fi ;

#--------------------------------------------------
function echo_msg () {
	if test "$QUIET" == "quiet"; then
		return
	fi ;
	echo $1 ;
}

#--------------------------------------------------
function setup_connection_environment () {
	# tell libpq-based tools about the non-default hostname, if any
	if test -n "${GM_CLUSTER_HOSTNAME}" ; then
		declare -g HOST_ARG="--host=${GM_CLUSTER_HOSTNAME}"
		declare -g -x PGHOST="${GM_CLUSTER_HOSTNAME}"
	else
		declare -g HOST_ARG=""
	fi ;
	# tell libpq-based tools about the non-default port, if any
	if test -n "${GM_CLUSTER_PORT}" ; then
		declare -g PORT_ARG="--port=${GM_CLUSTER_PORT}"
		declare -g -x PGPORT="${GM_CLUSTER_PORT}"
	else
		declare -g PORT_ARG=""
	fi ;
	# tell libpq-based tools about the non-default maintenance db, if any
	if test -n "${GM_CLUSTER_MAINTENANCE_DB}" ; then
		declare -g MAINTENANCE_DB_ARG="--dbname=${GM_CLUSTER_MAINTENANCE_DB}"
		declare -g -x PGDATABASE="${GM_CLUSTER_MAINTENANCE_DB}"
	else
		declare -g MAINTENANCE_DB_ARG=""
	fi ;
	# tell libpq-based tools about the non-default superuser, if any
	if test -n "${GM_CLUSTER_SUPERUSER}" ; then
		declare -g SUPERUSER_ARG="--user=${GM_CLUSTER_SUPERUSER}"
		declare -g -x PGUSER="${GM_CLUSTER_SUPERUSER}"
	else
		declare -g SUPERUSER_ARG=""
	fi ;
}

#--------------------------------------------------
function verify_dropping_of_existing_databases () {
	ALL_PREV_VERS="${VERSIONS_TO_DROP} ${PREV_VER} ${VER}"
	for DB_VER in ${ALL_PREV_VERS} ; do
		VER_EXISTS=$(su -c "psql --list ${HOST_ARG} ${PORT_ARG} ${MAINTENANCE_DB_ARG} ${SUPERUSER_ARG}" -l postgres | grep gnumed_v${DB_VER})
		if test "${VER_EXISTS}" != "" ; then
			echo ""
			echo "------------------------------------------------"
			echo "The database \"gnumed_v${DB_VER}\" exists."
			echo ""
			echo "During bootstrapping this database"
			echo "will be OVERWRITTEN !"
			echo ""
			echo "Do you really intend to *bootstrap* or did you"
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
	done
}

#--------------------------------------------------
function drop_intermediate_databases () {
	for DB_VER in ${VERSIONS_TO_DROP} ; do
		echo_msg "Dropping obsoleted staging database gnumed_v${DB_VER} ..."
		echo_msg " (you may need to provide the password for ${USER})"
		su -c "dropdb ${HOST_ARG} ${PORT_ARG} gnumed_v${DB_VER} ${SUPERUSER_ARG}" -l postgres
	done
}

#--------------------------------------------------
function run_bootstrapper () {
	LOG="${GM_LOG_BASE}/bootstrap-latest.log"
	CONF="bootstrap-latest.conf"
	./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF} --${QUIET}
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Bootstrapping \"gnumed_v${VER}\" did not finish successfully (${RESULT}). Aborting."
		read
		exit 1
	fi
}

#--------------------------------------------------
echo_msg "==========================================================="
echo_msg "Bootstrapping latest GNUmed database."
echo_msg ""
echo_msg "This will set up a GNUmed database of version v${VER}"
echo_msg "with the name \"gnumed_v${VER}\"."

setup_connection_environment
verify_dropping_of_existing_databases			# better safe than sorry
run_bootstrapper
drop_intermediate_databases
