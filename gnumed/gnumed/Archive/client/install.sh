#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/client/Attic/install.sh,v $
# $Revision: 1.2 $

echo "this must be run as root because we will put some stuff in /usr/bin/ and other places"

# group gnumed
groupadd gnumed

# install binaries
echo "installing binaries"
install -v -g gnumed -m 0750 -b \
	gmShowMedDocs.py run-viewer.sh \
	/usr/bin/

#	gmScanMedDocs.py run-scanner.sh \
#	index-med_docs.py run-indexer.sh \

# install modules
echo "installing GnuMed python modules"
install -v -g gnumed -m 0750 -d /usr/share/gnumed/
install -v -g gnumed -m 0750 -d /usr/share/gnumed/python-common/
install -v -g gnumed -m 0660 -b modules/* /usr/share/gnumed/python-common/

# install message catalog
echo "installing language translation files"
echo "German..."
install -v -g root -m 0644 locale/de_DE@euro/LC_MESSAGES/gnumed-archive.mo /usr/share/locale/de/LC_MESSAGES/

# install docs
install -v -g gnumed -m 0750 -d /usr/share/doc/gnumed/
install -v -g gnumed -m 0640 -b gnumed-archive.conf /usr/share/doc/gnumed/

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

# configure system
echo "configuration information can be found in /usr/share/doc/gnumed/"

#=============================================================
# $Log: install.sh,v $
# Revision 1.2  2003-04-18 16:16:16  ncq
# - some updates
#
