#!/bin/bash

# ============================================
#
# This should be run as a normal user, not as root.
#
# ============================================


# try to determine distribution of target system
# FIXME: use lsb_release
# SUSE
if [ -f /etc/SuSE-release ]; then
	DEPS="gnumed-common postgresql postgresql-plpython cron tar coreutils mailx openssl bzip2 gpg2 mc rsync python3-psycopg2 gzip"
	PKG_INSTALLER="zypper install"
	SYS_TYPE="SuSE"
fi
# Debian
if [ -f /etc/debian_version ]; then
	DEPS="gnumed-common postgresql postgresql-client cron anacron tar hostname coreutils mailx openssl bzip2 gzip gnupg mc rsync python3-psycopg2 sudo wget"
	PKG_INSTALLER="apt-get install"
	SYS_TYPE="Debian"
fi
# Mandriva
if [ -f /etc/mandriva-release ]; then
	DEPS="gnumed-common postgresql postgresql-client cron anacron tar hostname coreutils mailx openssl bzip2 gnupg mc rsync python3-psycopg2 gzip"
	PKG_INSTALLER="urpmi"
	SYS_TYPE="Mandriva"
fi


echo ""
echo "================================================"
echo "This GNUmed helper will download and install the"
echo "latest GNUmed server onto your ${SYS_TYPE} machine."
echo ""
echo "It will also take care of installing the"
echo "dependencies needed to operate GNUmed smoothly."
echo "================================================"


# prepare environment
mkdir -p ~/.gnumed/server-installation/
cd ~/.gnumed/server-installation/
rm -r GNUmed-v*									# old cleanup
rm -f GNUmed-server.latest.tgz					# old cleanup
rm -r gnumed-server.*
rm -f gnumed-server.latest.tgz


# install dependencies
echo ""
echo "Installing dependencies ..."
echo ""
echo "Do you want to install the following dependencies"
echo "needed to smoothly operate the GNUmed server ?"
echo ""
echo "${DEPS}"
echo ""
read -e -p "Install dependencies ? [y/N]: "
if test "${REPLY}" == "y" ; then
	echo ""
	echo "You may need to enter the root password now (unless you ARE root):"
	su -c "${PKG_INSTALLER} ${DEPS}"
fi


# get and unpack package
echo ""
echo "Downloading package ..."
echo ""
wget -c https://www.gnumed.de/downloads/server/gnumed-server.latest.tgz
tar -xzf gnumed-server.latest.tgz
BASEDIR=`ls -1 -d gnumed-server.*`
mv -f gnumed-server.latest.tgz ${BASEDIR}-server.tgz


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
su -c "./bootstrap-latest.sh"

# ============================================
