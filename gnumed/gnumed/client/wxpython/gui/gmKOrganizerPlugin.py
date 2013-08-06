#=====================================================
# GNUmed KOrganizer link
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmKOrganizerPlugin.py,v $
# $Id: gmKOrganizerPlugin.py,v 1.4 2009-06-29 15:13:25 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import os, sys

from Gnumed.wxpython import gmPlugin, gmDemographicsWidgets
from Gnumed.pycommon import gmExceptions, gmShellAPI
from Gnumed.wxpython import gmAccessPermissionWidgets

#======================================================================
class gmKOrganizerPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate a simple KOrganizer link window."""

	tab_name = _('Appointments')
	required_minimum_role = 'non-clinical access'

	@gmAccessPermissionWidgets.verify_minimum_required_role (
		required_minimum_role,
		activity = _('loading plugin <%s>') % tab_name,
		return_value_on_failure = False,
		fail_silently = False
	)
	def register(self):
		gmPlugin.cNotebookPlugin.register(self)
	#-------------------------------------------------
	#--------------------------------------------------------
	def __init__(self):
		# detect KOrganizer
		found, cmd = gmShellAPI.detect_external_binary(binary = 'konsolekalendar')
		if not found:
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
		return ('office', _('&Appointments'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
#======================================================================
# $Log: gmKOrganizerPlugin.py,v $
# Revision 1.4  2009-06-29 15:13:25  ncq
# - improved placement in menu hierarchy
# - add active letters
#
# Revision 1.3  2008/01/14 20:46:20  ncq
# - use detect_external_binary()
#
# Revision 1.2  2007/10/12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.1  2007/07/09 11:10:24  ncq
# - new plugin :-)
#
# Revision 1.1  2007/04/06 23:09:13  ncq
# - this is new
#
#