"""GnuMed date input widget

All GnuMed date input should happen via classes in
this module. Initially this is just a plain text box
but using this throughout GnuMed will allow us to
transparently add features.
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmDateTimeInput.py,v $
# $Id: gmDateTimeInput.py,v 1.1 2003-05-23 14:05:01 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"

import sys
if __name__ == "__main__":
	sys.path.append ("../python-common/")

import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	import gmI18N

import gmExceptions
from wxPython.wx import *
#==================================================
class gmDateInput(wxTextCtrl):
	def __init__(self, parent, *args, **kwargs):
		if len(args) < 2:
			if not kwargs.has_key('value'):
				kwargs['value'] = _('enter date here')
		wxTextCtrl.__init__(
			self,
			parent,
			*args,
			**kwargs
		)
	#----------------------------------------------
	def set_value(self, aValue = None):
		"""Only set value if it's a valid one."""
		pass
	#----------------------------------------------	
	def set_range(self, list_of_ranges):
	#----------------------------------------------
		pass
#==================================================
class gmTimeInput(wxTextCtrl):
	def __init__(self, parent, *args, **kwargs):
		if len(args) < 2:
			if not kwargs.has_key('value'):
				kwargs['value'] = _('enter time here')
		wxTextCtrl.__init__(
			self,
			parent,
			*args,
			**kwargs
		)
	#----------------------------------------------
#==================================================
# main
#--------------------------------------------------
if __name__ == '__main__':
	app = wxPyWidgetTester(size = (200, 80))
	app.SetWidget(gmDateInput, -1)
	app.MainLoop()
	app = wxPyWidgetTester(size = (200, 80))
	app.SetWidget(gmTimeInput, -1)
	app.MainLoop()
#==================================================
# $Log: gmDateTimeInput.py,v $
# Revision 1.1  2003-05-23 14:05:01  ncq
# - first implementation
#
