#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-dumps.sh,v $
# $Revision: 1.12 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

DB=gnumed_v11

SCHEMADUMP=~/gm-schemadocs/gm-schema-dump.sql
DATADUMP=~/gm-schemadocs/gm-data-dump.sql
GMDUMP=~/gm-schemadocs/gm-db-dump.tgz

pg_dump -i -f $SCHEMADUMP -F p -C -s -U gm-dbo $DB
pg_dump -i -f $DATADUMP -F p -a -D -U gm-dbo $DB

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP

#============================================
# $Log: make-dumps.sh,v $
# Revision 1.12  2009-06-11 13:02:32  ncq
# - bump version
#
# Revision 1.11  2009/04/05 09:20:35  ncq
# - add -i
#
# Revision 1.10  2009/04/03 11:08:07  ncq
# - bump db version
#
# Revision 1.9  2008/08/01 10:08:49  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.8  2008/01/07 19:45:11  ncq
# - bump db version
#
# Revision 1.7  2007/10/22 12:37:02  ncq
# - default database change
#
# Revision 1.6  2007/09/24 18:26:19  ncq
# - v5 -> v7
#
# Revision 1.5  2007/03/31 21:19:07  ncq
# - work with gnumed_v5
#
# Revision 1.4  2007/01/24 10:59:58  ncq
# - dump gnumed_v4 for now
#
# Revision 1.3  2005/12/09 20:43:25  ncq
# - improved output
#
# Revision 1.2  2005/02/21 16:45:48  ncq
# - improve naming
#
# Revision 1.1  2005/02/21 16:37:09  ncq
# - generate snapshot database dumps for people to try out
#
#
