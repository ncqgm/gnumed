"""GNUmed patient EMR tree browser
"""
#======================================================================
#
# this plugin holds patient EMR tree
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 2.1 $"
__author__ = "Jerzy Luszawski, Carlos Moro"
__license__ = 'GPL (details at http://www.gnu.org)'
if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

import logging


from Gnumed.wxpython import gmPlugin
from Gnumed.pycommon import gmI18N

_log = logging.getLogger('gm.ui')
_log.info(__version__)
from Gnumed.wxpython import gmEMRMultiViewWidgets
#======================================================================
class gmEMRMultiViewPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient EMR multi view window."""

	tab_name = _('EMR multi view')
	def name(self):
		return gmEMRMultiViewPlugin.tab_name
	#-------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmEMRMultiViewWidgets.cSplittedEMRTreeBrowserPnl(parent, -1)
		#		self._widget = gmEMRBrowser.cEMRBrowserPanel(parent, -1)
		#		self._widget = gmEMRBrowser.cScrolledEMRTreePnl(parent, -1)
		#		from Gnumed.wxpython import gmMedDocWidgets
		#		self._widget = gmMedDocWidgets.cSelectablySortedDocTreePnl(parent, -1)
		return self._widget
	#-------------------------------------------------
	def MenuInfo(self):
		return ('emr_show', _('multi view'))
	#-------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	# 3rd party
	import wx

	# GNUmed
	from Gnumed.exporters import gmPatientExporter
	from Gnumed.business import gmPerson
	_log.info("starting EMR multi view plugin...")

	#DEBUG
	from Gnumed.pycommon import gmPG2, gmLoginInfo
	login = gmLoginInfo.LoginInfo()
	login.host = 'localhost'
	login.database = 'gnumed_jl_test'
	login.user = 'any-doc'
	login.password = 'any-doc'
	login.port = 5432
	gmPG2.set_default_login(login=login)
	#\DEBUG
	try:
		# obtain patient
		#patient = gmPerson.ask_for_patient()
		patient = gmPerson.cPatient(aPK_obj=12)
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		# display standalone EncounterEdit window
		application = wx.wx.PyWidgetTester(size=(800,600))
		__frame = gmEMRMultiViewWidgets.cSplittedEMRTreeBrowserPnl(application.frame, -1)
		__frame.repopulate_ui()

		application.frame.Show(True)
		application.MainLoop()

		# clean up
		if patient is not None:
			try:
				patient.cleanup()
			except:
				print "error cleaning up patient"
	except StandardError:
		_log.exception("unhandled exception caught !")
		# but re-raise them
		raise

	_log.info("closing EMR multi view plugin")

	#======================================================================

#======================================================================
# $Log: gmEMRMultiViewPlugin.py,v $
# Revision 2.1  2009/09/02 23:22:01  jl
# - added view type radiobox (for switching to journal and log view)
# - added print button for right pane
#
# Revision 1.16  2008/03/06 18:32:30  ncq
# - standard lib logging only
#
# Revision 1.15  2008/01/27 21:21:59  ncq
# - no more gmCfg
#
# Revision 1.14  2007/10/12 07:28:24  ncq
# - lots of import related cleanup
#
# Revision 1.13  2006/10/31 16:06:19  ncq
# - no more gmPG
#
# Revision 1.12  2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.11  2006/05/28 16:18:52  ncq
# - use new splitter plugin class
#
# Revision 1.10  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.9  2005/12/27 19:05:36  ncq
# - use gmI18N
#
# Revision 1.8  2005/09/28 21:38:11  ncq
# - more 2.6-ification
#
# Revision 1.7  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.6  2005/06/07 20:56:56  ncq
# - take advantage of improved EMR menu
#
# Revision 1.5  2005/03/29 07:33:47  ncq
# - fix naming
#
# Revision 1.4  2005/03/11 22:53:37  ncq
# - ask_for_patient() is now in gmPerson
#
# Revision 1.3  2004/10/31 00:35:40  cfmoro
# Fixed some method names. Added sys import. Refesh browser at startup in standalone mode
#
# Revision 1.2  2004/09/25 13:12:15  ncq
# - switch to from wxPython import wx
#
# Revision 1.1  2004/09/06 18:59:18  ncq
# - Carlos wrote a plugin wrapper for us
#
