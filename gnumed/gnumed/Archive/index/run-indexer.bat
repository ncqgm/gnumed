@echo off
REM set your preferred language here
REM set LANG=de_DE@euro

c:\Python22\python.exe .\index-med_docs.py --conf-file=.\gnumed-archive.conf --text-domain=gnumed-archive

REM Delete the XDT file with the patient data
REM del c:\....\patient.dat
