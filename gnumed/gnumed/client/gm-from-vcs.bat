mklink /J ..\Gnumed ..\client
set PYTHONPATH=..\;%PYTHONPATH%
Python wxpython/gnumed.py --log-file=gm-from-vcs.log --conf-file=gm-from-vcs.conf --debug

