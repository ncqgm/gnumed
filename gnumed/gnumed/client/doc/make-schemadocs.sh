#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-schemadocs.sh,v $
# $Revision: 1.2 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

# this only really works on hherb.com
/usr/local/bin/postgresql_autodoc -d gnumed -f ~/gm-schemadocs/gnumed-schema -t html &> ~/schemadocs.log

#============================================
# $Log: make-schemadocs.sh,v $
# Revision 1.2  2004-07-15 06:28:46  ncq
# - fixed some pathes
#
# Revision 1.1  2004/07/15 06:25:32  ncq
# - first checkin
