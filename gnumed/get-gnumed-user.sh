#!/bin/sh

#------------------------------------------------------------------
# $Id: get-gnumed-user.sh,v 1.1 2005-03-11 11:37:07 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/get-gnumed-user.sh,v $
# $Revision: 1.1 $
#------------------------------------------------------------------

if [ -d gnumed ] || [ -e update_tree.sh ]; then
	echo " --------------------------------------------------------------"
	echo " There already seems to be a GnuMed CVS tree in this directory."
	echo " You likely want to use <update_tree.sh>."
	echo " --------------------------------------------------------------"
	exit
fi

GMCVSUSER="not set"

echo "Checking out a fresh copy of the GnuMed CVS tree for user <$GMCVSUSER>."
CVS_RSH="ssh"
CVSROOT=$GMCVSUSER@subversions.gnu.org:/cvsroot/gnumed/
cvs -z9 co gnumed

# once you have checked out you don't need CVSROOT anymore
# because it's recorded in the CVS/ subdirectories

#------------------------------------------------------------------
# $Log: get-gnumed-user.sh,v $
# Revision 1.1  2005-03-11 11:37:07  ncq
# - initial checkin
#
#