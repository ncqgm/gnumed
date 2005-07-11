#!/bin/python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/check-prerequisites.py,v $
# $Revision: 1.5 $

import sys

print "=> checking for Python module mxDateTime ..."
try:
	import mx.DateTime
	print "=> found"
except ImportError:
	print "ERROR: mxDateTime not installed"
	print "ERROR: this is needed to handle dates and times"
	print "ERROR: mxDateTime is available from http://www.egenix.com/files/python/"
	sys.exit(-1)

print "=> checking for Python module pyPgSQL ..."
try:
	import pyPgSQL.PgSQL
	print "=> found"
except ImportError:
	print "ERROR: pyPgSQL not installed"
	print "ERROR: this is needed to access PostgreSQL"
	print "ERROR: pyPgSQL is available from http://pypgsql.sourceforge.net"
	sys.exit(-1)

print "=> checking for Python module wxPython ..."
import os
if os.getenv('DISPLAY') is None:
	print "WARNING: cannot check for module wxPython"
	print "WARNING: you must run this in a GUI terminal window"
else:
	try:
		import wxPython.wx
		print "=> found"
	except ImportError:
		print "ERROR: wxPython not installed"
		print "ERROR: this is needed to show the GNUmed GUI"
		print "ERROR: wxPython is available from http://www.wxpython.org"
		print "INFO : on Mac OSX Panther you may have to use 'export DISPLAY=:0'"
		sys.exit(-1)

print "=> Most likely you can run GNUmed without problems."
sys.exit(0)

#=================================================================
# $Log: check-prerequisites.py,v $
# Revision 1.5  2005-07-11 08:31:23  ncq
# - string fixes
#
# Revision 1.4  2005/02/21 18:05:38  ncq
# - add some reassuring text in the case of success
#
# Revision 1.3  2004/07/05 03:33:55  dgrant
# Removed extraneous print "found"
#
# Revision 1.2  2004/05/29 22:39:14  ncq
# - warn on export DISPLAY on Mac OSX
#
# Revision 1.1  2004/02/19 16:51:08  ncq
# - first version
#
