#======================================================================
# GnuMed EncounterEdit plugin
# ------------------------------------------------
#
""" Displays the tree of patient episodes and encounters,
 and last progress note (SOAP) for selected encounter.
 Allows to create new or modify existing progress note.
 Prepares the report for printing using supplied OpenOffice.org template.
"""
#
# @thanks: this code has been based on 
#          progress note plugin and scan doc plugin 
#          by Karsten Hilbert, Sebastian Hilbert and Carlos Moro
#======================================================================
__version__ = "$Revision: 1.1 $"
__author__ = "Jerzy Luszawski"
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

from Gnumed.wxpython import gmEncounterEditWidgets

#======================================================================
class gmEncounterEditPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate EncounterEdit window."""

	tab_name = _('Encounter edit')

	def name (self):
		return gmEncounterEditPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmEncounterEditWidgets.cEncounterEditPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('&Encounter add/edit'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return True
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	# 3rd party
	import wx

	# GNUmed
	from Gnumed.business import gmPerson, gmPersonSearch
	_log.info("starting encounter edit plugin...")

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
		patient = gmPersonSearch.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		# display standalone EncounterEdit window
		application = wx.wx.PyWidgetTester(size=(800,600))
		__frame = gmEncounterEditWidgets.cEncounterEditPnl(application.frame, -1)

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

	_log.info("closing encounter edit plugin...")

	#======================================================================

#======================================================================
# $Log: gmEncounterEditPlugin.py,v $
# Revision 1.1	Wed Sep 03 22:39:56 CEST 2008 @902 /Internet Time/
# - first public release: new plugin for adding and editing encounter
