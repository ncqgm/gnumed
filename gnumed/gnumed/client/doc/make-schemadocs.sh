#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-schemadocs.sh,v $
# $Revision: 1.13 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

DB=gnumed_v5

export PGUSER="gm-dbo"
postgresql_autodoc -d $DB -f ~/gm-schemadocs/gnumed-schema -t html
postgresql_autodoc -d $DB -f ~/gm-schemadocs/gnumed-schema -t dot
postgresql_autodoc -d $DB -f ~/gm-schemadocs/gnumed-schema -t dia
postgresql_autodoc -d $DB -f ~/gm-schemadocs/gnumed-schema -t zigzag.dia

grep -v log_ ~/gm-schemadocs/gnumed-schema.dot > ~/gm-schemadocs/gnumed-schema-no_audit.dot

dot -Tpng -o ~/gm-schemadocs/gnumed-schema.png ~/gm-schemadocs/gnumed-schema-no_audit.dot

#============================================
# $Log: make-schemadocs.sh,v $
# Revision 1.13  2007-03-31 21:19:07  ncq
# - work with gnumed_v5
#
# Revision 1.12  2007/01/24 11:01:18  ncq
# - document v4 schema for now
#
# Revision 1.11  2006/01/07 09:06:24  ncq
# - remove audit tables from schema ER diagram
#
# Revision 1.10  2005/12/23 16:24:18  ncq
# - remove absolute path prefix on pg autodoc binary
#
# Revision 1.9  2005/12/09 20:43:25  ncq
# - improved output
#
# Revision 1.8  2005/01/25 17:35:03  ncq
# - Thilo wanted the other formats, too, so here it is ...
#
# Revision 1.7  2005/01/19 09:27:59  ncq
# - let callers deal with output, don't predefine target as file (cron mails it)
#
# Revision 1.6  2005/01/12 14:47:48  ncq
# - in DB speak the database owner is customarily called dbo, hence use that
#
# Revision 1.5  2005/01/10 12:26:40  ncq
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
