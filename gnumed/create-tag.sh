#!/bin/sh

#------------------------------------------------------------------
# $Id: create-tag.sh,v 1.1 2008-01-03 15:53:39 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/create-tag.sh,v $
# $Revision: 1.1 $
# License: GPL
#------------------------------------------------------------------

TAG=$1

if test "${TAG}" == "" ; then
	echo ""
	echo "usage: $0 <tag>"
	echo ""
	echo "   tag syntax convention:"
	echo ""
	echo "      rel-X-Y-Z:"
	echo "         - root of branch rel-x-y-z-patches for release x.y.z"
	echo "         - apply to TRUNK"
	echo "      rel-X-Y-Z-rcN:"
	echo "         - Release Candidate N for release x.y.z.0"
	echo "         - apply to branch rel-x-y-z-patches"
	echo "      rel-X-Y-Z-N:"
	echo "         - release x.y.z.n"
	echo "         - apply to branch rel-x-y-z-patches"
	echo ""
	exit
fi

# FIXME: verify tag structure

echo "Are you absolutely positively sure you want"
echo "to tag the CVS tree as \"${TAG}\" ?"
echo "Note that you must have checked in all changes."
echo ""
read -e -p "Tag CVS tree ? [yes/no]: "

if test "${REPLY}" != "yes" ; then
	echo ""
	echo "Tagging aborted."
	echo ""
	exit 0
fi

read -p "Hit [ENTER] to start tagging ..."
echo ""
echo "Tagging CVS tree as \"${TAG}\" ..."
cvs -v tag -c ${TAG}

#------------------------------------------------------------------
# $Log: create-tag.sh,v $
# Revision 1.1  2008-01-03 15:53:39  ncq
# - make tagging easier
#
#