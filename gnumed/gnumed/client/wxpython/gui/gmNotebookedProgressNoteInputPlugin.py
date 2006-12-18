#======================================================================
# GnuMed notebook based progress note input plugin
# ------------------------------------------------
#
# this plugin displays the list of patient problems
# toghether whith a notebook container for progress notes
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.12 $"
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

# GNUmed
from Gnumed.wxpython import gmPlugin, gmSOAPWidgets
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmNotebookedProgressNoteInputPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate multisash based progress note input window."""

	tab_name = _('Progress notes')

	def name (self):
		return gmNotebookedProgressNoteInputPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmSOAPWidgets.cNotebookedProgressNoteInputPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('Add progress notes'))

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
	from Gnumed.pycommon import gmCfg
	from Gnumed.business import gmPerson

	_cfg = gmCfg.gmDefCfgFile	
		
	_log.Log (gmLog.lInfo, "starting Notebooked progress notes input plugin...")

	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "None patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		# display standalone multisash progress notes input
		application = wx.wx.PyWidgetTester(size=(800,600))
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
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing Notebooked progress notes input plugin...")
#======================================================================
# $Log: gmNotebookedProgressNoteInputPlugin.py,v $
# Revision 1.12  2006-12-18 12:12:27  ncq
# - fix test suite
#
# Revision 1.11  2006/11/05 16:05:35  ncq
# - cleanup, tabify
#
# Revision 1.10  2006/10/31 16:06:19  ncq
# - no more gmPG
#
# Revision 1.9	2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.8	2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.7	2005/10/03 13:59:59  sjtan
# indentation errors
#
# Revision 1.6	2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.5	2005/09/12 15:11:15  ncq
# - tab name capitalized
#
# Revision 1.4	2005/06/30 10:21:01  cfmoro
# String corrections
#
# Revision 1.3	2005/06/07 10:19:18  ncq
# - string improvement
#
# Revision 1.2	2005/05/12 15:13:28  ncq
# - cleanup
#
# Revision 1.1	2005/05/08 21:45:25  ncq
# - new plugin for progress note input ...
#
