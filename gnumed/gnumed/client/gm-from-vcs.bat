REM # GNUmed tarball startup batch file

REM # normally we would like to use a link but Python
REM # on Windows seems to have problems importing
REM # modules from directory links
REM mklink /J ..\Gnumed ..\client

REM # hence we use xcopy: http://commandwindows.com/xcopy.htm
REM # but need to remove old link first (if any)
fsutil reparsepoint delete ..\Gnumed
REM # if it still exists it shouldn't be a link, so remove the directory now
rmdir ..\Gnumed /s
xcopy ..\client ..\Gnumed /E /I /F /H /O /Y

set PYTHONPATH=..;%PYTHONPATH%

REM echo Log file: ./gm-from-vcs.log
Python3 gnumed.py --log-file=gm-from-vcs.log --conf-file=gm-from-vcs.conf --local-import --debug

