#!/bin/bash

#======================================================
# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net
#======================================================

#BASE="/srv/www/vhosts/twiki/data/Gnumed/"
#BAKNAME="GNUmed-Wiki-backup-"`date --utc +%Y-%m-%d-%H-%M-%Z`".tgz"
#tar -cvzf $BAKNAME $BASE
#ln -vfs $BAKNAME GNUmed-Wiki-backup.tgz

BASE="/srv/www/vhosts/Foswiki-1.1.5/data/Gnumed/"
cd ~/public_html/gnumed/wiki-backup/
tar -cvzf GNUmed-Wiki-backup.tgz $BASE

#======================================================
