"""
This is a cardiac device interrogation management plugin 
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmCardiacDevicePlugin.py,v $
__version__ = "$Revision: 1.4 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, logging


import wx


from Gnumed.wxpython import gmMeasurementWidgets, gmPlugin, gmNarrativeWidgets, gmDeviceWidgets

if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()



_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class gmCardiacDevicePlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate document tree."""

	tab_name = _("Cardiac Devices")

	def name (self):
		return gmCardiacDevicePlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		self._widget = gmDeviceWidgets.cCardiacDevicePluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('tools', _('Show &cardiac devices'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
		if kwds['sort_mode'] == 'review':
			self._widget._on_sort_by_review_selected(None)
		return True
	#--------------------------------------------------------
#	def populate_toolbar (self, tb, widget):
#		wxID_TB_BTN_show_page = wx.NewId()
#		tool1 = tb.AddTool(
#			wxID_TB_BTN_show_page,
#			images_Archive_plugin.getreportsBitmap(),
#			shortHelpString=_("show document"),
#			isToggle=False
#		)
#		wx.EVT_TOOL(tb, wxID_TB_BTN_show_page, self._widget._doc_tree.display_selected_part)
#		tb.AddControl(wx.StaticBitmap(
#			tb,
#			-1,
#			images_Archive_plugin.getvertical_separator_thinBitmap(),
#			wx.DefaultPosition,
#			wx.DefaultSize
#		))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	# 3rd party
	import wx

	# GNUmed
	from Gnumed.business import gmPerson
	from Gnumed.wxpython import gmSOAPWidgets
	
	_log.info("starting Notebooked cardiac device input plugin...")

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "None patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		# display standalone multisash progress notes input
		application = wx.wx.PyWidgetTester(size = (800,600))
		multisash_notes = gmMeasurementWidgets.cCardiacDeviceMeasurementsPnl(application.frame, -1)

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

	_log.info("closing Notebooked cardiac device input plugin...")
#================================================================
# $Log: gmCardiacDevicePlugin.py,v $
# Revision 1.4  2009-04-14 18:37:39  shilbert
# - description updated
#
# Revision 1.3  2009/04/13 15:34:55  shilbert
# - renamed class cCardiacDeviceMeasurmentPnl to cCardiacDevicePluginPnl
#
# Revision 1.2  2009/04/12 20:22:12  shilbert
# - make it run in pywidgettester
#
# Revision 1.1  2009/04/09 11:37:37  shilbert
# - first iteration of cardiac device management plugin