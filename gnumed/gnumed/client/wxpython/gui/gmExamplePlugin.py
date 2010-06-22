"""
This is a template plugin 
"""
__version__ = "$Revision: 0.1 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL"

#================================================================
import os.path, sys, logging
import wx

if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

""" import the widgets from the file referencing the widgets 
for that particualr plugin (e.g. ExamplePlugin.
If you code your own plugin replace Example by something reflecting
what your plugin does. 
"""

from Gnumed.wxpython import gmPlugin, gmExamplePluginWidgets

_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
#The name of the class must match the filename of the plugin
class gmExamplePlugin(gmPlugin.cNotebookPlugin):
	#name of the plugin as it will appear as tab in GNUmed
	tab_name = _("Template Plugin")

	def name (self):
		return gmExamplePlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		#Sets up the GUI by instanciating the file containing the widget that make up the layout in the plugin
		self._widget = gmExamplePluginWidgets.cExamplePluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		#This will set the name of the Plugin in the GNUmed menu
		return ('emr', _('Show &ExamplePlugin'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		""" uncomment the next two lines if a patient
		needs to be active before the plugin """
		#if not self._verify_patient_avail():
		#	return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
		try:
			# add here any code you for the plugin executed after
			# raising the pugin
			pass
		except KeyError:
			pass
		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	# GNUmed
	from Gnumed.business import gmPerson
	from Gnumed.wxpython import gmPatSearchWidgets

	_log.info("starting template plugin...")

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "None patient. Exiting gracefully..."
			sys.exit(0)
		gmPatSearchWidgets.set_active_patient(patient=patient)

		# display the plugin standalone
		application = wx.wx.PyWidgetTester(size = (800,600))
		widgets = gmExamplePluginWidgets.cExamplePluginPnl(application.frame, -1)

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