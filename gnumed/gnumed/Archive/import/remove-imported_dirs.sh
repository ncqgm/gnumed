#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/import/Attic/remove-imported_dirs.sh,v $
# $Revision: 1.2 $
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
		echo $DIR
		echo "this dir can be deleted"
		echo "but you must manually activate that"

		# kill 'em
		#rm -f $DIR/* && rmdir -f $DIR

		# or move 'em about
		#mv -f --strip-trailing-slashes $DIR $BACKUP
	fi
done

#==============================================================
# $Log: remove-imported_dirs.sh,v $
# Revision 1.2  2003-04-18 16:38:17  ncq
# - better docs in remove*dirs
# - install binaries on server
# - text domain "gnumed" in run-viewer.bat
#
# Revision 1.1  2003/03/01 15:39:49  ncq
# - moved here from test-area
#
# Revision 1.2  2002/12/25 16:03:51  ncq
# - proofread, debugging
#
# Revision 1.1  2002/12/23 08:51:29  ncq
# - the remove script belongs into import/ of course
#
