#!/bin/bash

#==============================================================
# This script can be used to try to adjust database settings
# if the GNUmed client complains about them at startup.
#
# usage: ./gm-adjust_db_settings.sh <database name>
#
# author: Karsten Hilbert
# license: GPL v2 or later
#
#==============================================================

SQL_FILE="/tmp/gnumed/gm-db-settings-$$.sql"

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
echo "==> Creating database settings adjustment SQL script ..."
echo "    ${SQL_FILE}"

mkdir -p /tmp/gnumed

echo "-- GNUmed database settings adjustment script" > $SQL_FILE
echo "-- (created by: $0 $*)" >> $SQL_FILE
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
echo "" >> $SQL_FILE
echo "-- starting with 9.3 (remove when 9.3 is required):" >> $SQL_FILE
echo "\unset ON_ERROR_STOP" >> $SQL_FILE
echo "alter database ${TARGET_DB} set ignore_checksum_failure to 'off';     -- comment out if the script fails" >> $SQL_FILE
echo "\set ON_ERROR_STOP 1" >> $SQL_FILE
echo "" >> $SQL_FILE
echo "-- < PG 9.0 only:" >> $SQL_FILE
echo "--\unset ON_ERROR_STOP" >> $SQL_FILE
echo "--alter database ${TARGET_DB} set regex_flavor to 'advanced';" >> $SQL_FILE
echo "--\set ON_ERROR_STOP 1" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- the following can only be set at server start" >> $SQL_FILE
echo "-- (therefore must be set in postgresql.conf)" >> $SQL_FILE
echo "-- 1) allow_system_table_mods = off" >> $SQL_FILE
echo "-- 2) log_connections = on (only needed for HIPAA compliance)" >> $SQL_FILE
echo "-- 3) log_disconnections = on (only needed for HIPAA compliance)" >> $SQL_FILE
echo "-- 4) fsync = on" >> $SQL_FILE
echo "-- 5) full_page_writes = on" >> $SQL_FILE
echo "-- 6) wal_sync_method = <see PostgreSQL docs>" >> $SQL_FILE
echo "-- 7) track_commit_timestamp = on" >> $SQL_FILE
echo "" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- cannot be changed without an initdb (pg_dropcluster):" >> $SQL_FILE
echo "-- lc_ctype = *.UTF-8" >> $SQL_FILE
echo "-- server_encoding = UTF8"

echo "" >> $SQL_FILE
echo "select gm.log_script_insertion('gm-adjust_db_settings.sh', '19.1');" >> $SQL_FILE
echo "commit;" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- should be checked in pg_hba.conf in case of client connection problems:" >> $SQL_FILE
echo "--local   samerole    +gm-logins   md5" >> $SQL_FILE
echo "-- should be checked in pg_controldata /var/lib/postgresql/x.y/main output:" >> $SQL_FILE
echo "-- data checksum version != 0" >> $SQL_FILE

echo "" >> $SQL_FILE
echo "-- current relevant settings:" >> $SQL_FILE
echo "select name, setting from pg_settings where name in ('allow_system_table_mods', 'log_connections', 'log_disconnections', 'fsync', 'full_page_writes', 'wal_sync_method', 'lc_ctype', 'server_encoding', 'hba_file', 'config_file');" >> $SQL_FILE
echo "" >> $SQL_FILE

echo ""
echo "==> Adjusting settings of database ${TARGET_DB} ..."
LOG="/tmp/gnumed/$(basename $0)-$$.log"
sudo -u postgres psql -d ${TARGET_DB} -f ${SQL_FILE} &> ${LOG}
if test $? -ne 0 ; then
	echo "    ERROR: failed to adjust database settings. Aborting."
	echo "    LOG  : ${LOG}"
	chmod 0666 ${LOG}
	exit 1
fi
chmod 0666 ${LOG}


echo ""
echo "You will now have to take one of the following actions"
echo "to make PostgreSQL recognize some of the changes:"
echo ""
echo "- run '/etc/init.d/postgresql reload (adjust to version)'"
echo "- run 'pg_ctlcluster <version> <name> reload'"
echo "- run 'pg_ctl reload'"
echo "- stop and restart postgres"
echo "- SIGHUP the server process"
echo "- reboot the machine (Windows)"
echo ""

#==============================================================
