mklink /J ..\Gnumed ..\client
set PYTHONPATH=..\;%PYTHONPATH%
Python gnumed.py --log-file=gm-from-vcs.log --conf-file=gm-from-vcs.conf --debug

