"""gmExceptions - classes for exceptions GNUmed modules may throw"""

#=====================================================================
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

class AccessDenied(Exception):
	def __init__(self, msg, source=None, code=None, details=None):
		self.errmsg = msg
		self.source = source
		self.code = code
		self.details = details
	#----------------------------------
	def __str__(self):
		txt = self.errmsg
		if self.source is not None:
			txt += '\nSource: %s' % self.source
		if self.code is not None:
			txt += '\nCode: %s' % self.code
		if self.details is not None:
			txt += '\n%s' % self.details
		return txt
	#----------------------------------
	def __repr__(self):
		txt = self.errmsg
		if self.source is not None:
			txt += '\nSource: %s' % self.source
		if self.code is not None:
			txt += '\nCode: %s' % self.code
		if self.details is not None:
			txt += '\n%s' % self.details
		return txt

#------------------------------------------------------------
class ConnectionError(Exception):
	#raised whenever the database backend connection fails
	def __init__(self, errmsg):
		self.errmsg=errmsg

	def __str__(self):
		return self.errmsg

#------------------------------------------------------------
# constructor errors
class ConstructorError(Exception):
	"""Raised when a constructor fails."""
	def __init__(self, errmsg = None):
		if errmsg is None:
			self.errmsg = "%s.__init__() failed" % self.__class__.__name__
		else:
			self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

# business DB-object exceptions
class NoSuchBusinessObjectError(ConstructorError):
	"""Raised when a business db-object can not be found."""
	def __init__(self, errmsg = None):
		if errmsg is None:
			self.errmsg = "no such business DB-object found"
		else:
			self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

#=====================================================================
