@echo off
SET PYTHONPATH="%PYTHONPATH%;../../"


SET VER=6
set GM_CORE_DB=gnumed_v%VER%

echo ===========================================================
echo Bootstrapping latest GNUmed database.

echo This will set up a GNUmed database of version v%VER%
echo with the name %GM_CORE_DB%
echo It contains all the currently working parts including
echo localizations for countries you don't live in. This does
echo not disturb the operation of the GNUmed client in your
echo country in any way.
echo ===========================================================
echo 1) Dropping old baseline gnumed_v2 database if there is any.
dropdb -U gm-dbo -i gnumed_v2
del %LOG%

echo ==========================
echo 2) bootstrapping databases

COLOR 0E
SET LOG=bootstrap-latest-v2.log
SET CONF=redo-v2.conf
SET GM_CORE_DB=gnumed_v2
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
set GM_CORE_DB=

COLOR 0A
SET LOG=bootstrap-latest-v3.log
SET CONF=update_db-v2_v3.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v2

COLOR 0F
SET LOG=bootstrap-latest-v4.log
SET CONF=update_db-v3_v4.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v3

COLOR 07
SET LOG=bootstrap-latest-v5.log
SET CONF=update_db-v4_v5.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v4

COLOR F9
SET LOG=bootstrap-latest-v6.log
SET CONF=update_db-v5_v6.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v5

COLOR 0E
SET LOG=bootstrap-latest-v7.log
SET CONF=update_db-v6_v7.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v6

COLOR 0A
SET LOG=bootstrap-latest-v8.log
SET CONF=update_db-v7_v8.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v7

COLOR 0F
SET LOG=bootstrap-latest-v9.log
SET CONF=update_db-v8_v9.conf
python bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
dropdb -U gm-dbo gnumed_v8

