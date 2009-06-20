#!/bin/bash

# ===========================================================
# This script must be run as the user who wants to use the
# GNUmed client. If you opt for letting the script try to
# install dependancies it will attempt to use SU for which
# you will need to know the root password.
#
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/Attic/gm-install_client_locally.sh,v $
# $Id: gm-install_client_locally.sh,v 1.8 2009-06-20 12:48:57 ncq Exp $
# ===========================================================

INSTALL_BASE=~/".gnumed/client-installation"
DL_BASE="http://www.gnumed.de/downloads/client"

# ===========================================================
if test "$LOGNAME" == "root" ; then
	echo ""
	echo "This script is not intended to be run as root."
	echo ""
	echo "Please run it as the user you want"
	echo "to use the GNUmed client as."
	echo ""
	exit
fi


ARG_ONE="$1"
if test -z ${ARG_ONE} ; then
	echo "======================================================="
	echo "usage:"
	echo ""
	echo " $0 <version> | <tarball> | update | deps"
	echo ""
	echo " <version>: the client version to install from the net"
	echo " <tarball>: a downloaded client tarball"
	echo " update:    update the installer itself from the net"
	echo " deps:      install client dependencies (system-wide)"
	echo ""
	echo " Download area: ${DL_BASE}/"
	echo ""
	echo " Note: This does NOT run as root !"
	echo "======================================================="
	exit 1
fi


# installer update
if test "${ARG_ONE}" == "update" ; then
	echo ""
	echo "Updating the installer itself."
	echo ""
	echo "The new version will be in $0.new."
	wget http://www.gnumed.de/downloads/client/$0 -O $0.new
	chmod +x $0.new
	exit 0
fi


# try to determine distribution of target system
DEPS=""
PKG_INSTALLER=`which true`
SYS_TYPE="generic Un*x"

# FIXME: use "lsb_release"
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


# installation of dependencies
if test "${ARG_ONE}" == "deps" ; then
	echo ""
	echo "Installing dependencies on ${SYS_TYPE} ..."
	echo ""
	echo "Do you want to install the following dependencies"
	echo "needed to smoothly operate the GNUmed client ?"
	echo ""
	echo "${DEPS}"
	echo ""
	echo "Note that dependencies will be installed system-wide."
	echo ""
	read -e -p "Install dependencies ? [y/N]: "
	if test "${REPLY}" == "y" ; then
		echo ""
		echo "You may need to enter the password for \"${USER}\" now:"
		su -c "${PKG_INSTALLER} ${DEPS}"
	fi

	exit 0
fi



if test -r ${ARG_ONE} ; then
	TGZ_NAME=${ARG_ONE}
	TARGET_VER=`basename ${TGZ_NAME} .tgz | cut --complement -c 1-14`
else
	TARGET_VER=${ARG_ONE}
	TGZ_NAME="GNUmed-client.${TARGET_VER}.tgz"
	TARGET_BRANCH=`echo ${TARGET_VER} | cut -c 1-3`
	DL_BASE_URL="${DL_BASE}/${TARGET_BRANCH}"
fi
LAUNCHER=~/"Desktop/GNUmed ${TARGET_VER}"



echo ""
echo "=========================================================="
echo "This GNUmed helper will install the GNUmed client v${TARGET_VER}"
echo "onto your ${SYS_TYPE} machine. The system account"
echo "\"${USER}\" will be the only one able to use it."
echo ""
echo "A link will be put on the desktop so you can"
echo "easily start this version of the GNUmed client."
echo ""
echo "Installation directory:"
echo ""
echo "  ${INSTALL_BASE}/GNUmed-${TARGET_VER}/"
echo "=========================================================="


# download tarball ?
if test ! -r ${TGZ_NAME} ; then
	echo ""
	echo "Downloading ..."
	wget -c "${DL_BASE_URL}/${TGZ_NAME}"
	if test $? -ne 0 ; then
		echo "ERROR: cannot download v${TARGET_VER}, aborting"
		exit 1
	fi
	if test ! -r ${TGZ_NAME} ; then
		echo "ERROR: ${TGZ_NAME} not there after download, aborting"
		exit 1
	fi
fi


# prepare environment
mkdir -p ${INSTALL_BASE}
mv -f ${TGZ_NAME} ${INSTALL_BASE}/
cd ${INSTALL_BASE}


# check previous installation and unpack package
echo ""
if test -d GNUmed-${TARGET_VER}/ ; then
	echo ""
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


# check dependancies
echo ""
echo "Checking dependencies ..."
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
cd ../../
# pt_BR
mkdir -p ./pt_BR/LC_MESSAGES/
cd pt_BR/LC_MESSAGES/
ln -sf ../../pt_BR-gnumed.mo gnumed.mo
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
echo "Editing configuration file ..."
echo ""
echo "You may want to adjust profiles and workplace name."
read -p "hit [ENTER] to continue"
mc -e gm-from-cvs.conf


# edit startup script
echo "Editing startup shell script ..."
echo ""
echo "You may want to remove the --debug and --override-schema-check options."
read -p "hit [ENTER] to continue"
mc -e gm-from-cvs.sh


# ============================================
# $Log: gm-install_client_locally.sh,v $
# Revision 1.8  2009-06-20 12:48:57  ncq
# - support installing deps by "deps" argument
#
# Revision 1.7  2009/05/08 08:03:03  ncq
# - add self-update
#
# Revision 1.6  2009/05/05 08:42:57  ncq
# - fix missing cut
#
# Revision 1.5  2009/05/05 08:37:25  ncq
# - add option update
#
# Revision 1.4  2009/04/21 17:02:27  ncq
# - calculate DL URL from version on command line
#
# Revision 1.3  2009/04/13 11:01:40  ncq
# - hint on what to edit in conf file
# - offer to edit startup file with hint
#
# Revision 1.2  2009/02/25 09:38:18  ncq
# - better wording
#
# Revision 1.1  2009/02/24 17:57:32  ncq
# - added install script, works both from local tarball or from the net
#
# Revision 1.9  2009/02/17 11:58:53  ncq
# - bump download client version dir
#
# Revision 1.8  2009/01/06 18:26:30  ncq
# - sudo -> su
#
# Revision 1.7  2008/10/22 12:24:48  ncq
# - lsb_release
#
# Revision 1.6  2008/10/12 16:38:46  ncq
# - do not run as root
#
# Revision 1.5  2008/08/28 18:35:46  ncq
# - bump download URL
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
