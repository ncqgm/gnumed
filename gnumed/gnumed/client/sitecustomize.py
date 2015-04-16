# -*- coding: utf-8 -*-
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
	normalized =    aString.replace(u'ä'.encode('latin-1'), u'(Ä|AE|Ae|A|E)'.encode('latin-1'))
	UnicodeDecodeError: 'ascii' codec can't decode byte 0xc4 in position 0: ordinal not in range(128)

when trying to search for a patient. There is a built-in test below
but that approach may not be fool-proof.
"""
#==============================================================
__author__  = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import sys

# flip this flag if you need to set the encoding explicitly
do_set_encoding = False

# - most European countries but shouldn't
#   hurt in US-ASCII countries, either
# - includes the EURO symbol
#def_encoding = 'iso8859-15'
def_encoding = 'utf-8'

# - for testing
#def_encoding = 'ascii'
#==============================================================
if __name__ == '__main__':
	print "------------------------------------------------"
	print "This file is not intended to be run standalone."
	print "It is used in the Python/GNUmed startup process."
	print "Please consult the Python docs for details."
	print "------------------------------------------------"
	sys.exit()

if do_set_encoding:
	print "GNUmed startup: Setting Python string encoding to [%s]" % def_encoding
	try:
		sys.setdefaultencoding(def_encoding)
	except LookupError:
		print "GNUmed startup: Cannot set Python string encoding to invalid value [%s]" % def_encoding
		print "GNUmed startup: Default Python string encoding is [%s]" % sys.getdefaultencoding()
		print "GNUmed startup: GNUmed is likely to fail where non-7-bit-ASCII is involved"
	except AttributeError:
		print "GNUmed startup: Python string encoding must have been set already ?!?"

#==============================================================
