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
if test -z "${TARGET_DB}" ; then
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

{
	echo "-- GNUmed database settings adjustment script"
	echo "-- (created by: $0 $*)"
	echo ""
	echo "\set ON_ERROR_STOP 1"
	echo "\set ECHO queries"
	echo ""
	echo "set default_transaction_read_only to 'off';"
	echo ""
	echo "begin;"
	echo "alter database ${TARGET_DB} set datestyle to 'ISO';"
	echo "alter database ${TARGET_DB} set default_transaction_read_only to 'on';"
	echo "alter database ${TARGET_DB} set default_transaction_isolation to 'read committed';"
	echo "alter database ${TARGET_DB} set lc_messages to 'C';"
	echo "alter database ${TARGET_DB} set password_encryption to 'on';"
	echo "alter database ${TARGET_DB} set synchronous_commit to 'on';"
	echo "alter database ${TARGET_DB} set check_function_bodies to 'on';"
	echo "-- starting with 9.3:"
	echo "alter database ${TARGET_DB} set ignore_checksum_failure to 'off';"
	echo ""
	echo "-- PG < 10 only:"
	echo "--alter database ${TARGET_DB} set sql_inheritance to 'on';"
	echo ""
	echo "-- the following can only be set at server start"
	echo "-- (therefore must be set in postgresql.conf)"
	echo "-- 1) allow_system_table_mods = off"
	echo "-- 2) log_connections = on (only needed for HIPAA compliance)"
	echo "-- 3) log_disconnections = on (only needed for HIPAA compliance)"
	echo "-- 4) fsync = on"
	echo "-- 5) full_page_writes = on"
	echo "-- 6) wal_sync_method = <see PostgreSQL docs>"
	echo "-- 7) track_commit_timestamp = on"
	echo ""
	echo ""
	echo "-- cannot be changed without an initdb (pg_dropcluster/pg_createcluster):"
	echo "-- lc_ctype = *.UTF-8"
	echo "-- server_encoding = UTF8"
	echo ""
	echo "select gm.log_script_insertion('gm-adjust_db_settings.sh', '22.0');"
	echo "commit;"
	echo ""
	echo "-- should be checked in pg_hba.conf in case of client connection problems:"
	echo "--local   samerole    +gm-logins   md5"
	echo "-- should be checked in pg_controldata /var/lib/postgresql/x.y/main output:"
	echo "-- data checksum version != 0"
	echo ""
	echo "-- current relevant settings:"
	echo "select name, setting from pg_settings where name in ('server_version', 'allow_system_table_mods', 'log_connections', 'log_disconnections', 'fsync', 'full_page_writes', 'wal_sync_method', 'track_commit_timestamp', 'data_checksums', 'lc_ctype', 'server_encoding', 'hba_file', 'config_file');"
	echo ""
} > $SQL_FILE


echo ""
echo "==> Adjusting settings of database ${TARGET_DB} ..."
LOG="/tmp/gnumed/$(basename "$0")-$$.log"
sudo -u postgres psql -d "${TARGET_DB}" -f ${SQL_FILE} &> "${LOG}"
if test $? -ne 0 ; then
	echo "    ERROR: failed to adjust database settings. Aborting."
	echo "    LOG  : ${LOG}"
	chmod 0666 "${LOG}"
	exit 1
fi
chmod 0666 "${LOG}"


echo ""
echo "You will now have to take one of the following actions"
echo "to make PostgreSQL recognize some of the changes:"
echo ""
echo "- run 'systemctl stop postgresql.service && systemctl start postgresql.service'"
echo "- run '/etc/init.d/postgresql reload (adjust to version)'"
echo "- run 'pg_ctlcluster <version> <name> reload'"
echo "- run 'pg_ctl reload'"
echo "- stop and restart postgres"
echo "- SIGHUP the server process"
echo "- reboot the machine (Windows)"
echo ""

#==============================================================
