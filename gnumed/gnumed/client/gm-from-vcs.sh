#!/bin/bash


#export WXSUPPRESS_SIZER_FLAGS_CHECK="true"


# useful for reproducing problems with certain LOCALE settings
# (set values from a --debug log file)
#export LANGUAGE=
#export LC_NUMERIC=
#export LC_MESSAGES=
#export LC_MONETARY=
#export LC_COLLATE=
#export LC_CTYPE=
#export LC_ALL=
#export LC_TIME=
#export LANG=


# source systemwide startup extension shell script if it exists
if [ -r /etc/gnumed/gnumed-startup-local.sh ] ; then
	echo "running /etc/gnumed/gnumed-startup-local.sh"
	. /etc/gnumed/gnumed-startup-local.sh
fi


# source local startup extension shell script if it exists
if [ -r ${HOME}/.gnumed/scripts/gnumed-startup-local.sh ] ; then
	echo "running ${HOME}/.gnumed/scripts/gnumed-startup-local.sh"
	. ${HOME}/.gnumed/scripts/gnumed-startup-local.sh
fi


# standard options
CONF="--conf-file=gm-from-vcs.conf"

# options useful for development and debugging:
TS=$(date +%m_%d--%H_%M_%S)
DEV_OPTS="--log-file=gm-vcs-${TS}--$$.log --override-schema-check --local-import --debug"
#DEV_OPTS="${DEV_OPTS} --special=debug_sizers"
#DEV_OPTS="${DEV_OPTS} --tool=check_mimetypes_in_archive"
#DEV_OPTS="${DEV_OPTS} --tool=check_enc_epi_xref"
#DEV_OPTS="${DEV_OPTS} --tool=read_all_rows_of_table"
# --profile=gm-from-vcs.prof

# options for running from released tarballs:
TARBALL_OPTS="--local-import --debug"
# --skip-update-check

#PSYCOPG_DEBUG="on"		# should actually be done within gnumed.py based on --debug


# eventually run it
export PYTHONIOENCODING=utf-8:surrogateescape
# - devel version:
ACTIVE_BRANCH=$(git branch --show-current)
RC=$?
echo "-------------------------------------------------"
if test ${RC} -eq 0 ; then
	echo "Running from Git branch: ${ACTIVE_BRANCH}"
else
	echo "Cannot detect Git branch. Running from tarball?"
fi
echo "-------------------------------------------------"
echo "config file: ${CONF}"
echo "options: ${DEV_OPTS}"
echo "extra options: $*"
#python3 gnumed.py ${CONF} ${DEV_OPTS} "$@"
#python3 gnumed.py ${CONF} ${DEV_OPTS} "$@" |& tee gm-vcs-console_output.log
python3 gnumed.py ${CONF} ${DEV_OPTS} "$@"

# - *released* tarball version:
#echo "options: ${TARBALL_OPTS}"
#python3 gnumed.py ${CONF} ${TARBALL_OPTS} "$@"

# - production version (does not use tarball files !):
#python3 gnumed.py "$@"

# - production version with HIPAA support (does not use tarball files !):
#python3 gnumed.py --hipaa "$@"


# source systemwide shutdown extension shell script if it exists
if [ -r /etc/gnumed/gnumed-shutdown-local.sh ] ; then
	. /etc/gnumed/gnumed-shutdown-local.sh
fi


# source local shutdown extension shell script if it exists
if [ -r ${HOME}/.gnumed/scripts/gnumed-shutdown-local.sh ] ; then
	. ${HOME}/.gnumed/scripts/gnumed-shutdown-local.sh
fi
