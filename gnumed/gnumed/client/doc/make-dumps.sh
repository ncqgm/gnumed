#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-dumps.sh,v $
# $Revision: 1.1 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

TODAY=`date -I`
SCHEMADUMP=~/gm-schemadocs/gm-schema-dump-$TODAY.sql
DATADUMP=~/gm-schemadocs/gm-schema-dump-$TODAY.sql
GMDUMP=~/gm-schemadocs/gm-dump-$TODAY.tgz

pg_dump -f $SCHEMADUMP -F p -C -s -U gm-dbo gnumed
pg_dump -f $DATADUMP -F p -a -D -U gm-dbo gnumed

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP

#============================================
# $Log: make-dumps.sh,v $
# Revision 1.1  2005-02-21 16:37:09  ncq
# - generate snapshot database dumps for people to try out
#
#
