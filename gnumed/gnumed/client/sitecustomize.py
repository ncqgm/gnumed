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
# $Id: sitecustomize.py,v 1.3 2005-06-20 20:41:30 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__  = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys

# some handy definitions:

# - most European countries but shouldn't
#   hurt in US-ASCII countries, either
def_encoding = 'iso8859-1'

# - if you need the EURO symbol
#def_encoding = 'iso8859-15'

# - might work, too
#def_encoding = 'latin1'

# - for testing
#def_encoding = 'ascii'
#==============================================================
def __setup_encoding():
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
if __name__ == '__main__':
	print "------------------------------------------------"
	print "This file is note intended to be run standalone."
	print "It is used in the Python/GNUmed startup process."
	print "Please consult the Python docs for details."
	print "------------------------------------------------"
	sys.exit()

print "GNUmed startup: running sitecustomize.py"

try:
	tmp = u'ß'.encode('latin-1')
	# for testing uncomment the following line
	#tmp = u'ß'.encode('totally-bogus-encoding')
	print "GNUmed startup: Your Python string encoding seems to already be set to [%s]" % sys.getdefaultencoding()
except:
	__setup_encoding()

#==============================================================
# $Log: sitecustomize.py,v $
# Revision 1.3  2005-06-20 20:41:30  ncq
# - improved again, it might even work
#
# Revision 1.2  2005/06/20 19:42:25  ncq
# - improved
#
# Revision 1.1  2005/06/20 18:54:32  ncq
# - can be used as an example
#
