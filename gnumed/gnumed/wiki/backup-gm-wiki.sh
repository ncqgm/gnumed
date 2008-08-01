#!/bin/bash

#======================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/wiki/backup-gm-wiki.sh,v $
# $Id: backup-gm-wiki.sh,v 1.6 2008-08-01 10:46:53 ncq Exp $
# license: GPL
# author: Karsten.Hilbert@gmx.net
#======================================================

BASE="/srv/www/vhosts/twiki/data/Gnumed/"
#BAKNAME="GNUmed-Wiki-backup-"`date --utc +%Y-%m-%d-%H-%M-%Z`".tgz"

cd ~/public_html/gnumed/wiki-backup/
#tar -cvzf $BAKNAME $BASE
#ln -vfs $BAKNAME GNUmed-Wiki-backup.tgz
tar -cvzf GNUmed-Wiki-backup.tgz $BASE

#======================================================
# $Log: backup-gm-wiki.sh,v $
# Revision 1.6  2008-08-01 10:46:53  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.5  2006/08/10 07:32:45  ncq
# - re-added
#
# Revision 1.3  2005/12/11 21:01:07  ncq
# - make simpler
#
# Revision 1.2  2005/12/11 20:44:05  ncq
# - publish backups
#
# Revision 1.1  2005/12/11 20:10:30  ncq
# - backup the wiki so the GAU doesn't reoccur
#
