#!/bin/sh

# this is a wrapper for the indexer
# set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#INDEX-MED_DOCS_DIR = ""

CONF=/home/ncq/.gnumed/gnumed-archive.conf
LOG=/var/log/gnumed/archive-index.log

python ./index-med_docs.py \
	--conf-file=$CONF \
	--text-domain=gnumed \
	--log-file=$LOG

#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/index/Attic/run-indexer.sh,v $
# $Revision: 1.2 $

# $Log: run-indexer.sh,v $
# Revision 1.2  2003-04-20 15:31:06  ncq
# - cleaner argument handling
#
# Revision 1.1  2003/04/06 09:43:14  ncq
# - moved here from test-area/blobs_hilbert/
#
# Revision 1.3  2002/11/30 20:01:59  ncq
# - fix view() in show-med_docs
# - fix archiv -> archive
#
# Revision 1.2  2002/11/20 12:55:13  ncq
# - standard log file location
#
