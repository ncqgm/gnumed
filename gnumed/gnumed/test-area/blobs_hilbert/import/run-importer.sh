#!/bin/sh

# this is a wrapper for the importer
# set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#IMPORT-MED_DOCS_DIR = ""

python ./import-med_docs.py \
	--conf-file=/etc/gnumed/gnumed-archive.conf \
	--log-file=/var/log/gnumed/archive-import.log

#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/import/Attic/run-importer.sh,v $
# $Revision: 1.1 $

# $Log: run-importer.sh,v $
# Revision 1.1  2002-12-26 15:54:19  ncq
# - initial checkin
#