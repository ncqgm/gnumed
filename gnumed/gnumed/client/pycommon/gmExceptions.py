#############################################################################
#
# gmExceptions - classes for exceptions gnumed modules may throw
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	07.02.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################


class ConnectionError(Exception):
	#raised whenever the database backend connection fails
	def __init__(self, errmsg):
		self.errmsg=errmsg

	def __str__(self):
		return self.errmsg

class ConfigError(Exception):
	#raised whenever a configuration error occurs
	def __init__(self, errmsg):
		self.errmsg=errmsg

	def __str__(self):
		return self.errmsg



class NoGuiError(Exception):
	#raised whenever the database backend connection fails
	def __init__(self, errmsg):
		self.errmsg=errmsg

	def __str__(self):
		return self.errmsg


class PureVirtualFunction(Exception):
	#raised whenever the database backend connection fails
	def __init__(self, errmsg=None):
		if errmsg is not None:
			self.errmsg=errmsg
		else:
			self.errmsg="Attempt to call a pure virtual function!"

	def __str__(self):
		return self.errmsg


class ConstructorError(Exception):
	"""Raised when a constructor fails."""
	def __init__(self, errmsg = None):
		if errmsg is None:
			self.errmsg = "%s.__init__() failed" % self.__class__.__name__
		else:
			self.errmsg = errmsg

	def __str__(self):
		return self.errmsg


class InvalidInputError(Exception):
	"""Raised by business layers when an attempt is made to input
	invalid data"""
	def __init__(self, errmsg = None):
		if errmsg is None:
			self.errmsg = "%s.__init__() failed" % self.__class__.__name__
		else:
			self.errmsg = errmsg

	def __str__(self):
		return self.errmsg

#=====================================================================
# $Log: gmExceptions.py,v $
# Revision 1.3  2004-03-27 04:37:01  ihaywood
# lnk_person2address now lnk_person_org_address
# sundry bugfixes
#
# Revision 1.2  2004/03/10 00:14:04  ncq
# - fix imports
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
