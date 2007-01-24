#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/cvs-snapshot/make-cvs_tarball.sh,v $
# $Revision: 1.2 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

BASE=~/gm-cvs-branches/HEAD
ARCHIVE=$HOME/public_html/gnumed/snapshot/gnumed-latest-snapshot.tgz

cd $BASE
tar -cvzf $ARCHIVE gnumed/

#============================================
# $Log: make-cvs_tarball.sh,v $
# Revision 1.2  2007-01-24 15:11:29  ncq
# - proper base dir
#
# Revision 1.1  2006/07/19 11:39:00  ncq
# - add here from elsewhere
#
# Revision 1.2  2005/12/27 17:15:52  ncq
# - backup relative path
#
# Revision 1.1  2005/12/27 17:08:06  ncq
# - make snapshots of the CVS tree
#
