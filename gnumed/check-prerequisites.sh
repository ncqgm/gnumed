#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/check-prerequisites.sh,v $
# $Revision: 1.2 $

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

#=================================================================
# $Log: check-prerequisites.sh,v $
# Revision 1.2  2004-08-13 06:28:35  ncq
# - spit out note on required PostgreSQL access
#
# Revision 1.1  2004/02/19 16:51:08  ncq
# - first version
#
