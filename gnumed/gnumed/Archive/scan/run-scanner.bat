@echo off
REM =================================
REM $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/scan/Attic/run-scanner.bat,v $
REM $Revision: 1.1 $
REM =================================
REM set your preferred language here
set LANG=de_DE@euro

c:\Python22\python.exe .\gmScanMedDocs.py --conf-file=.\gnumed-archive.conf --text-domain=gnumed-archive
