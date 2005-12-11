#!/bin/sh

#======================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/wiki/backup-gm-wiki.sh,v $
# $Id: backup-gm-wiki.sh,v 1.1 2005-12-11 20:10:30 ncq Exp $
# license: GPL
# author: Karsten.Hilbert@gmx.net
#======================================================

BASE="/srv/www/vhosts/twiki/data/Gnumed/"
BAKNAME="~/backup/GNUmed-Wiki-backup-"`date --utc +%Y-%m-%d-%H-%M-%Z`".tgz"

tar -cvzf $BAKNAME $BASE

#======================================================
# $Log: backup-gm-wiki.sh,v $
# Revision 1.1  2005-12-11 20:10:30  ncq
# - backup the wiki so the GAU doesn't reoccur
#
