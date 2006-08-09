#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/check-prerequisites.sh,v $
# $Revision: 1.7 $

echo "-------------------------------------------------------------"
echo "Please make sure to also read the INSTALL and README files."
echo ""
echo "Run this script from the directory it is in or it might fail."
echo "-------------------------------------------------------------"
echo ""
echo "You need to be able to connect to a PostgreSQL"
echo "server. It is, however, non-trivial to reliably"
echo "test for that."
echo "If you want to work with a *local* database (on this"
echo "machine) you should see at least one process saying"
echo "'postmaster' in the following list."
echo "If you don't you can still use our public database"
echo "at salaam.homeunix.com for testing."
echo ""
echo "-------------------------------------------------------------------------"
ps axww | grep postmaster | grep -v "grep"
echo "-------------------------------------------------------------------------"
echo ""

echo "=> checking for Python interpreter ..."
PYBIN=`which python`
if [ "x${PYBIN}x" == "xx" ]; then
	echo "ERROR: You don't have Python installed."
	echo "ERROR: Python is available with your OS or from www.python.org"
else
	echo "=> found"
fi

# make sure we can locally find the Python modules
cd gnumed
ln -s client Gnumed
cd -

echo ""
read -p "Press <RETURN> key to continue."
echo    "-------------------------------"

${PYBIN} check-prerequisites.py

echo ""
read -p "Press <RETURN> key to continue."
echo    "-------------------------------"

echo "=> checking for 'file' command ..."
BIN=`which file`
if [ "x${BIN}x" == "xx" ]; then
	echo "INFO : You don't seem to have the 'file' command installed."
	echo "INFO : It is available with your OS. On Windows it is not needed."
else
	echo "=> found"
fi

echo "=> checking for 'extract' command ..."
BIN=`which extract`
if [ "x${BIN}x" == "xx" ]; then
	echo "INFO : You don't seem to have the 'extract' command installed."
	echo "INFO : It is available with your OS. On Windows it is not needed."
else
	echo "=> found"
fi


#=================================================================
# $Log: check-prerequisites.sh,v $
# Revision 1.7  2006-08-09 14:06:27  ncq
# - make more sure output doesn't scroll off the screen
# - add checks for file/extract commands
#
# Revision 1.6  2006/08/01 18:47:43  ncq
# - improved wording/readability
# - add test for GNUmed's own Python modules
#
# Revision 1.5  2005/09/24 09:11:46  ncq
# - enhance wxPython checks
#
# Revision 1.4  2005/01/16 20:02:53  ncq
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
