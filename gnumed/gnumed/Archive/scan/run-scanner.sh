#!/bin/sh

# - this is a wrapper for the scanner,
# - set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#GMSCANMEDDOCS_DIR = ""

python ./gmScanMedDocs.py \
	--conf-file=/home/ncq/.gnumed/gnumed-archive.conf \
	--text-domain=gnumed-archive \
	--log-file=/var/log/gnumed/archive-scan.log

#=================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/scan/Attic/run-scanner.sh,v $
# $Revision: 1.1 $

# $Log: run-scanner.sh,v $
# Revision 1.1  2003-04-13 13:47:22  ncq
# - moved here from test_area
#
# Revision 1.5  2002/11/30 20:01:59  ncq
# - fix view() in show-med_docs
# - fix archiv -> archive
#
# Revision 1.4  2002/11/20 12:56:47  ncq
# - standard log file location
#
