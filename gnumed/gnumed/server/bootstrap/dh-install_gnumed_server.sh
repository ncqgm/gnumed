#!/bin/sh

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/Attic/dh-install_gnumed_server.sh,v $
# $Id: dh-install_gnumed_server.sh,v 1.5 2007-10-07 12:35:02 ncq Exp $
# ============================================

DEPS="gnumed-common postgresql postgresql-client cron anacron tar hostname coreutils mailx openssl bzip2 gnupg mc rsync python-psycopg2"

echo ""
echo "================================================"
echo "This GNUmed helper will download and install the"
echo "latest GNUmed server onto your Debian machine."
echo ""
echo "It will also take care to also install the"
echo "dependancies needed to operate GNUmed smoothly."
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

# install dependancies
echo ""
echo "Package dependancies are about to be installed."
echo "You may need to enter your password now:"
sudo apt-get install ${DEPS}

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
# Revision 1.5  2007-10-07 12:35:02  ncq
# - depend on latest version of postgresql
#
# Revision 1.4  2007/10/02 19:13:42  shilbert
# - fix for wrong dependency, gpg2 --> gnupg, added python-psycopg2
#
# Revision 1.3  2007/09/16 01:01:57  ncq
# - install dependancies
#
# Revision 1.2  2007/09/16 00:45:40  ncq
# - prettified output
#
# Revision 1.1  2007/09/16 00:44:03  ncq
# - first version
#
#