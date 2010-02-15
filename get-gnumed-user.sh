#!/bin/bash

#------------------------------------------------------------------
# $Id: get-gnumed-user.sh,v 1.4 2008-08-01 09:35:25 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/get-gnumed-user.sh,v $
# $Revision: 1.4 $
#------------------------------------------------------------------

if [ -d gnumed ] || [ -e update_tree.sh ]; then
	echo " --------------------------------------------------------------"
	echo " There already seems to be a GnuMed CVS tree in this directory."
	echo " You likely want to use <update_tree.sh>."
	echo " --------------------------------------------------------------"
	exit
fi

export GMCVSUSER="not set"

echo "Checking out a fresh copy of the GnuMed CVS tree for user <$GMCVSUSER>."
export CVS_RSH="ssh"
export CVSROOT=$GMCVSUSER@cvs.sv.gnu.org:/sources/gnumed/
cvs -z9 co gnumed

# once you have checked out you don't need CVSROOT anymore
# because it's recorded in the CVS/ subdirectories

#------------------------------------------------------------------
# $Log: get-gnumed-user.sh,v $
# Revision 1.4  2008-08-01 09:35:25  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.3  2005/12/11 18:20:38  ncq
# - sources were moved to cvs.savannah.gnu.org
#
# Revision 1.2  2005/07/11 08:32:57  ncq
# - need to *export* environment variable to make them
#   work properly in subprocesses
#
# Revision 1.1  2005/03/11 11:37:07  ncq
# - initial checkin
#
#