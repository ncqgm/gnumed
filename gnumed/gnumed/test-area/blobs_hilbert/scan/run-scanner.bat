@echo off
REM =================================
REM $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/scan/Attic/run-scanner.bat,v $
REM $Revision: 1.4 $
REM =================================
REM set your preferred language here
set LANG=de_DE@euro

c:\Python22\python.exe .\gmScanMedDocs.py --conf-file=.\gnumed-archive.conf --text-domain=gnumed-archive
