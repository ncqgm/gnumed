#!/bin/bash

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/Attic/net_install-gnumed_server.sh,v $
# $Id: net_install-gnumed_server.sh,v 1.7 2008-10-22 12:25:23 ncq Exp $
# ============================================

# try to determine distribution of target system
# FIXME: use lsb_release
# SUSE
if [ -f /etc/SuSE-release ]; then
	DEPS="gnumed-common postgresql postgresql-plpython cron tar coreutils mailx openssl bzip2 gpg2 mc rsync python-psycopg2 gzip"
	PKG_INSTALLER="zypper install"
	SYS_TYPE="SuSE"
fi
# Debian
if [ -f /etc/debian_version ]; then
	DEPS="gnumed-common postgresql postgresql-client cron anacron tar hostname coreutils mailx openssl bzip2 gzip gnupg mc rsync python-psycopg2 sudo wget"
	PKG_INSTALLER="apt-get install"
	SYS_TYPE="Debian"
fi
# Mandriva
if [ -f /etc/mandriva-release ]; then
	DEPS="gnumed-common postgresql postgresql-client cron anacron tar hostname coreutils mailx openssl bzip2 gnupg mc rsync python-psycopg2 gzip"
	PKG_INSTALLER="urpmi"
	SYS_TYPE="Mandriva"
fi

echo ""
echo "================================================"
echo "This GNUmed helper will download and install the"
echo "latest GNUmed server onto your ${SYS_TYPE} machine."
echo ""
echo "It will also take care to also install the"
echo "dependancies needed to operate GNUmed smoothly."
echo "================================================"

# prepare environment
mkdir -p ~/.gnumed/server-installation/
cd ~/.gnumed/server-installation/
rm -r GNUmed-v?
rm -f GNUmed-server.latest.tgz

# install dependancies
echo ""
echo "Installing dependancies ..."
echo ""
echo "Do you want to install the following dependancies"
echo "needed to smoothly operate the GNUmed server ?"
echo ""
echo "${DEPS}"
echo ""
read -e -p "Install dependancies ? [y/N]: "
if test "${REPLY}" == "y" ; then
	echo ""
	echo "You may need to enter the password for \"${USER}\" now:"
	sudo ${PKG_INSTALLER} ${DEPS}
fi

# get and unpack package
echo ""
echo "Downloading package ..."
echo ""
wget -c http://www.gnumed.de/downloads/server/GNUmed-server.latest.tgz
tar -xzf GNUmed-server.latest.tgz
BASEDIR=`ls -1 -d GNUmed-v?`
mv -f GNUmed-server.latest.tgz ${BASEDIR}-server.tgz

# run bootstrapper
cd ${BASEDIR}/server/bootstrap/
echo ""
echo "Installing database ..."
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
# $Log: net_install-gnumed_server.sh,v $
# Revision 1.7  2008-10-22 12:25:23  ncq
# - lsb_release
#
# Revision 1.6  2008/08/01 10:38:25  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.5  2008/02/29 23:50:41  ncq
# - optionalize installing DEPs
# - improve output
#
# Revision 1.4  2008/02/25 19:41:07  ncq
# - add gzip as dependancy
#
# Revision 1.3  2008/01/05 19:33:59  ncq
# - re-reorder
#
# Revision 1.2  2008/01/05 19:33:15  ncq
# - add sudo and wegt
# - reorder a bit
#
# Revision 1.1  2007/10/28 10:19:07  ncq
# - renamed to better reflect the use beyond Debian
#
# Revision 1.7  2007/10/28 09:16:49  ncq
# - slightly improved
#
# Revision 1.6  2007/10/28 01:02:24  shilbert
# - introduce install_helper to make it usable for openSUSE and Mandriva
#
# Revision 1.5  2007/10/07 12:35:02  ncq
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