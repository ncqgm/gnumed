"""Python version dependant compatibility code.

@copyright: author
@license: GPL (details at http://www.gnu.org)
"""
#========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmPyCompat.py,v $
# $Id: gmPyCompat.py,v 1.2 2004-03-18 09:47:33 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# define dict() if < Python 2.2
try:
	dict(['a','b'])
except NameError:
	def dict(list):
		d = {}
		for line in list:
			d[line[0]] = line[1]
		return d

# define true/false if < Python 2.3
try:
	True
except NameError:
	True = (1==1)
	False = not True

#========================================================================
# $Log: gmPyCompat.py,v $
# Revision 1.2  2004-03-18 09:47:33  ncq
# - removed printk()
#
# Revision 1.1  2004/03/15 15:06:28  ncq
# - True/False and dict()
#
