# -*- coding: utf-8 -*-
#======================================================================
# GNUmed multisash based progress note input plugin
# -------------------------------------------------
#
# this plugin displays the list of patient problems
# toghether whith a multisash container for progress notes
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.15 $"
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmSOAPWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#======================================================================
class gmMultiSashedProgressNoteInputPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate multisash based progress note input window."""

	tab_name = _('progress notes (sash)')

	def name (self):
		return gmMultiSashedProgressNoteInputPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmSOAPWidgets.cMultiSashedProgressNoteInputPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('tools', _('progress notes'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

    import sys

    import wx

    from Gnumed.business import gmPersonSearch

    _log.info("starting multisashed progress notes input plugin...")

    # make sure we have a db connection
    pool = gmPG.ConnectionPool()

    # obtain patient
    patient = gmPersonSearch.ask_for_patient()
    if patient is None:
        print("None patient. Exiting gracefully...")
        sys.exit(0)
    gmPatSearchWidgets.set_active_patient(patient=patient)

    # display standalone multisash progress notes input
    application = wx.wxPyWidgetTester(size=(800,600))
    multisash_notes = gmSOAPWidgets.cMultiSashedProgressNoteInputPanel(application.frame, -1)

    application.frame.Show(True)
    application.MainLoop()

    # clean up
    if patient is not None:
        try:
            patient.cleanup()
        except Exception:
            print("error cleaning up patient")
    pool.StopListeners()

    _log.info("closing multisashed progress notes input plugin...")

#======================================================================
