#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/check-prerequisites.sh,v $
# $Revision: 1.4 $

echo "-----------------------------------------------------------"
echo "Please make sure to also read the INSTALL and README files."
echo ""
echo "Run this script from the directory it is in or it might fail."
echo ""

echo "=> checking for Python being installed ..."
PYBIN=`which python`
if [ "x${PYBIN}x" == "xx" ]; then
	echo "ERROR: You don't have Python installed."
	echo "ERROR: Python is available with your OS or from www.python.org"
else
	echo "=> found"
fi

${PYBIN} check-prerequisites.py

echo "NOTE: You also need to have access to a working PostgreSQL"
echo "NOTE: installation. It is, however, non-trivial to reliably"
echo "NOTE: test for that."
echo "NOTE: In the following list you should see at least one"
echo "NOTE: process saying 'postmaster' but NOT saying 'grep'"
echo ""
ps ax | grep postmaster

#=================================================================
# $Log: check-prerequisites.sh,v $
# Revision 1.4  2005-01-16 20:02:53  ncq
# - some crude visual check for a running PostgreSQL postmaster process
#
# Revision 1.3  2005/01/16 19:56:29  ncq
# - improved wording
#
# Revision 1.2  2004/08/13 06:28:35  ncq
# - spit out note on required PostgreSQL access
#
# Revision 1.1  2004/02/19 16:51:08  ncq
# - first version
#
