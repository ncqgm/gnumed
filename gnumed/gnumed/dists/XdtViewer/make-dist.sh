#!/bin/sh

#========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/XdtViewer/Attic/make-dist.sh,v $
# $Id: make-dist.sh,v 1.1 2003-02-15 17:14:32 ncq Exp $

echo "making tgz"
tar -cvzhf gnumed-XdtViewer.tgz gmXdtViewer.py run-xdt-viewer.sh modules
echo "done"

#========================================================
# $Log: make-dist.sh,v $
# Revision 1.1  2003-02-15 17:14:32  ncq
# - first check in
#
