#!/bin/sh

# - this is a wrapper for the scanner,
# - set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#GMSCANMEDDOCS_DIR = ""

python ./gmScanMedDocs.py \
	--conf-file=/home/ncq/.gnumed/gnumed-archiv.conf \
	--text-domain=gnumed-archiv \
	--log-file=/var/log/gnumed/archive-scan.log

#=================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/scan/Attic/run-scanner.sh,v $
# $Revision: 1.4 $

# $Log: run-scanner.sh,v $
# Revision 1.4  2002-11-20 12:56:47  ncq
# - standard log file location
#
