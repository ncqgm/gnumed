#=====================================================
# GNUmed KOrganizer link
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmKOrganizerPlugin.py,v $
# $Id: gmKOrganizerPlugin.py,v 1.2 2007-10-12 07:28:25 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import os, sys

from Gnumed.wxpython import gmPlugin, gmDemographicsWidgets
from Gnumed.pycommon import gmExceptions

#======================================================================
class gmKOrganizerPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate a simple KOrganizer link window."""

	tab_name = _('Appointments')
	#--------------------------------------------------------
	def __init__(self):
		# detect KOrganizer
		cmd = 'which konsolekalendar'
		pipe = os.popen(cmd.encode(sys.getfilesystemencoding()), "r")
		tmp = pipe.readline()
		ret_code = pipe.close()
		if tmp == '':
			raise gmExceptions.ConstructorError('cannot detect "konsolekalendar" via [%s]' % cmd)

		gmPlugin.cNotebookPlugin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmKOrganizerPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmDemographicsWidgets.cKOrganizerSchedulePnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('office', _('Appointments'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
#======================================================================
# $Log: gmKOrganizerPlugin.py,v $
# Revision 1.2  2007-10-12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.1  2007/07/09 11:10:24  ncq
# - new plugin :-)
#
# Revision 1.1  2007/04/06 23:09:13  ncq
# - this is new
#
#