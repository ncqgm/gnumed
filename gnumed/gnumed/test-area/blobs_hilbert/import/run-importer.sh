#!/bin/sh

# this is a wrapper for the importer
# set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#IMPORT-MED_DOCS_DIR = ""

LOG=/var/log/gnumed/archive-import.log
CFG=/etc/gnumed/gnumed-archive.conf

echo > $LOG
cd /usr/bin
import-med_docs.py \
 --conf-file=$CFG \
 --log-file=$LOG
cd -

#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/import/Attic/run-importer.sh,v $
# $Revision: 1.2 $

# $Log: run-importer.sh,v $
# Revision 1.2  2003-02-23 20:39:12  ncq
# - eating your own dog-food makes you find lots of inconsistencies
#
# Revision 1.1  2002/12/26 15:54:19  ncq
# - initial checkin
#