__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmTools.py,v 1.2 2006-10-31 16:03:06 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmTools.py,v $
__version__ = "$Revision: 1.2 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

#===========================================================================
def coalesce(initial=None, instead=None):
	"""Modelled after the SQL coalesce function.

	To be used to simplify constructs like:

	if value is None:
		real_value = some_other_value
	else:
		real_value = value
	print real_value
	"""
	if initial is None:
		return instead
	return initial
#---------------------------------------------------------------------------
def capitalize(text=None):
	"""Capitalize the first character but leave the rest alone."""
	return text[0].capitalize() + text[1:]

#===========================================================================
if __name__ == '__main__':

	print __doc__

	val = None
	print 'testing coalesce()'
	print 'value          : %s (%s)' % (val, type(val))
	print 'coalesce(value): %s (%s)' % (coalesce(val, 'something other than <None>'), type(coalesce(val, 'something other than <None>')))

	print 'testing capitalize()'
	for word in ['Boot', 'boot', 'booT', 'boots-Schau', 'boot camp']:
		print word, capitalize(word)

#===========================================================================
# $Log: gmTools.py,v $
# Revision 1.2  2006-10-31 16:03:06  ncq
# - add capitalize() and test
#
# Revision 1.1  2006/09/03 08:53:19  ncq
# - first version
#
#