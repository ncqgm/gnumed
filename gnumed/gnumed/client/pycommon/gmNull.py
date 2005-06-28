"""null.py

This is a sample implementation of the 'Null Object' design pattern.

Roughly, the goal with Null objects is to provide an 'intelligent'
replacement for the often used primitive data type None in Python or
Null (or Null pointers) in other languages. These are used for many
purposes including the important case where one member of some group 
of otherwise similar elements is special for whatever reason. Most 
often this results in conditional statements to distinguish between
ordinary elements and the primitive Null value.

Among the advantages of using Null objects are the following:

  - Superfluous conditional statements can be avoided 
	by providing a first class object alternative for 
	the primitive value None.

  - Code readability is improved.

  - Null objects can act as a placeholder for objects 
	with behaviour that is not yet implemented.

  - Null objects can be replaced for any other class.

  - Null objects are very predictable at what they do.

To cope with the disadvantage of creating large numbers of passive 
objects that do nothing but occupy memory space Null objects are 
often combined with the Singleton pattern.

For more information use any internet search engine and look for 
combinations of these words: Null, object, design and pattern.

Dinu C. Gherman,
August 2001

For modifications see CVS changelog below.

Karsten Hilbert
July 2004
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmNull.py,v $
__version__ = "$Revision: 1.6 $"
__author__ = "Dinu C. Gherman"
__license__ = "GPL (details at http://www.gnu.org)"

#==============================================================
class cNull:
	"""A class for implementing Null objects.

	This class ignores all parameters passed when constructing or 
	calling instances and traps all attribute and method requests. 
	Instances of it always (and reliably) do 'nothing'.

	The code might benefit from implementing some further special 
	Python methods depending on the context in which its instances 
	are used. Especially when comparing and coercing Null objects
	the respective methods' implementation will depend very much
	on the environment and, hence, these special methods are not
	provided here.
	"""
	_warn = 0

	# object constructing
	
	def __init__(self, *args, **kwargs):
		"Ignore parameters."
		try:
			cNull._warn = kwargs['warn']
		except KeyError:
			pass
		return None

	# object calling

	def __call__(self, *args, **kwargs):
		"Ignore method calls."
		if cNull._warn:
			print "cNull.__call__()"
		return self

	# attribute handling

	def __getattr__(self, mname):
		"Ignore attribute requests."
		if cNull._warn:
			print "cNull.__getattr__()"
		return self

	def __setattr__(self, name, value):
		"Ignore attribute setting."
		if cNull._warn:
			print "cNull.__setattr__()"
		return self

	def __delattr__(self, name):
		"Ignore deleting attributes."
		if cNull._warn:
			print "cNull.__delattr__()"
		return self

	# misc.

	def __repr__(self):
		"Return a string representation."
		if cNull._warn:
			print "cNull.__repr__()"
		return "<cNull instance @ %s>" % id(self)

	def __str__(self):
		"Convert to a string and return it."
		if cNull._warn:
			print "cNull.__str__()"
		return "cNull instance"

	def __nonzero__(self):
		if cNull._warn:
			print "cNull.__nonzero__()"
		return 0
        
	def __len__(self):
		if cNull._warn:
			print "cNull.__len__()"
		return 0        

#==============================================================
def test():
	"Perform some decent tests, or rather: demos."

	# constructing and calling

	n = cNull()
	n = cNull('value')
	n = cNull('value', param='value', warn=1)

	n()
	n('value')
	n('value', param='value')

	# attribute handling

	n.attr1
	n.attr1.attr2
	n.method1()
	n.method1().method2()
	n.method('value')
	n.method(param='value')
	n.method('value', param='value')
	n.attr1.method1()
	n.method1().attr1

	n.attr1 = 'value'
	n.attr1.attr2 = 'value'

	del n.attr1
	del n.attr1.attr2.attr3

	# representation and conversion to a string
	tmp = '<cNull instance @ %s>' % id(n)
	assert repr(n) == tmp
	assert str(n) == 'cNull instance'

	# comparing
	if n == 1:
		print "Null object == 1"
	else:
		print "Null object != 1"
#--------------------------------------------------------------
if __name__ == '__main__':
	test()

#==============================================================
# $Log: gmNull.py,v $
# Revision 1.6  2005-06-28 14:12:55  cfmoro
# Integration in space fixes
#
# Revision 1.5  2004/12/22 08:40:01  ncq
# - make output more obvious
#
# Revision 1.4  2004/11/24 15:49:11  ncq
# - use 0/1 not False/True so we can run on older pythons
#
# Revision 1.3  2004/08/20 08:38:47  ncq
# - robustify while working on allowing inactive patient after search
#
# Revision 1.2  2004/07/21 07:51:47  ncq
# - tabified
# - __nonzero__ added
# - if keyword argument 'warn' is True: warn on use of Null class
#
# Revision 1.1	2004/07/06 00:08:31	 ncq
# - null design pattern from python cookbook
#
