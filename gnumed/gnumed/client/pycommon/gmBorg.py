#===================================================
# Thanks to Python Patterns !
# ---------------------------
# $Id: gmBorg.py,v 1.4 2007-09-24 22:05:23 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

#===================================================
class cBorgOld:
	"""A generic Borg mixin for old-style classes.

	- mixin this class with your class' ancestors to borg it
	- call cBorg.__init__(self) right away in your own __init__()

	- there may be many instances of this but they all share state

	CAVE: ALL inherited classes share state !!!
	"""
	_shared_state = {}

	def __init__(self):
		# share state among all instances ...
		self.__dict__ = self._shared_state
#===================================================
class cBorg(object):
	"""A generic Borg mixin for new-style classes.

	- mixin this class with your class' ancestors to borg it

	- there may be many instances of this - PER CHILD CLASS - but they all share state
	"""
	_instances = {}

	def __new__(cls, *args, **kargs):
		# look up sublcass instance cache
		if cBorg._instances.get(cls) is None:
			cBorg._instances[cls] = object.__new__(cls, *args, **kargs)
		return cBorg._instances[cls]
#===================================================
if __name__ == '__main__':

	class A(cBorg):
		pass

	class B(cBorg):
		pass

	print "testing old-style classes borg"
	a1 = cBorgOld()
	a2 = cBorgOld()
	a1.a = 5
	print a1.a, "==", a2.a
	a3 = cBorgOld()
	print a1.a, "==", a2.a, "==", a3.a

	print "testing new-style classes borg"
	a1 = A()
	a2 = A()
	a1.a = 5
	print a1.a, "==", a2.a
	a3 = A()
	print a1.a, "==", a2.a, "==", a3.a
	b1 = B()
	b1.a = 10
	print b1.a
	print a1.a
	b2 = B()
	print b2.a

#===================================================
# $Log: gmBorg.py,v $
# Revision 1.4  2007-09-24 22:05:23  ncq
# - improved docs
#
# Revision 1.3  2007/05/11 14:14:59  ncq
# - make borg per-sublcass
#
# Revision 1.2  2007/05/07 12:30:05  ncq
# - make cBorg an object child so properties work on it
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.3  2003/12/29 16:21:51  uid66147
# - spelling fix
#
# Revision 1.2  2003/11/17 10:56:35  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.1  2003/04/02 16:07:55  ncq
# - first version
#
