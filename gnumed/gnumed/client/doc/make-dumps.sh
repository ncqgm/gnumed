#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-dumps.sh,v $
# $Revision: 1.2 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

SCHEMADUMP=~/gm-schemadocs/gm-schema-dump.sql
DATADUMP=~/gm-schemadocs/gm-data-dump.sql
GMDUMP=~/gm-schemadocs/gm-db-dump.tgz

pg_dump -f $SCHEMADUMP -F p -C -s -U gm-dbo gnumed
pg_dump -f $DATADUMP -F p -a -D -U gm-dbo gnumed

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP

#============================================
# $Log: make-dumps.sh,v $
# Revision 1.2  2005-02-21 16:45:48  ncq
# - improve naming
#
# Revision 1.1  2005/02/21 16:37:09  ncq
# - generate snapshot database dumps for people to try out
#
#
