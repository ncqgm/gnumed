#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/check-prerequisites.sh,v $
# $Revision: 1.1 $

echo "=> checking for Python being installed ..."
PYBIN=`which python`
if [ "x${PYBIN}x" == "xx" ]; then
	echo "ERROR: You don't have Python installed."
	echo "ERROR: Python is available with your OS or from www.python.org"
else
	echo "=> found"
fi

${PYBIN} check-prerequisites.py

#=================================================================
# $Log: check-prerequisites.sh,v $
# Revision 1.1  2004-02-19 16:51:08  ncq
# - first version
#
