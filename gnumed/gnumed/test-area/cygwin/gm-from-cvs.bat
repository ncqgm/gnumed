
echo must setup python files  by doing bash cygwin_path.sh once.
echo this .bat file is run from client\ directory
set PYTHONPATH=..\;%PYTHONPATH%
set PATH=%PATH%;c:\\Python2.3
Python wxpython/gnumed.py --log-file=gm-from-cvs.bat.log --debug

