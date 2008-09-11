@echo off

REM ========================================================
REM Upgrade GNUmed database from version to version.
REM
REM usage:
REM  upgrade-db.sh vX vX+1 <secrets>
REM
REM limitations:
REM  Only works from version to version sequentially.
REM
REM prerequisites:
REM  update_db-vX_vX+1.conf must exist
REM
REM "secret" command line options:
REM  no-backup
REM  - don't create a database backup (you got faith)
REM  no-compression
REM  - create a backup but don't compress it (you got plenty of disk but REM run low on cycles)
REM  quiet
REM  - display failures only, don't chatter
REM
REM ========================================================


REM SET PYTHONPATH="%PYTHONPATH%;../../"


SET PREV_VER=%1
SET NEXT_VER=%2
SET SKIP_BACKUP=%3
SET BZIP_BACKUP=%3
SET QUIET=%3
SET LOG_BASE=.
SET LOG=%LOG_BASE%\update_db-v%PREV_VER%_v%NEXT_VER%.log
SET CONF=update_db-v%PREV_VER%_v%NEXT_VER%.conf
SET BAK_FILE=backup-upgrade-v%PREV_VER%-to-v%NEXT_VER%.sql


if %1=="" echo "usage: update-db x x+1"

REM if you need to adjust the database name to something
REM other than what the config file has you can use the
REM following environment variable:
REM SET GM_CORE_DB=gnumed_v%NEXT_VER%

REM if you need to adjust the port you want to use to
REM connect to PostgreSQL you can use the environment
REM variable below (this may be necessary if your PostgreSQL
REM server is running on a port different from the default 5432)
REM SET GM_DB_PORT=5433



echo ===========================================================
echo Upgrading GNUmed database.
echo ...
echo This will non-destructively transform a GNUmed database
echo of version v%NEXT_VER% from an existing version v%PREV_VER% database.
echo Existing data is transferred and transformed as necessary.
echo ...
echo The name of the new database will be gnumed_v%NEXT_VER% .
echo ===========================================================


echo 2) upgrading to new database ...
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF% %QUIET
