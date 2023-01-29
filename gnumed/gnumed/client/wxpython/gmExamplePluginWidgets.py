"""GNUmed measurement widgets.
"""
#================================================================
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL"

# stdlib
import sys, logging

# 3rd party
#import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher

#from Gnumed.business import gmPerson

from Gnumed.wxpython import gmRegetMixin
#from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')

#================================================================
# Import the Panel that holds your widgets you designed with
# wxglade and adapt the name of the files and panel to match
# those you defined in wxglade:
from Gnumed.wxGladeWidgets import wxgExamplePluginPnl

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

	from Gnumed.pycommon import gmDateTime, gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

def show_template_pnl():
	pass

	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		show_template_pnl()
