#!/usr/bin/python

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
		print "  INFO : you may have to explicitly set $DISPLAY"
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

#print " simplejson...",
#try:
#	import simplejson
#	print "found"
#except ImportError:
#	missing = True
#	print ""
#	print "  ERROR: simplejson not installed"
#	print "  INFO : this is needed for accessing eGK/KVK/PKVK cards"
#	print "  INFO : GNUmed will work but you will be unable"
#	print "  INFO : to read German chipcards"

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
	from Gnumed.pycommon import gmTools
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

print " hl7...",
try:
	import hl7
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: hl7 not installed"
	print "  INFO : this is needed to work with HL7 data"
	print "  INFO : GNUmed will still work without it"

print " pysvg...",
try:
	import pysvg
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: pysvg not installed"
	print "  INFO : this is needed to print EMR timelines"
	print "  INFO : GNUmed will still work without it"
	print "  INFO : note that you need v0.2.1 (not 0.2.2)"
	print "  INFO :  <pip install pysvg==0.2.1>"

print " faulthandler...",
try:
	import faulthandler
	print "found"
except ImportError:
	missing = True
	print ""
	print "  ERROR: faulthandler not installed"
	print "  INFO : this is used to capture catastrophic faults"
	print "  INFO : GNUmed will still work without it"

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
