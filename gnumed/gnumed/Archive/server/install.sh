#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/server/Attic/install.sh,v $
# $Revision: 1.1 $

echo "this must be run as root because we will put some links in /usr/bin/ and other places"

# group gnumed
groupadd gnumed

# boostrap database
# FIXME: check returned result: 1 == failed
./bootstrap-gm_db_system.py --conf-file=bootstrap-archive.conf

# install binaries
install -v -g gnumed -m 0750 -b import-med_docs.py run-importer.sh /usr/bin/

# FIXME: install modules
#install -v -g gnumed -m 0750 -d /

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
echo "you must add some users to the system group gnumed"

# cron
echo "you should set up a cron job for regular import of data into the database,"
echo "the command to call regularly is /usr/bin/run-importer.sh"

# config system
echo "you should configure your system in /etc/gnumed/gnumed-archive.conf"

#=============================================================
# $Log: install.sh,v $
# Revision 1.1  2003-03-01 15:01:10  ncq
# - moved here from test-area/blobs_hilbert/
#
# Revision 1.4  2003/02/24 23:10:21  ncq
# - darn it, we do need modules on the server !!
# - I should also check whether bootstrap* fails ...
#
# Revision 1.3  2003/02/02 14:08:49  ncq
# - updated install
# - new bootstrap config file
#
# Revision 1.2  2003/01/27 11:56:00  ncq
# - update links (gmUserSetup.py deprecated)
# - note about user setup in server/install.sh
#
# Revision 1.1  2002/11/29 15:17:02  ncq
# - installation of GnuMed Archive Server
#
