@echo off

SET DRIVE_LTR=%~d0
cd /d %~dp0
REM should be run as root
REM command line options:
REM  quiet

SET VER=13
SET PREV_VER=12
SET QUIET=%1

SET PYTHONPATH="%PYTHONPATH%;../../"

set GM_CORE_DB=gnumed_v%VER%


echo ===========================================================
echo Bootstrapping latest GNUmed database.

echo This will set up a GNUmed database of version v%VER%
echo with the name %GM_CORE_DB%
REM echo It contains all the currently working parts including
REM echo localizations for countries you don't live in. This does
REM echo not disturb the operation of the GNUmed client in your
REM echo country in any way.
echo ===========================================================




rem echo 1) Dropping old baseline gnumed_v2 database if there is any.
rem dropdb -U gm-dbo -i gnumed_v2
del %LOG%

echo ==========================
echo 2) bootstrapping databases


REM baseline v2
COLOR 0E
SET LOG=bootstrap-latest-v2.log
SET CONF=redo-v2.conf
SET GM_CORE_DB=gnumed_v2
bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%
set GM_CORE_DB=

REM v2 -> v3
COLOR 0A
call upgrade-db.bat 2 3

REM v3 -> v4
COLOR 0F
call upgrade-db.bat 3 4

REM v4 -> v5
COLOR 07
call upgrade-db.bat 4 5

REM v5 -> v6
COLOR F9
call upgrade-db.bat 5 6

REM v6 -> v7
COLOR 0E
call upgrade-db.bat 6 7

REM v7 -> v8
COLOR 0A
call upgrade-db.bat 7 8

REM v8 -> v9
COLOR 0F
call upgrade-db.bat 8 9

REM v9 -> v10
COLOR 07
call upgrade-db.bat 9 10

REM v10 -> v11
COLOR F9
call upgrade-db.bat 10 11

REM v11 -> v12
COLOR 0E
call upgrade-db.bat 11 12

REM v12 -> v13
COLOR 0A
call upgrade-db.bat 12 13

dropdb -U gm-dbo gnumed_v2
dropdb -U gm-dbo gnumed_v3
dropdb -U gm-dbo gnumed_v4
dropdb -U gm-dbo gnumed_v5
dropdb -U gm-dbo gnumed_v6
dropdb -U gm-dbo gnumed_v7
dropdb -U gm-dbo gnumed_v8
dropdb -U gm-dbo gnumed_v9
dropdb -U gm-dbo gnumed_v10
dropdb -U gm-dbo gnumed_v11
