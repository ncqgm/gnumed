#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-dumps.sh,v $
# $Revision: 1.6 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

SCHEMADUMP=~/gm-schemadocs/gm-schema-dump.sql
DATADUMP=~/gm-schemadocs/gm-data-dump.sql
GMDUMP=~/gm-schemadocs/gm-db-dump.tgz
DB=gnumed_v7

pg_dump -f $SCHEMADUMP -F p -C -s -U gm-dbo $DB
pg_dump -f $DATADUMP -F p -a -D -U gm-dbo $DB

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP

#============================================
# $Log: make-dumps.sh,v $
# Revision 1.6  2007-09-24 18:26:19  ncq
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
