@echo off
rem SET PYTHONPATH="%PYTHONPATH%;../../"

set VER=3
set LOG=update_db-v2_v%VER%.log
set CONF=update_db-v2_v%VER%.conf

rem set GM_CORE_DB=gnumed_v%VER%_cp
set GM_CORE_DB=gnumed_v%VER%

echo ===========================================================
echo Bootstrapping GNUmed database.
echo ...
echo This will non-destructively transform a GNUmed database
echo of version v2 into a version v%VER% database.
echo ...
echo The name of the new database will be %GM_CORE_DB% .
echo ===========================================================
echo Dropping target database if there is any.

dropdb -U gm-dbo -i %GM_CORE_DB%
del %LOG%
echo =======================
echo bootstrapping database
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
