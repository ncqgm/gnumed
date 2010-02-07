#!/bin/sh

#------------------------------------------------------------------
# $Id: get-branch-user.sh,v 1.1 2010-02-07 15:31:12 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/get-branch-user.sh,v $
# $Revision: 1.1 $
#------------------------------------------------------------------

BRANCH="rel-0-6-patches"

if [ -d gnumed ] || [ -e update_tree.sh ]; then
	echo " --------------------------------------------------------------"
	echo " There already seems to be a GNUmed CVS tree in this directory."
	echo " You likely want to use <update_tree.sh>."
	echo " --------------------------------------------------------------"
	exit
fi

export GMCVSUSER="not set"

echo "Checking out a fresh copy of the GNUmed CVS branch \"${BRANCH}\" for user <$GMCVSUSER>."
export CVS_RSH="ssh"
export CVSROOT=$GMCVSUSER@cvs.sv.gnu.org:/sources/gnumed/
cvs -z9 co -r ${BRANCH} gnumed

# once you have checked out you don't need CVSROOT anymore
# because it's recorded in the CVS/ subdirectories

#------------------------------------------------------------------
# $Log: get-branch-user.sh,v $
# Revision 1.1  2010-02-07 15:31:12  ncq
# - new
#
#