#!/bin/sh

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/Attic/backup-gnumed-database.sh,v $
# $Id: backup-gnumed-database.sh,v 1.4 2007-01-07 23:10:24 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#==============================================================

PGDATABASE="gnumed_v3"
PGPASSWORD="need to set this"

BACKUPDIR="need to set this"
# identify the logical/business-level owner of this
# GNUmed database instance, such as "ACME GP Office",
# do not use spaces: "ACME_GP_Offices"
INSTANCEOWNER="need to set this"
BACKUPOWNER="$USER.$USER"
BACKUPMASK="0600"

#==============================================================
# There really should not be any need to
# change anything below this line.

PGUSER="gm-dbo"
PGPORT="5432"

TS=`date +%Y-%m-%d-%H-%M-%S`
HOST=`hostname`
BACKUPFILE="$BACKUPDIR/backup-$PGDATABASE-$INSTANCEOWNER-$HOST-$TS.sql"

pg_dump -f $BACKUPFILE

chmod $BACKUPMASK $BACKUPFILE
chown $BACKUPOWNER $BACKUPFILE

# GNotary support

#==============================================================
# $Log: backup-gnumed-database.sh,v $
# Revision 1.4  2007-01-07 23:10:24  ncq
# - more documentation
# - add backup file permission mask
#
# Revision 1.3  2006/12/25 22:55:10  ncq
# - comment on gnotary support
#
# Revision 1.2  2006/12/21 19:01:21  ncq
# - add target owner chown
#
# Revision 1.1  2006/12/05 14:48:08  ncq
# - first release of a backup script
#
#