#!/bin/bash

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-net_upgrade_server.sh,v $
# $Id: gm-net_upgrade_server.sh,v 1.2 2009-11-19 15:07:53 ncq Exp $
# ============================================

PREV_VER="11"
NEXT_VER="12"

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
cd ${BASEDIR}/server/bootstrap/
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
# $Log: gm-net_upgrade_server.sh,v $
# Revision 1.2  2009-11-19 15:07:53  ncq
# - bump db version
#
# Revision 1.1  2009/09/08 17:25:40  ncq
# - relocated
# - renamed to be more consistent
# - adjusted to tarball name
#
# Revision 1.9  2009/09/01 22:40:56  ncq
# - add self-upgrade
# - cleanup
#
# Revision 1.8  2009/04/07 11:32:02  ncq
# - deal with non-one-digit versions
#
# Revision 1.7  2009/03/18 14:32:57  ncq
# - bump version
#
# Revision 1.6  2009/01/06 18:23:24  ncq
# - sudo -> su
#
# Revision 1.5  2008/10/22 12:25:21  ncq
# - lsb_release
#
# Revision 1.4  2008/08/01 10:38:25  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.3  2008/01/05 20:42:32  ncq
# - bump version
#
# Revision 1.2  2007/12/06 13:08:13  ncq
# - support more upgrade-db.sh options
#
# Revision 1.1  2007/11/02 12:44:09  ncq
# - first version to ease migration
#
#
