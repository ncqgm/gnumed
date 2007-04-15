@echo off
SET PYTHONPATH="%PYTHONPATH%;../../"
if %1=="" echo "usage: update-db x x+1"

set PREV_VER=%1
set VER=%2
set LOG=update_db-v%PREV_VER%_v%VER%.log
set CONF=update_db-v%PREV_VER%_v%VER%.conf
set GM_CORE_DB=gnumed_v%VER%

echo ===========================================================
echo Bootstrapping GNUmed database.
echo ...
echo This will non-destructively transform a GNUmed database
echo of version v%PREV_VER% into a version v%VER% database.
echo ...
echo The name of the new database will be %GM_CORE_DB% .
echo ===========================================================
echo Dropping target database if there is any.

del %LOG%
echo =======================
echo bootstrapping database
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%