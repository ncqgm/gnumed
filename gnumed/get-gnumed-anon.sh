#!/bin/sh

#------------------------------------------------------------------
# $Id: get-gnumed-anon.sh,v 1.1 2005-03-11 11:10:14 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/get-gnumed-anon.sh,v $
# $Revision: 1.1 $
#------------------------------------------------------------------

if [ -d gnumed ] || [ -e update_tree.sh ]; then
	echo " --------------------------------------------------------------"
	echo " There already seems to be a GnuMed CVS tree in this directory."
	echo " You likely want to use <update_tree.sh>."
	echo " --------------------------------------------------------------"
	exit
fi

echo "Anonymously checking out a fresh copy of the GnuMed CVS tree."
CVS_RSH="ssh"
cvs -z9 -d:ext:anoncvs@subversions.gnu.org:/cvsroot/gnumed co -P gnumed

#------------------------------------------------------------------
# $Log: get-gnumed-anon.sh,v $
# Revision 1.1  2005-03-11 11:10:14  ncq
# - initial checkin
#
#
