#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-backup_data.sh,v $
# $Id: gm-backup_data.sh,v 1.5 2008-08-01 10:34:21 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# You need to be able to access the GNUmed database as
# user "gm-dbo" by either editing pg_hba.conf or using a
# .pgpass file.
#
# To restore the data-only dump do this:
#
# 1) $> python gmDBPruningDMLGenerator.py <data only dump>
# 2) $> psql -d gnumed_vX -U gm-dbo -f <data only dump>-prune_tables.sql
# 3) $> psql -d gnumed_vX -U gm-dbo -f <data only dump>
#
# Note that this will DELETE ALL DATA in the database
# you are restoring into.
#
# To speed things up you can replace step 1) with:
#
# 1a) $> cut -f -5 -d " " <data only dump> | grep -E "^(SET)|(INSERT)" > tmp.sql
# 1b) $> python gmDBPruningDMLGenerator.py tmp.sql
#
# and use that in step 2):
#
# 2) $> psql -d gnumed_vX -U gm-dbo -f tmp-prune_tables.sql
#
# Note that 1a) will only work on UN*X.
#
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

TS=`date +%Y-%m-%d-%H-%M-%S`
BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-"`hostname`
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"

cd ${BACKUP_DIR}
if test "$?" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}]. Aborting."
	exit 1
fi

# local only
pg_dump --data-only -v -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-data_only.sql 2> /dev/null

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
# $Log: gm-backup_data.sh,v $
# Revision 1.5  2008-08-01 10:34:21  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.4  2007/12/08 15:23:14  ncq
# - minor cleanup
#
# Revision 1.3  2007/12/02 11:45:18  ncq
# - tar the sql so it gets picked up by both the zipping and offsiting script
#
# Revision 1.2  2007/11/04 22:58:45  ncq
# - improved docs
#
# Revision 1.1  2007/11/04 01:40:45  ncq
# - first version
#
#