#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/server/Attic/install.sh,v $
# $Revision: 1.1 $

echo "this must be run as root because we will put some links in /usr/bin/ and other places"

# group gnumed
groupadd gnumed

# boostrap database
./bootstrap-gm_db_system.py

# install binaries
install -v -g gnumed -m 0750 -b import-med_docs.py run-importer.sh /usr/bin/

# install message catalog
echo "no need for message catalog installation"

# install config files
install -v -g gnumed -m 0750 -d /etc/gnumed/
install -v -g gnumed -m 0660 -b gnumed-archive.conf /etc/gnumed/

# log file
touch archive-import.log
install -v -g gnumed -m 0750 -d /var/log/gnumed/
install -v -g gnumed -m 0660 -b archive-import.log /var/log/gnumed/

# repository for clients
echo "you must set up and configure a data repository for clients"

# add root to group gnumed
echo "you must add some users to group gnumed"

# cron
echo "you should set up a cron job for regular import of data into the database,"
echo "the command to call regularly is /usr/bin/run-importer.sh"

# config system
echo "you should configure your system in /etc/gnumed/gnumed-archive.conf"


#=============================================================
# $Log: install.sh,v $
# Revision 1.1  2002-11-29 15:17:02  ncq
# - installation of GnuMed Archive Server
#
