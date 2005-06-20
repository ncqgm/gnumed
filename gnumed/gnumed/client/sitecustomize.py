# -*- coding: iso-8859-1 -*-
"""GNUmed site customization file.

This file sets up the default string encoding for Python.

Some countries will be able to get by without this file,
eg those using the 7-bit US-ASCII character set (without
those weird accents and stuff). Most others will need to
set the proper value here.

Most European countries will be OK with 'iso8859-1' or
'iso8859-15'. On Linux you can find out a suitable encoding
by running "locale charmap". On Windows, tough luck.

If you need this file you will see an error like this:

File "/usr/lib/python2.4/site-packages/Gnumed/business/gmPerson.py", line 836, in __normalize
	normalized =    aString.replace(u'Ä'.encode('latin-1'), u'(Ä|AE|Ae|A|E)'.encode('latin-1'))
	UnicodeDecodeError: 'ascii' codec can't decode byte 0xc4 in position 0: ordinal not in range(128)

when trying to search for a patient. There is a built-in test below
but that approach may not be fool-proof.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/sitecustomize.py,v $
# $Id: sitecustomize.py,v 1.2 2005-06-20 19:42:25 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__  = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

# some handy definitions:
# - most European countries,+
# - shouldn't hurt in US-ASCII countries, either
def_encoding = 'iso8859-1'
# - if you need the EURO symbol
#def_encoding = 'iso8859-15'
# - might work, too
#def_encoding = 'latin1'
# - for testing
#def_encoding = 'ascii'
#==============================================================
def __setup_encoding():
	import sys
	print "GNUmed startup: Setting Python string encoding to:", def_encoding
	try:
		sys.setdefaultencoding(def_encoding)
	except LookupError:
		print "GNUmed startup: Cannot set Python string encoding to invalid value:", def_encoding
		print "GNUmed startup: Default Python string encoding is:", sys.getdefaultencoding()
	except AttributeError:
		print "GNUmed startup: Python string encoding must have been set already ?!?"
		raise
#==============================================================
try:
	tmp = u'Ä'.encode('latin-1')
	print "GNUmed startup: Your Python string encoding seems to already be set:", sys.getdefaultencoding()
except:
	__setup_encoding()

#==============================================================
# $Log: sitecustomize.py,v $
# Revision 1.2  2005-06-20 19:42:25  ncq
# - improved
#
# Revision 1.1  2005/06/20 18:54:32  ncq
# - can be used as an example
#
