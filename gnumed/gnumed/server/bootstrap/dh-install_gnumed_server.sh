#!/bin/sh

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/Attic/dh-install_gnumed_server.sh,v $
# $Id: dh-install_gnumed_server.sh,v 1.2 2007-09-16 00:45:40 ncq Exp $
# ============================================

echo ""
echo "================================================"
echo "This GNUmed helper will download and install the"
echo "latest GNUmed server onto your Debian machine."
echo "================================================"

# prepare environment
mkdir -p ~/.gnumed/server-installation/
cd ~/.gnumed/server-installation/
rm -r GNUmed-v?
rm -f GNUmed-server.latest.tgz

# get and unpack package
wget -q http://www.gnumed.de/downloads/server/GNUmed-server.latest.tgz
tar -xzf GNUmed-server.latest.tgz
BASEDIR=`ls -1 -d GNUmed-v?`
mv -f GNUmed-server.latest.tgz ${BASEDIR}-server.tgz

# run bootstrapper
cd ${BASEDIR}/server/bootstrap/
echo ""
echo "The GNUmed server version \"${BASEDIR}\" has been"
echo "prepared for installation in the directory"
echo ""
echo " ["`pwd`"]"
echo ""
echo "The GNUmed database is about to be installed."
echo "You may need to enter your password now:"
sudo ./bootstrap-latest.sh

# ============================================
# $Log: dh-install_gnumed_server.sh,v $
# Revision 1.2  2007-09-16 00:45:40  ncq
# - prettified output
#
# Revision 1.1  2007/09/16 00:44:03  ncq
# - first version
#
#