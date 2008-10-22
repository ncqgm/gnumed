#!/bin/bash

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/Attic/net_upgrade-gnumed_server.sh,v $
# $Id: net_upgrade-gnumed_server.sh,v 1.5 2008-10-22 12:25:21 ncq Exp $
# ============================================

PREV_VER="8"
NEXT_VER="9"

OTHER_UPGRADE_OPTS="$1"

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
echo "The GNUmed database is about to be upgraded."
echo "You may need to enter your password now:"
sudo ./upgrade-db.sh ${PREV_VER} ${NEXT_VER} ${OTHER_UPGRADE_OPTS}

# ============================================
# $Log: net_upgrade-gnumed_server.sh,v $
# Revision 1.5  2008-10-22 12:25:21  ncq
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
