@echo off
REM =================================
REM $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/viewer/Attic/run-viewer.bat,v $
REM $Revision: 1.1 $
REM =================================
REM set your preferred language here
REM set LANG=de_DE@euro

c:\Python22\python.exe .\gmShowMedDocs.py --conf-file=.\gnumed-archive.conf --text-domain=gnumed-archive

REM delete the XDT file with the patient data, but be careful
REM to not delete the file from under the viewer ...
REM pause
REM del c:\....\patient.dat
