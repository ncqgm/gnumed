#!/bin/bash

# ============================================

PREV_VER="21"
NEXT_VER="22"

INSTALL_BASE=~/".gnumed/server-installation"
DL_BASE="http://www.gnumed.de/downloads/server"

OTHER_UPGRADE_OPTS="$1"


# upgrader update
if test "${OTHER_UPGRADE_OPTS}" == "update" ; then
	echo ""
	echo "Updating the upgrader itself."
	echo ""
	echo "The new version will be in $0.new."
	wget http://www.gnumed.de/downloads/server/$0 -O $0.new
	chmod +x $0.new
	exit 0
fi


# try to determine distribution of target system
# FIXME: use lsb_release
# SUSE
if [ -f /etc/SuSE-release ]; then
	SYS_TYPE="SuSE"
fi
# Debian
if [ -f /etc/debian_version ]; then
	SYS_TYPE="Debian"
fi
# Mandriva
if [ -f /etc/mandriva-release ]; then
	SYS_TYPE="Mandriva"
fi


echo ""
echo "================================================"
echo "This GNUmed helper will download the latest (v${NEXT_VER})"
echo "GNUmed server onto your ${SYS_TYPE} machine and"
echo "upgrade your existing \"gnumed_v${PREV_VER}\" database."
echo "================================================"


# prepare environment
mkdir -p ${INSTALL_BASE}/
cd ${INSTALL_BASE}/
rm -r GNUmed-v*							# old cleanup
rm -f GNUmed-server.latest.tgz			# old cleanup
rm -r gnumed-server.*
rm -f gnumed-server.latest.tgz


# get and unpack package
wget -q ${DL_BASE}/gnumed-server.latest.tgz
tar -xzf gnumed-server.latest.tgz
BASEDIR=`ls -1 -d gnumed-server.*`
mv -f gnumed-server.latest.tgz ${BASEDIR}-server.tgz


# run bootstrapper
cd ${INSTALL_BASE}/${BASEDIR}/server/bootstrap/
echo ""
echo "The GNUmed server version \"${BASEDIR}\" has been"
echo "prepared for installation in the directory"
echo ""
echo " ["`pwd`"]"
echo ""
echo "The GNUmed database is about to be upgraded."
echo "You may need to enter your password now:"
su -c "./upgrade-db.sh ${PREV_VER} ${NEXT_VER} ${OTHER_UPGRADE_OPTS}"

# ============================================
