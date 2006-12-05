#!/bin/sh

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/Attic/backup-gnumed-database.sh,v $
# $Id: backup-gnumed-database.sh,v 1.1 2006-12-05 14:48:08 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#==============================================================

PGDATABASE="gnumed_v3"
PGPASSWORD="need to set this"

BACKUPDIR="need to set this"
# identify the logical/business-level owner of this
# GNUmed database instance
INSTANCEOWNER="need to set this"

#==============================================================
# There really should not be any need to
# change anything below this line.

PGUSER="gm-dbo"
PGPORT="5432"

TS=`date +%Y-%m-%d-%H-%M-%S`
HOST=`hostname`
BACKUPFILE="$BACKUPDIR/backup-$PGDATABASE-$INSTANCEOWNER-$HOST-$TS.sql"

pg_dump -f $BACKUPFILE

#==============================================================
# $Log: backup-gnumed-database.sh,v $
# Revision 1.1  2006-12-05 14:48:08  ncq
# - first release of a backup script
#
#