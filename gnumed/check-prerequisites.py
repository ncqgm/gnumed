#!/bin/python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/check-prerequisites.py,v $
# $Revision: 1.22 $

import sys

missing = False

print "Checking for Python modules"
print "==========================="

print " mx.DateTime...",
try:
	import mx.DateTime
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: mxDateTime not installed"
	print "  ERROR: this is needed to handle dates and times"
	print "  ERROR: mxDateTime is available from http://www.egenix.com/files/python/"

print " enchant...",
try:
	import enchant
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: 'enchant' not installed"
	print "  ERROR: this is used to handle spellchecking"

print " psycopg2...",
try:
	import psycopg2
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: psycopg2 not installed"
	print "  ERROR: this is needed to access PostgreSQL"
	print "  ERROR: psycopg2 is available from http://www.initd.org/"

print " wx(version)...",
if hasattr(sys, 'frozen'):
	print "cannot check"
	print "  INFO : py2exe or similar in use, cannot check wxPython version"
	print "  INFO : skipping test and hoping for the best"
	print "  INFO : wxPython must be >= v2.8 and unicode-enabled"
else:
	try:
		import wxversion
		print "found"
		print "  selecting unicode enabled version >= 2.8...",
		wxversion.select(versions='2.8-unicode', optionsRequired=True)
		print "success"
	except ImportError:
		missing = True
		print ""
		print "  ERROR: wxversion not installed"
		print "  ERROR: this is used to select the proper wxPython version"
		print "  INFO : for details, see here:"
		print "  INFO : http://wiki.wxpython.org/index.cgi/MultiVersionInstalls"
		print "  INFO : skipping test and hoping for the best"
		print "  INFO : wxPython must be >= v2.8 and unicode-enabled"
	except wxversion.VersionError:
		print "failure"
		print "  ERROR: wxPython-2.8-unicode not installed"
		print "  ERROR: this is needed to show the GNUmed GUI"
		print "  INFO : wxPython is available from http://www.wxpython.org"

print " wx(python)...",
try:
	import wx
	print "found"
#	print "  active version:", wx.VERSION_STRING
#	try:
#		print "  platform info:", wx.PlatformInfo
#	except: pass
except ImportError:
	missing = True
	print ""
	import os
	if os.getenv('DISPLAY') is None:
		print "  INFO : you may have to explicitely set $DISPLAY"
	print "  ERROR: wxPython not installed"
	print "  ERROR: this is needed to show the GNUmed GUI"
	print "  INFO : wxPython is available from http://www.wxpython.org"
	print "  INFO : on Mac OSX Panther you may have to use 'export DISPLAY=:0'"

print " uno...",
try:
	import uno
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: uno not installed"
	print "  INFO : this is needed for form and letter handling"
	print "  INFO : GNUmed will work but you will be unable"
	print "  INFO : to use OpenOffice to write letters and"
	print "  INFO : fill in forms"

print " Gnuplot...",
try:
	import Gnuplot
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: Gnuplot python binding not installed"
	print "  INFO : this is needed for data visualization"
	print "  INFO : GNUmed will work but you will be unable"
	print "  INFO : to visualize search results and lab data"

print " libxml2...",
try:
	import libxml2
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: libxml2 not installed"
	print "  INFO : this is needed to work with XML forms"

print " libxslt...",
try:
	import libxslt
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: libxslt not installed"
	print "  INFO : this is needed to work with XML forms"

print " GNUmed Python modules...",
try:
	from Gnumed.pycommon import gmNull
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: GNUmed's own Python modules not installed site-wide"
	print "  INFO : these handle most of the work in GNUmed"
	print "  INFO : it may still be possible to run GNUmed locally"
	print "  INFO : from a directory containing a CVS tree"

#print "=> checking for Python module 'sane' ..."
#try:
#	import sane
#	print "=> found"
#except ImportError:
#	print "  ERROR: sane not installed"
#	print "  INFO : this is needed to access scanners on Linux"
#	print "  INFO : GNUmed will work but you will be unable to scan"

print " twain...",
try:
	import twain
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: twain not installed"
	print "  INFO : this is needed to access scanners on Windows"
	print "  INFO : GNUmed will work but you will be unable to"
	print "  INFO : scan if you are on a Windows machine"

if missing:
	print ""
	print "sys.path is currently set as follows:"
	print " ", "\n  ".join(sys.path)
	sys.exit(-1)

print "\n****************************************************"
print "* Most likely you can run GNUmed without problems. *"
print "****************************************************"
sys.exit(0)

#=================================================================
# $Log: check-prerequisites.py,v $
# Revision 1.22  2009-11-24 19:51:59  ncq
# - add libxml2/libxslt
#
# Revision 1.21  2009/07/09 16:40:47  ncq
# - better output
#
# Revision 1.20  2009/02/27 11:59:06  ncq
# - improved output
#
# Revision 1.19  2008/07/24 17:51:27  ncq
# - cleanup
#
# Revision 1.18  2008/07/15 15:23:50  ncq
# - check for wxp2.8
#
# Revision 1.17  2007/09/24 18:25:12  ncq
# - gnuplot.py
#
# Revision 1.16  2007/09/16 01:01:03  ncq
# - check for python-uno
#
# Revision 1.15  2007/03/31 20:10:13  ncq
# - check for enchant Python module
#
# Revision 1.14  2007/01/29 11:55:05  ncq
# - drop check for SANE python module
# - more precise output
#
# Revision 1.13  2006/12/18 16:17:42  ncq
# - do not check for pyPgSQL anymore
#
# Revision 1.12  2006/11/05 18:00:06  ncq
# - drop check for pyPgSQL
#
# Revision 1.11  2006/09/01 15:31:13  ncq
# - add check for psycopg2
#
# Revision 1.10  2006/08/09 14:05:28  ncq
# - more unified output
# - better wxversion/wxPython detection
# - add checks for SANE/TWAIN
#
# Revision 1.9  2006/08/08 10:41:35  ncq
# - improve debug output
#
# Revision 1.8  2006/08/01 18:47:43  ncq
# - improved wording/readability
# - add test for GNUmed's own Python modules
#
# Revision 1.7  2005/10/15 11:29:14  ncq
# - some wxPythons don't support wx.PlatformInfo so don't error on it
#
# Revision 1.6  2005/09/24 09:11:46  ncq
# - enhance wxPython checks
#
# Revision 1.5  2005/07/11 08:31:23  ncq
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
