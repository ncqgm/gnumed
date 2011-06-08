#!/bin/bash

#------------------------------------------------------------------
# $Id: get-gnumed-user.sh,v 1.4 2008-08-01 09:35:25 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/get-gnumed-user.sh,v $
# $Revision: 1.4 $
#------------------------------------------------------------------

if [ -d gnumed ] || [ -e update_tree.sh ]; then
	echo " --------------------------------------------------------------"
	echo " There already seems to be a GNUmed CVS tree in this directory."
	echo " You likely want to use <update_tree.sh>."
	echo " --------------------------------------------------------------"
	exit
fi

export GMCVSUSER="not set"

echo "Checking out a fresh copy of the GNUmed CVS tree for user <$GMCVSUSER>."
export CVS_RSH="ssh"
export CVSROOT=$GMCVSUSER@cvs.sv.gnu.org:/sources/gnumed/
cvs -z9 co gnumed

# once you have checked out you don't need CVSROOT anymore
# because it's recorded in the CVS/ subdirectories

#------------------------------------------------------------------
