#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/client/Attic/install.sh,v $
# $Revision: 1.1 $

echo "this must be run as root because we will put some stuff in /usr/bin/ and other places"

# group gnumed
groupadd gnumed

# install binaries
echo "installing binaries"
install -v -g gnumed -m 0750 -b \
	gmScanMedDocs.py run-scanner.sh \
	index-med_docs.py run-indexer.sh \
	show-med_docs.py run-viewer.sh \
	/usr/bin/

# install modules
echo "installing GnuMed python modules"
install -v -g gnumed -m 0750 -d /usr/share/gnumed/
install -v -g gnumed -m 0750 -d /usr/share/gnumed/python-common/
install -v -g gnumed -m 0660 -b modules/* /usr/share/gnumed/python-common/

# install message catalog
echo "installing language translation files"
echo "German..."
install -v -g root -m 0644 locale/de_DE@euro/LC_MESSAGES/gnumed-archive.mo /usr/share/locale/de/LC_MESSAGES/

# install config files
install -v -g gnumed -m 0750 -d /etc/gnumed/
install -v -g gnumed -m 0660 -b gnumed-archive.conf /etc/gnumed/

# log files
touch archive-scan.log archive-index.log archive-view.log
install -v -g gnumed -m 0750 -d /var/log/gnumed/
install -v -g gnumed -m 0660 -b \
	archive-scan.log \
	archive-index.log \
	archive-view.log \
	/var/log/gnumed/

# repository for clients
echo "you must set up and configure data repositories for this client"

# add root to group gnumed
echo "you must add some users to group gnumed"

# config system
echo "you should configure your system in /etc/gnumed/gnumed-archive.conf"


#=============================================================
# $Log: install.sh,v $
# Revision 1.1  2003-04-13 15:19:52  ncq
# - cleanup
#
# Revision 1.1  2002/11/29 15:17:02  ncq
# - installation of GnuMed Archive Server
#
