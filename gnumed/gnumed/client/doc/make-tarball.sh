#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/Attic/make-tarball.sh,v $
# $Revision: 1.1 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

BASE=~/gm-cvs-head/gnumed/
ARCHIVE=$HOME/public_html/gnumed/snapshot/gnumed-latest-snapshot.tgz

tar -cvzf $ARCHIVE $BASE

#============================================
# $Log: make-tarball.sh,v $
# Revision 1.1  2005-12-27 17:08:06  ncq
# - make snapshots of the CVS tree
#
#
