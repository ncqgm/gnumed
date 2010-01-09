#!/bin/bash

#------------------------------------------------------------------
# $Id: create-tag.sh,v 1.5 2010-01-09 19:54:13 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/create-tag.sh,v $
# $Revision: 1.5 $
# License: GPL
#------------------------------------------------------------------

TAG=$1
REGEX="rel-[0-9]-[0-9](-(rc){0,1}[0-9]){0,1}$"

if ! [[ "${TAG}" =~ ${REGEX} ]] ; then
	echo ""
	echo "usage: $0 <tag>"
	echo ""
	echo "   should match: ${REGEX}"
	echo "   you entered : ${TAG}"
	echo ""
	echo "   tag syntax convention:"
	echo ""
	echo "      rel-X-Y:"
	echo "         - root of branch rel-x-y-z-patches for release x.y.z"
	echo "         - apply to TRUNK"
	echo "      rel-X-Y-rcN:"
	echo "         - Release Candidate N for release x.y.z.0"
	echo "         - apply to branch rel-x-y-z-patches"
	echo "      rel-X-Y-Z-N:"
	echo "         - release x.y.z.n"
	echo "         - apply to branch rel-x-y-z-patches"
	echo ""
	exit
fi

echo ""
echo "Are you absolutely positively sure you"
echo "want to tag the CVS tree as"
echo ""
echo "   \"${TAG}\" ?"
echo ""
echo "(you must have checked in all changes)"
echo ""
read -e -p "Tag CVS tree ? [yes/no]: "

if test "${REPLY}" != "yes" ; then
	echo ""
	echo "Tagging aborted."
	echo ""
	exit 0
fi

echo ""
read -p "Hit [ENTER] to *actually* start tagging ..."
echo ""
echo "Tagging CVS tree as \"${TAG}\" ..."
cvs tag -c ${TAG}

#------------------------------------------------------------------
# $Log: create-tag.sh,v $
# Revision 1.5  2010-01-09 19:54:13  ncq
# - fix it, eventually :-)
#
# Revision 1.4  2009/08/24 20:11:27  ncq
# - bump db version
# - fix tag creation
# - provider inbox:
# 	enable filter-to-active-patient,
# 	listen to new signal,
# 	use cInboxMessage class
# - properly constrain LOINC phrasewheel SQL
# - include v12 scripts in release
# - install arriba jar to /usr/local/bin/
# - check for table existence in audit schema generator
# - include dem.message inbox with additional generic signals
#
# Revision 1.3  2008/01/30 13:28:20  ncq
# - properly use cvs
#
# Revision 1.2  2008/01/03 16:28:17  ncq
# - stricter TAG checking
#
# Revision 1.1  2008/01/03 15:53:39  ncq
# - make tagging easier
#
#