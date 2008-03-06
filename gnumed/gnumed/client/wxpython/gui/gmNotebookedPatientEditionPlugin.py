#======================================================================
# GnuMed notebook based patient edition plugin
# ------------------------------------------------
#
# this plugin displays a notebook container for patient edition
# current pages (0.1): identity, contacts, occupation
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.11 $"
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

import logging


if __name__ == '__main__':

	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

# GNUmed
from Gnumed.wxpython import gmPlugin, gmDemographicsWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#======================================================================
class gmNotebookedPatientEditionPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate notebooked patient edition window."""

	tab_name = _('Patient details')

	def name (self):
		return gmNotebookedPatientEditionPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmDemographicsWidgets.cNotebookedPatEditionPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('patient', _('Edit demographics'))

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
	from Gnumed.business import gmPerson

	_log.info("starting Notebooked patient edition plugin...")

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "None patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)
					
		# display standalone notebooked patient editor
		application = wx.PyWidgetTester(size=(800,600))
		application.SetWidget(gmDemographicsWidgets.cNotebookedPatEditionPanel, -1)
		
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

	_log.info("closing Notebooked progress notes input plugin...")

#======================================================================
# $Log: gmNotebookedPatientEditionPlugin.py,v $
# Revision 1.11  2008-03-06 18:32:31  ncq
# - standard lib logging only
#
# Revision 1.10  2008/01/27 21:21:59  ncq
# - no more gmCfg
#
# Revision 1.9  2008/01/22 12:26:24  ncq
# - better tab names
#
# Revision 1.8  2006/12/15 16:31:32  ncq
# - fix test suite
#
# Revision 1.7	2006/10/31 16:06:19  ncq
# - no more gmPG
#
# Revision 1.6	2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.5	2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.4	2005/10/03 13:49:21  sjtan
# using new wx. temporary debugging to stdout(easier to read). where is rfe ?
#
# Revision 1.3	2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.2	2005/05/26 15:57:03  ncq
# - slightly better strings
#
# Revision 1.1	2005/05/25 22:52:47  cfmoro
# Added notebooked patient edition plugin
#
