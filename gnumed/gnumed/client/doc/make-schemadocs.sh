#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-schemadocs.sh,v $
# $Revision: 1.5 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

export PGUSER="gm-dbowner"
/usr/local/bin/postgresql_autodoc -d gnumed -f ~/gm-schemadocs/gnumed-schema -t html &> ~/schemadocs.log

#============================================
# $Log: make-schemadocs.sh,v $
# Revision 1.5  2005-01-10 12:26:40  ncq
# - properly installing pg_autodoc on Carlos' machine should help
#
# Revision 1.4  2005/01/10 12:06:13  ncq
# - tell pg autodoc to act as gm-dbowner
#
# Revision 1.3  2005/01/06 19:21:29  ncq
# - adjust for running on Carlos' server
#
# Revision 1.2  2004/07/15 06:28:46  ncq
# - fixed some pathes
#
# Revision 1.1  2004/07/15 06:25:32  ncq
# - first checkin
