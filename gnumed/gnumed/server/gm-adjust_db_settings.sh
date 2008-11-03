#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-adjust_db_settings.sh,v $
# $Id: gm-adjust_db_settings.sh,v 1.2 2008-11-03 11:19:28 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# This script can be used to try to adjust database settings
# if the GNUmed client complains about them at startup.
#
#==============================================================

SQL_FILE="/tmp/gm-db-settings.sql"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

TARGET_DB="$1"
if test -z ${TARGET_DB} ; then
	echo "============================================================="
	echo "usage: $0 <target database>"
	echo ""
	echo " <target database>: a GNUmed database (such as \"gnumed_v9\")"
	echo "============================================================="
	exit 1
fi


echo ""
echo "=> Creating adjustment script ..."
echo "    ${SQL_FILE}"

echo "-- GNUmed database settings adjustment script" > $SQL_FILE
echo "-- \$Id: gm-adjust_db_settings.sh,v 1.2 2008-11-03 11:19:28 ncq Exp $" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "\set ON_ERROR_STOP 1" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "set default_transaction_read_only to 'off';" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "begin;" >> $SQL_FILE
echo "alter database ${TARGET_DB} set default_transaction_read_only to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set lc_messages to 'C';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set password_encryption to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set regex_flavor to 'advanced';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set synchronous_commit to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set sql_inheritance to 'on';" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "-- cannot be set after server start:" >> $SQL_FILE
echo "-- alter database ${TARGET_DB} set allow_system_table_mods to 'off';" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "-- cannot be changed now (?):" >> $SQL_FILE
echo "-- alter database ${TARGET_DB} set fsync to 'on';" >> $SQL_FILE
echo "-- alter database ${TARGET_DB} set full_page_writes to 'on';" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "select gm.log_script_insertion('\$RCSfile: gm-adjust_db_settings.sh,v $', '\$Revision: 1.2 $');" >> $SQL_FILE
echo "commit;" >> $SQL_FILE


echo ""
echo "=> Adjusting database ${TARGET_DB} ..."
LOG="gm-db-settings.log"
# FIXME: when 8.2 becomes standard use --single-transaction
sudo -u postgres psql -d ${TARGET_DB} -f ${SQL_FILE} &> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: failed to adjust database settings. Aborting."
	echo "           see: ${LOG}"
	chmod 0666 ${LOG}
	exit 1
fi
chmod 0666 ${LOG}
rm ${SQL_FILE}


echo "You will now have to take one of the following actions"
echo "to make PostgreSQL recognize some of the changes:"
echo ""
echo "- run /etc/init.d/postgresql reload (adjust to version)"
echo "- run pg_ctlcluster <version> <name> reload"
echo "- run pg_ctl reload"
echo "- stop and restart postgres"
echo "- SIGHUP the server process"
echo "- reboot the machine"
echo ""

#==============================================================
# $Log: gm-adjust_db_settings.sh,v $
# Revision 1.2  2008-11-03 11:19:28  ncq
# - improved instructions
#
# Revision 1.1  2008/11/03 11:15:56  ncq
# - new script to adjust db settings
#
#