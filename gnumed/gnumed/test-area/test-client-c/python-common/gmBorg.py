#===================================================
# Thanks to Python Patterns !
# ---------------------------
# $Id: gmBorg.py,v 1.1 2003-10-23 06:02:38 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

#===================================================
class cBorg:
	"""A generic Borg mixin.

	- mixin this class with your class' ancestors to borg it
	- call Borg.__init__(self) right away in your own __init__()

	- there may be many instances of this but they all share state
	"""
	_shared_state = {}

	def __init__(self):
		# share state among all instances ...
		self.__dict__ = self._shared_state

#===================================================
# $Log: gmBorg.py,v $
# Revision 1.1  2003-10-23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.1  2003/04/02 16:07:55  ncq
# - first version
#
