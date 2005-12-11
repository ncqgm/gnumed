#!/bin/sh

#======================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/wiki/backup-gm-wiki.sh,v $
# $Id: backup-gm-wiki.sh,v 1.2 2005-12-11 20:44:05 ncq Exp $
# license: GPL
# author: Karsten.Hilbert@gmx.net
#======================================================

BASE="/srv/www/vhosts/twiki/data/Gnumed/"
BAKNAME="GNUmed-Wiki-backup-"`date --utc +%Y-%m-%d-%H-%M-%Z`".tgz"

cd ~/public_html/gnumed/wiki-backup/
tar -cvzf $BAKNAME $BASE
ln -vfs $BAKNAME GNUmed-Wiki-backup.tgz

#======================================================
# $Log: backup-gm-wiki.sh,v $
# Revision 1.2  2005-12-11 20:44:05  ncq
# - publish backups
#
# Revision 1.1  2005/12/11 20:10:30  ncq
# - backup the wiki so the GAU doesn't reoccur
#
