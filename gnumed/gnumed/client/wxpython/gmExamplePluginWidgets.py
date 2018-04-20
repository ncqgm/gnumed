"""GNUmed measurement widgets.
"""
#================================================================
__version__ = "$Revision: 0.1 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL"

import sys, logging, datetime as pyDT, decimal

import wx	#, wx.grid

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.business import gmPerson
from Gnumed.pycommon import gmDispatcher, gmMatchProvider
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmPatSearchWidgets
"""
Now import the Panel that holds your widgets you designed with wxglade
adapt the name of the files and panel to match those you define in 
wxglade
"""
from Gnumed.wxGladeWidgets import wxgExamplePluginPnl

_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class cExamplePluginPnl(wxgExamplePluginPnl.wxgExamplePluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of widgets. Used as notebook page."""
	def __init__(self, *args, **kwargs):
		wxgExamplePluginPnl.wxgExamplePluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		pass
	#--------------------------------------------------------
	def repopulate_ui(self):
		_log.info('repopulate ui')
		self._populate_with_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		pass
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		""" uncomment the following lines if you need the current patient in your plugin"""
#		pat = gmPerson.gmCurrentPatient()
#		if not pat.connected:
#			return True

#		pat = gmPerson.gmCurrentPatient()

		self._TCTRL_template.SetValue('you did it!')
		return True
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmLog2, gmDateTime, gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

def show_template_pnl():
	pass

	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		show_template_pnl()