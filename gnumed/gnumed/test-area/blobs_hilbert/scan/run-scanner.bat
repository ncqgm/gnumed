@echo off
REM set your preferred language here
set LANG=de_DE@euro

c:\Python22\python.exe .\scan-med_docs.py --conf-file=.\gnumed-archiv.conf --text-domain=gnumed-archiv
