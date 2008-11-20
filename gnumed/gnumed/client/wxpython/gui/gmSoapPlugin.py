#======================================================================
# GNUmed notebook based progress note input plugin
# ------------------------------------------------
#
# this plugin displays the list of patient problems
# together whith a notebook container for progress notes
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.1 $"
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
from Gnumed.wxpython import gmPlugin, gmNarrativeWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)

#======================================================================
class gmSoapPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate notebook based progress note input window."""

	tab_name = _('Progress notes 2')

	def name (self):
		return gmSoapPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmNarrativeWidgets.cSoapPluginPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('&Progress notes editor 2'))

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
	from Gnumed.business import gmPerson

	_log.info("starting Notebooked progress notes input plugin...")

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "None patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		# display standalone multisash progress notes input
		application = wx.wx.PyWidgetTester(size = (800,600))
		multisash_notes = gmSOAPWidgets.cNotebookedProgressNoteInputPanel(application.frame, -1)

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
# $Log: gmSoapPlugin.py,v $
# Revision 1.1  2008-11-20 20:30:49  ncq
# - new plugin
#
#