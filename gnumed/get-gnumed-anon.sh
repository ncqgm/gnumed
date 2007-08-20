#!/bin/sh

#------------------------------------------------------------------
# $Id: get-gnumed-anon.sh,v 1.5 2007-08-20 19:21:29 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/get-gnumed-anon.sh,v $
# $Revision: 1.5 $
#------------------------------------------------------------------

if [ -d gnumed ] || [ -e update_tree.sh ]; then
	echo " --------------------------------------------------------------"
	echo " There already seems to be a GnuMed CVS tree in this directory."
	echo " You likely want to use <update_tree.sh>."
	echo " --------------------------------------------------------------"
	exit
fi

echo "Anonymously checking out a fresh copy of the GNUmed CVS tree."
cvs -z9 -d:pserver:anonymous@cvs.sv.gnu.org:/sources/gnumed co -P gnumed

#------------------------------------------------------------------
# $Log: get-gnumed-anon.sh,v $
# Revision 1.5  2007-08-20 19:21:29  ncq
# - fix gnumed spelling
#
# Revision 1.4  2005/12/23 16:07:26  ncq
# - no need for CVS_RSH=ssh anymore
#
# Revision 1.3  2005/12/11 18:24:45  ncq
# - use pserver again for anon, also moved to cvs.sv.gnu.org
#
# Revision 1.2  2005/07/11 08:32:57  ncq
# - need to *export* environment variable to make them
#   work properly in subprocesses
#
# Revision 1.1  2005/03/11 11:10:14  ncq
# - initial checkin
#
#
