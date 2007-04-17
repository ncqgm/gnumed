@echo off
SET PYTHONPATH="%PYTHONPATH%;../../"
if %1=="" echo "usage: update-db x x+1"

set PREV_VER=%1
set NEXT_VER=%2
set LOG=update_db-v%PREV_VER%_v%NEXT_VER%.log
set CONF=update_db-v%PREV_VER%_v%NEXT_VER%.conf
set GM_CORE_DB=gnumed_v%NEXT_VER%

echo ===========================================================
echo Bootstrapping GNUmed database.
echo ...
echo This will non-destructively transform a GNUmed database
echo of version v%PREV_VER% into a version v%NEXT_VER% database.
echo ...
echo The name of the new database will be %GM_CORE_DB% .
echo ===========================================================

del %LOG%
echo =======================
echo bootstrapping database
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%