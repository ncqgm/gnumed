#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/import/Attic/remove-imported_dirs.sh,v $
# $Revision
# GnuMed, GPL, Karsten.Hilbert@gmx.net

# this will delete/move data that has been successfully imported

# you need to adjust these values to what you have in
# your GnuMed/Archive config file
REPOSITORY=~/gnumed/scans/*
DONEFILE="imported.txt"

# set this if you want to keep backups on disk
BACKUP="/somewhere/"

for DIR in $REPOSITORY ; do
	if test -f $DIR/$DONEFILE; then
		# those are the ones we want deleted
		DUMMY="dummy"

		# kill 'em
		#rm -f $DIR/* && rmdir -f $DIR

		# or move 'em about
		#mv -f --strip-trailing-slashes $DIR $BACKUP
	fi
done

#==============================================================
# $Log: remove-imported_dirs.sh,v $
# Revision 1.1  2002-12-23 08:51:29  ncq
# - the remove script belongs into import/ of course
#
