#!/bin/bash

# ===========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/Attic/net_install-gnumed_client.sh,v $
# $Id: net_install-gnumed_client.sh,v 1.4.2.8 2008-11-26 12:22:26 ncq Exp $
# ===========================================================

VER_LATEST="0.3.8"
INSTALL_BASE=~/".gnumed/client-installation"

# ===========================================================
VER_CLI="$1"
DL_BASE_URL="http://www.gnumed.de/downloads/client/0.3"		# FIXME: derive "0.2" from version
SYS_TYPE="generic Un*x"
PKG_INSTALLER=`which true`
DEPS=""

# determine version to install
if test -z ${VER_CLI} ; then
	TARGET_VER=${VER_LATEST}
else
	TARGET_VER=${VER_CLI}
fi ;

TGZ_NAME="GNUmed-client.${TARGET_VER}.tgz"
LAUNCHER=~/"Desktop/GNUmed ${TARGET_VER}"

# try to determine distribution of target system
# SuSE
if [ -f /etc/SuSE-release ]; then
	DEPS="postgresql tar coreutils mc python-psycopg2 openssl wget gzip file"
	PKG_INSTALLER="zypper install"
	SYS_TYPE="SuSE"
fi
# Debian
if [ -f /etc/debian_version ]; then
	DEPS="postgresql-client tar coreutils mc python-psycopg2 openssl wget gzip file python-gnuplot konsolekalendar aspell python python-enchant python-support python-wxgtk2.8 bash xsane apt"
	PKG_INSTALLER="apt-get install"
	SYS_TYPE="Debian"
fi
# Mandriva
if [ -f /etc/mandriva-release ]; then
	DEPS="postgresql-client tar coreutils mc python-psycopg2 openssl wget gzip file"
	PKG_INSTALLER="urpmi"
	SYS_TYPE="Mandriva"
fi
# PCLinuxOS
if [ -f /etc/version ] ; then
	grep -q PCLinuxOS /etc/version
	if [ $? -eq 0 ] ; then
		DEPS="postgresql-client tar coreutils mc python-psycopg2 openssl wget gzip file"
		PKG_INSTALLER="rpm -i"
		SYS_TYPE="PCLinuxOS"
	fi
fi

echo ""
echo "======================================================="
echo "This GNUmed helper will download and install the GNUmed"
echo "client v${TARGET_VER} onto your ${SYS_TYPE} machine. The system"
echo "account \"${USER}\" will be the only one able to use it."
echo ""
echo "It can also try to take care of installing any"
echo "dependancies needed to operate GNUmed smoothly."
echo ""
echo "A link will be put on the desktop so you can"
echo "easily start this version of the GNUmed client."
echo ""
echo "Installation directory:"
echo ""
echo "  ${INSTALL_BASE}/GNUmed-${TARGET_VER}/"
echo "======================================================="


# install dependancies
echo ""
echo "Installing dependancies ..."
echo ""
echo "Do you want to install the following dependancies"
echo "needed to smoothly operate the GNUmed client ?"
echo ""
echo "${DEPS}"
echo ""
read -e -p "Install dependancies ? [y/N]: "
if test "${REPLY}" == "y" ; then
	echo ""
	echo "You may need to enter the password for \"${USER}\" now:"
	sudo ${PKG_INSTALLER} ${DEPS}
fi


# prepare environment
mkdir -p ${INSTALL_BASE}
cd ${INSTALL_BASE}


# get and unpack package
echo ""
echo "Downloading ..."
wget -c "${DL_BASE_URL}/${TGZ_NAME}"
if test $? -ne 0 ; then
	echo "ERROR: cannot download v${TARGET_VER}, aborting"
	exit 1
fi
if test -d GNUmed-${TARGET_VER}/ ; then
	echo "It seems the client version v${TARGET_VER} is"
	echo "already installed. What do you want to do ?"
	echo ""
	echo " o - overwrite with new installation"
	echo " c - configure existing installation"
	echo " q - quit"
	echo ""
	read -e -p "Do what ? [o/c/q]: "
else
	REPLY="o"
fi
if test "${REPLY}" == "q" ; then
	exit 0
fi
if test "${REPLY}" == "c" ; then
	CONFIGURE="true"
elif test "${REPLY}" == "o" ; then
	rm -rf GNUmed-${TARGET_VER}/
	tar -xzf ${TGZ_NAME}
	if test $? -ne 0 ; then
		echo "ERROR: cannot unpack ${TGZ_NAME}, aborting"
		exit 1
	fi
	CONFIGURE="false"
else
	echo "ERROR: invalid choice: ${REPLY}"
	exit 1
fi


# check for dependancies
echo ""
echo "Checking dependancies ..."
cd GNUmed-${TARGET_VER}/client/
./check-prerequisites.sh


# activate local translation
cd locale/
# DE
mkdir -p ./de_DE/LC_MESSAGES/
cd de_DE/LC_MESSAGES/
ln -sf ../../de-gnumed.mo gnumed.mo
cd ../../
# ES
mkdir -p ./es_ES/LC_MESSAGES/
cd es_ES/LC_MESSAGES/
ln -sf ../../es-gnumed.mo gnumed.mo
cd ../../
# FR
mkdir -p ./fr_FR/LC_MESSAGES/
cd fr_FR/LC_MESSAGES/
ln -sf ../../fr-gnumed.mo gnumed.mo
cd ../../
# IT
mkdir -p ./it_IT/LC_MESSAGES/
cd it_IT/LC_MESSAGES/
ln -sf ../../it-gnumed.mo gnumed.mo
cd ../../../


# add desktop link
if test -e "${LAUNCHER}" ; then
	if test "${CONFIGURE}" == "true" ; then
		echo ""
		read -p "Editing launcher script (hit [ENTER]) ..."
		mc -e "${LAUNCHER}"
	else
		echo "#!/bin/bash" > "${LAUNCHER}"
		echo "" >> "${LAUNCHER}"
		echo "cd ${INSTALL_BASE}/GNUmed-${TARGET_VER}/client/" >> "${LAUNCHER}"
		echo "./gm-from-cvs.sh" >> "${LAUNCHER}"
	fi
else
	echo "#!/bin/bash" > "${LAUNCHER}"
	echo "" >> "${LAUNCHER}"
	echo "cd ${INSTALL_BASE}/GNUmed-${TARGET_VER}/client/" >> "${LAUNCHER}"
	echo "./gm-from-cvs.sh" >> "${LAUNCHER}"
fi
chmod u+x "${LAUNCHER}"


# edit config file
echo ""
read -p "Editing configuration file (hit [ENTER]) ..."
mc -e gm-from-cvs.conf

# ============================================
# $Log: net_install-gnumed_client.sh,v $
# Revision 1.4.2.8  2008-11-26 12:22:26  ncq
# - bump version
#
# Revision 1.4.2.7  2008/11/23 17:23:13  ncq
# - bump version
#
# Revision 1.4.2.6  2008/11/10 22:45:15  ncq
# - bump version
#
# Revision 1.4.2.5  2008/10/28 14:16:30  ncq
# - bump version
#
# Revision 1.4.2.4  2008/10/24 14:12:50  ncq
# - bump version
#
# Revision 1.4.2.3  2008/10/15 15:39:55  ncq
# - bump version
#
# Revision 1.4.2.2  2008/09/09 18:39:54  ncq
# - bump version
#
# Revision 1.4.2.1  2008/08/31 14:26:59  ncq
# - bumb version and dl url
#
# Revision 1.4  2008/08/05 12:45:28  ncq
# - adjust Debian dependancies
#
# Revision 1.3  2008/08/01 10:33:16  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.2  2008/02/25 17:47:12  ncq
# - detect PCLinuxOS for setting installer/dependancies
#
# Revision 1.1  2008/02/21 16:22:06  ncq
# - newly added
#
#
