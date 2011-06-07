#!/bin/bash

#==============================================================
# This script can be used to try to adjust database settings
# if the GNUmed client complains about them at startup.
#
# usage: ./gm-adjust_db_settings.sh <database name>
#
# author: Karsten Hilbert
# license: GPL v2
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
	echo " <target database>: a GNUmed database (such as \"gnumed_vNN\")"
	echo "============================================================="
	exit 1
fi


echo ""
echo "=> Creating adjustment script ..."
echo "    ${SQL_FILE}"

echo "-- GNUmed database settings adjustment script" > $SQL_FILE
echo "-- (gm-adjust_db_settings.sh)" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "\set ON_ERROR_STOP 1" >> $SQL_FILE
echo "\set ECHO queries" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "set default_transaction_read_only to 'off';" >> $SQL_FILE
echo "" >> $SQL_FILE

echo "begin;" >> $SQL_FILE
echo "alter database ${TARGET_DB} set datestyle to 'ISO';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set default_transaction_read_only to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set default_transaction_isolation to 'read committed';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set lc_messages to 'C';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set password_encryption to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set synchronous_commit to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set sql_inheritance to 'on';" >> $SQL_FILE
echo "alter database ${TARGET_DB} set check_function_bodies to 'on';" >> $SQL_FILE
echo "-- < PG 9.0 only:"
echo "--alter database ${TARGET_DB} set regex_flavor to 'advanced';" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- cannot be set after server start:" >> $SQL_FILE
echo "--alter database ${TARGET_DB} set allow_system_table_mods to 'off';" >> $SQL_FILE
echo "-- (only needed for HIPAA compliance):" >> $SQL_FILE
echo "--alter database ${TARGET_DB} set log_connections to 'on';" >> $SQL_FILE
echo "--alter database ${TARGET_DB} set log_disconnections to 'on';" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- cannot be changed now (?):" >> $SQL_FILE
echo "--alter database ${TARGET_DB} set fsync to 'on';" >> $SQL_FILE
echo "--alter database ${TARGET_DB} set full_page_writes to 'on';" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "select gm.log_script_insertion('gm-adjust_db_settings.sh', 'v16');" >> $SQL_FILE
echo "commit;" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- cannot be changed without an initdb (pg_dropcluster):" >> $SQL_FILE
echo "select name, setting from pg_settings where name in ('lc_ctype', 'server_encoding');" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- should be checked in pg_hba.conf in case of client connection problems:" >> $SQL_FILE
echo "--local   samegroup   +gm-logins   md5" >> $SQL_FILE



echo ""
echo "=> Adjusting database ${TARGET_DB} ..."
LOG="gm-db-settings.log"
sudo -u postgres psql -d ${TARGET_DB} --single-transaction -f ${SQL_FILE} &> ${LOG}
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
