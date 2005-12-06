#!/bin/sh

#========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/XdtViewer/Attic/make-dist.sh,v $
# $Id: make-dist.sh,v 1.3 2005-12-06 22:47:33 shilbert Exp $

echo "making tgz"
tar -cvzhf gnumed-XdtViewer.tgz gmXdtViewer.py gnumed.conf run-xdt-viewer.sh modules locale data
echo "done"

#========================================================
# $Log: make-dist.sh,v $
# Revision 1.3  2005-12-06 22:47:33  shilbert
# - include sample bdt file
#
# Revision 1.2  2003/02/19 15:43:17  ncq
# - add locale
#
# Revision 1.1  2003/02/15 17:14:32  ncq
# - first check in
#
