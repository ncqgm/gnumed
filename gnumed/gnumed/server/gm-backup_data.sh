#!/bin/bash

echo "Using <$0> is discouraged. Please switch to <gm-backup(.sh)>."

exit 1

#==============================================================
#
# This script creates a backup of the data of a GNUmed
# database. It includes neither roles nor the schema.
# The backup can be used to restore the data into a
# preexisting, empty database.
#
# You need to be able to access the GNUmed database as
# user "gm-dbo" by either editing pg_hba.conf or using a
# .pgpass file.
#
#
# To restore the data-only dump do this:
#
# 1) $> python3 gmDBPruningDMLGenerator.py <data only dump>
# 2) $> psql -d gnumed_vX -U gm-dbo -f <data only dump>-prune_tables.sql
# 3) $> psql -d gnumed_vX -U gm-dbo -f <data only dump>
#
# Note that this will DELETE ALL DATA in the database
# you are restoring into.
#
# To speed things up you can replace step 1) with:
#
# 1a) $> cut -f -5 -d " " <data only dump> | grep -E "^(SET)|(INSERT)" > tmp.sql
# 1b) $> python3 gmDBPruningDMLGenerator.py tmp.sql
#
# and use that in step 2):
#
# 2) $> psql -d gnumed_vX -U gm-dbo -f tmp-prune_tables.sql
#
# Note that 1a) will only work on UN*X.
#
# author: Karsten Hilbert
# license: GPL v2 or later
#==============================================================

CONF="/etc/gnumed/gnumed-backup.conf"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


# switched off ? (database name empty)
if [ "$GM_DATABASE" = "" ] ; then
	exit 0
fi


# sanity check
if ! su -c "psql -t -l -p ${GM_PORT}" -l postgres | grep -q "^[[:space:]]*${GM_DATABASE}" ; then
	echo "The configuration in ${CONF} is set to backup"
	echo "the GNUmed database ${GM_DATABASE}. This"
	echo "database does not exist, however. Aborting."
	exit 1
fi


# are we backing up the latest DB ?
OUR_VER=`echo ${GM_DATABASE} | cut -f 2 -d v`
if test -z ${GM_HOST} ; then
	HAS_HIGHER_VER=`sudo -u postgres psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -c "SELECT exists (select 1 from pg_database where datname like 'gnumed_v%' and substring(datname from 9 for 3)::integer > '${OUR_VER}');"`
else
	HAS_HIGHER_VER=`sudo -u postgres psql -A -t -h ${GM_HOST} -d ${GM_DATABASE} -p ${GM_PORT} -c "SELECT exists (select 1 from pg_database where datname like 'gnumed_v%' and substring(datname from 9 for 3)::integer > '${OUR_VER}');"`
fi;

if test "${HAS_HIGHER_VER}" = "t" ; then
	echo "Backing up database ${GM_DATABASE}."
	echo ""
	echo "However, a newer database seems to exist:"
	echo ""
	sudo -u postgres psql -l -p ${GM_PORT} | grep gnumed_v
	echo ""
	echo "Make sure you really want to backup the older database !"
fi ;


TS=`date +%Y-%m-%d-%H-%M-%S`
BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-"`hostname`
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"


cd ${BACKUP_DIR}
if test "$?" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}]. Aborting."
	exit 1
fi


# data only
pg_dump --data-only --column-inserts -v -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-data_only.sql ${GM_DATABASE} 2> /dev/null


# tar and test it
if test -z ${VERIFY_TAR} ; then
	tar -cf ${BACKUP_FILENAME}-data_only.tar ${BACKUP_FILENAME}-data_only.sql
else
	tar -cWf ${BACKUP_FILENAME}-data_only.tar ${BACKUP_FILENAME}-data_only.sql
fi ;
if test "$?" != "0" ; then
	echo "Creating backup tar archive [${BACKUP_FILENAME}-data_only.tar] failed. Aborting."
	exit 1
fi
rm -f ${BACKUP_FILENAME}-data_only.sql


chown ${BACKUP_OWNER} ${BACKUP_FILENAME}-data_only.tar

exit 0

#==============================================================
