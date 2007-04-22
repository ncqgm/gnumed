mklink /J ..\Gnumed ..\client
set PYTHONPATH=..\;%PYTHONPATH%
Python wxpython/gnumed.py --log-file=gm-from-cvs.log --conf-file=gm-from-cvs.conf --debug

