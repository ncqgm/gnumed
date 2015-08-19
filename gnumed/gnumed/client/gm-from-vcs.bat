REM # GNUmed tarball startup batch file

REM # normally we would like to use a link but Python
REM # on Windows seems to have problems importing
REM # modules from directory links
REM mklink /J ..\Gnumed ..\client

REM # hence we use xcopy: http://commandwindows.com/xcopy.htm
REM # note that no (old) link should pre-exist lest we overwrite ourselves
xcopy ..\client ..\Gnumed /E /I /F /H /O /Y

set PYTHONPATH=..;%PYTHONPATH%

Python gnumed.py --log-file=gm-from-vcs.log --conf-file=gm-from-vcs.conf --local-import --debug

