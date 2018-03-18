@echo off

SET DRIVE_LTR=%~d0
cd /d %~dp0
REM command line options:
REM quiet

SET VER=22
SET PREV_VER=21
SET LASTVERSIONSTODROP=20
SET QUIET=%1

SET PYTHONPATH="%PYTHONPATH%;../../"


echo ===========================================================
echo Bootstrapping latest GNUmed database.

echo This will set up a GNUmed database of version %VER%
echo with the name gnumed_v%VER%
echo It contains all the currently working parts including
echo localizations for countries you don't live in. This does
echo not disturb the operation of the GNUmed client in your
echo country in any way.
echo ===========================================================

echo bootstrapping databases ...

COLOR 0E
SET LOG=bootstrap-latest.log
SET CONF=bootstrap-latest.conf
bootstrap_gm_db_system.py --log-file=%LOG% --conf-file=%CONF%


echo ============================================================
echo Dropping staging databases. You might have to enter the 
echo password for 'postgres' unless it is provided.
echo ============================================================

for /l %%X in (2,1,%LASTVERSIONSTODROP%) do dropdb -U postgres gnumed_v%%X
