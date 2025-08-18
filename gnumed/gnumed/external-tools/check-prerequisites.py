#!/usr/bin/python3

import sys
import os

missing = False

print("Checking for Python modules")
print("===========================")

print(" psycopg2...", end=' ')
try:
	import psycopg2
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: psycopg2 not installed")
	print("  ERROR: this is needed to access PostgreSQL")
	print("  ERROR: psycopg2 is available from https://www.initd.org/")

print(" wxPython...", end=' ')
try:
	import wx
	print("found")
	print("  active version:", wx.VERSION_STRING)
	print("  platform info:", wx.PlatformInfo)
except ImportError:
	missing = True
	print("")
	import os
	if os.getenv('DISPLAY') is None:
		print("  INFO : you may have to explicitly set $DISPLAY")
	print("  ERROR: wxPython not installed")
	print("  ERROR: this is needed to show the GNUmed GUI")
	print("  INFO : wxPython is available from https://www.wxpython.org")
	print("  INFO : on Mac OSX Panther you may have to use 'export DISPLAY=:0'")

# needs to check for uno3
#print " uno...",
#try:
#	import uno
#	print "found"
#except ImportError:
#	missing = True
#	print ""
#	print "  ERROR: uno not installed"
#	print "  INFO : this is needed for form and letter handling"
#	print "  INFO : GNUmed will work but you will be unable"
#	print "  INFO : to use OpenOffice to write letters and"
#	print "  INFO : fill in forms"

#print(" Gnuplot...", end=' ')
#try:
#	import Gnuplot
#	print("found")
#except ImportError:
#	missing = True
#	print("")
#	print("  ERROR: Gnuplot python binding not installed")
#	print("  INFO : this is needed for data visualization")
#	print("  INFO : GNUmed will work but you will be unable")
#	print("  INFO : to visualize search results and lab data")

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

print(" libxml2...", end=' ')
try:
	import libxml2
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: libxml2 not installed")
	print("  INFO : this is needed to work with XML forms")

#print(" libxslt...", end=' ')
#try:
#	import libxslt
#	print("found")
#except ImportError:
#	missing = True
#	print("")
#	print("  ERROR: libxslt not installed")
#	print("  INFO : this is needed to work with XML forms")

print(" hl7...", end=' ')
try:
	import hl7
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: hl7 not installed")
	print("  INFO : this is needed to work with HL7 data")
	print("  INFO : GNUmed will still work without it")

print(" pysvg...", end=' ')
try:
	import pysvg
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: pysvg not installed")
	print("  INFO : this is needed to print EMR timelines")
	print("  INFO : GNUmed will still work without it")
	print("  INFO : note that you need v0.2.1 (not 0.2.2)")
	print("  INFO :  $> pip3 install pysvg==0.2.1")
	print("  INFO : (you may need to install <pip3> first)")

print(" packaging...", end=' ')
try:
	import packaging
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: packaging not installed")
	print("  INFO : this is needed to check Orthanc versions")

print(" mailcap...", end=' ')
try:
	import mailcap
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: mailcap not installed")
	print("  INFO : this is needed to work with mimetypes")

print(" vobject...", end=' ')
try:
	import vobject
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: vobject not installed")
	print("  INFO : this is used to handle vCard data")
	print("  INFO : GNUmed will still work without it")

print(" pyqrcode...", end=' ')
try:
	import pyqrcode
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: pyqrcode not installed")
	print("  INFO : this is used to create QR codes")

print(" pyudev...", end=' ')
try:
	import pyudev
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: pyudev not installed")
	print("  INFO : this is used to scan for USB/MMC/optical drives")

print(" psutil...", end=' ')
try:
	import psutil
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: psutil not installed")
	print("  INFO : this is used to scan for USB/MMC/optical drives")

print(" docutils...", end=' ')
try:
	import docutils
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: docutils not installed")
	print("  INFO : this is used to process reStructuredText")

print(" unidecode...", end=' ')
try:
	import unidecode
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: unidecode not installed")
	print("  INFO : this is used to transliterate names")
	print("  INFO : GNUmed will still work without it")

print(" httplib2...", end=' ')
try:
	import httplib2
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: httplib2 not installed")
	print("  INFO : this is used to access the Orthanc DICOM server")

print(" humblewx...", end=' ')
try:
	import humblewx
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: humblewx not installed")
	print("  INFO : this is used to display the EMR timeline")

#print "=> checking for Python module 'sane' ..."
#try:
#	import sane
#	print "=> found"
#except ImportError:
#	print "  ERROR: sane not installed"
#	print "  INFO : this is needed to access scanners on Linux"
#	print "  INFO : GNUmed will work but you will be unable to scan"

print(" twain...", end=' ')
try:
	import twain
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: twain not installed")
	print("  INFO : this is needed to access scanners on Windows")
	print("  INFO : GNUmed will work but you will be unable to")
	print("  INFO : scan if you are on a Windows machine")

print(" GNUmed Python modules...", end=' ')
try:
	from Gnumed.pycommon import gmTools
	print("found")
except ImportError:
	missing = True
	print("")
	print("  ERROR: GNUmed's own Python modules not installed site-wide")
	print("  INFO : these handle most of the work in GNUmed")
	print("  INFO : it may still be possible to run GNUmed locally")
	print("  INFO : from a directory containing a CVS tree")



if missing:
	print("")
	input('sys.path (press <ENTER> key to show):')
	print(' ', '\n  '.join(sys.path))
	for path in ['PYTHONPATH', 'LD_LIBRARY_PATH', 'PATH', 'DYLD_LIBRARY_PATH', 'LD_RUN_PATH']:
		try:
			paths = os.environ[path]
		except KeyError:
			continue
		print("")
		input('${%s} (press <ENTER> key to show):' % path)
		print('  %s' % paths)
	sys.exit(-1)

print("\n****************************************************")
print("* Most likely you can run GNUmed without problems. *")
print("****************************************************")
sys.exit(0)

#=================================================================
