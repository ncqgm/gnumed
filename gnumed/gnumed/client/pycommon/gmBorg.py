# -*- coding: utf-8 -*-
"""A base class turning child classes into a Singleton."""

__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

#===================================================
class cBorg(object):
	"""A generic Borg mixin for new-style classes.

	- mixin this class with your class' ancestors to borg it

	- there may be many _instances_ of this - PER CHILD CLASS - but they all share _state_
	"""
	_instances:dict = {}

	def __new__(cls, *args, **kargs):
		# look up subclass instance cache
		if cBorg._instances.get(cls) is None:
			#cBorg._instances[cls] = object.__new__(cls, *args, **kargs)
			cBorg._instances[cls] = object.__new__(cls)
		return cBorg._instances[cls]

#===================================================
if __name__ == '__main__':

	import sys

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	class A(cBorg):
		pass

	class B(cBorg):
		pass

	class C(cBorg):
		def __init__(self, val='default'):
			self.x = val

	#===================================================
	print("testing new-style classes borg")
	a1 = A()
	a2 = A()
	a1.a = 5									# type: ignore
	print(a1.a, "==", a2.a)						# type: ignore
	a3 = A()
	print(a1.a, "==", a2.a, "==", a3.a)			# type: ignore
	b1 = B()
	b1.a = 10									# type: ignore
	print(b1.a)									# type: ignore
	print(a1.a)									# type: ignore
	b2 = B()
	print(b2.a)									# type: ignore

	c1 = C(val = 'non-default')
	print(c1.x)
	c2 = C(val = 'non-default 2')
	print(c2.x)
	c3 = C()
	print(c3.x)

#===================================================
