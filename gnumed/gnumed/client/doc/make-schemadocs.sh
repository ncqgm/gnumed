#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-schemadocs.sh,v $
# $Revision: 1.1 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

# this only really works on hherb.com
/usr/local/bin/postgresql_autodoc -d gnumed -f gnumed-schema -t html

#============================================
# $Log: make-schemadocs.sh,v $
# Revision 1.1  2004-07-15 06:25:32  ncq
# - first checkin
#
# Revision 1.1  2004/07/14 10:11:04  ncq
# - first checkin
#
