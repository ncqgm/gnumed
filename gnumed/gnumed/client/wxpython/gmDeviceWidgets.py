"""GNUmed measurement widgets.
"""
#================================================================
__version__ = "$Revision: 1.17 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, logging, datetime as pyDT, decimal, StringIO
from lxml import etree

import wx	#, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.business import gmPerson, gmDevices, gmDocuments, gmPersonSearch
from Gnumed.pycommon import gmDispatcher, gmMatchProvider
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmPatSearchWidgets
from Gnumed.wxGladeWidgets import wxgCardiacDevicePluginPnl

_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class cCardiacDevicePluginPnl(wxgCardiacDevicePluginPnl.wxgCardiacDevicePluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of widgets to manage implanted cardiac devices. Used as notebook page."""
	def __init__(self, *args, **kwargs):
		wxgCardiacDevicePluginPnl.wxgCardiacDevicePluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		# check if report types exist in db, if not create them
		self.__checkup_doc_type = u'cardiac device checkup report'
		dtype = gmDocuments.create_document_type(self.__checkup_doc_type)
		# cannot reuse self.__checkup_doc_type here or else it wouldn't get translated
		dtype.set_translation(_('cardiac device checkup report'))

		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		#self.data_grid.patient = None
		pass
	#--------------------------------------------------------
	def repopulate_ui(self):
		_log.info('repopulate ui')
		self._populate_with_data()
	#--------------------------------------------------------
	#def _on_select_button_pressed(self, evt):
	#	if self._RBTN_my_unsigned.GetValue() is True:
	#		self.data_grid.select_cells(unsigned_only = True, accountables_only = True, keep_preselections = False)
	#	elif self._RBTN_all_unsigned.GetValue() is True:
	#		self.data_grid.select_cells(unsigned_only = True, accountables_only = False, keep_preselections = False)
	#--------------------------------------------------------
	#def __on_sign_current_selection(self, evt):
	#	self.data_grid.sign_current_selection()
	#--------------------------------------------------------
	#def __on_delete_current_selection(self, evt):
	#	self.data_grid.delete_current_selection()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		pass
		#self.__action_button_popup = wx.Menu(title = _('Act on selected results'))

		#menu_id = wx.NewId()
		#self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('Review and &sign')))
		#wx.EVT_MENU(self.__action_button_popup, menu_id, self.__on_sign_current_selection)

		#menu_id = wx.NewId()
		#self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('Export to &file')))
		##wx.EVT_MENU(self.__action_button_popup, menu_id, self.data_grid.current_selection_to_file)
		#self.__action_button_popup.Enable(id = menu_id, enable = False)

		#menu_id = wx.NewId()
		#self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('Export to &clipboard')))
		##wx.EVT_MENU(self.__action_button_popup, menu_id, self.data_grid.current_selection_to_clipboard)
		#self.__action_button_popup.Enable(id = menu_id, enable = False)

		#menu_id = wx.NewId()
		#self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('&Delete')))
		#wx.EVT_MENU(self.__action_button_popup, menu_id, self.__on_delete_current_selection)
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):

		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return True

		# get documents of type self.__checkup_doc_type
		pat = gmPerson.gmCurrentPatient()
		doc_folder = pat.get_document_folder()
		checkups = doc_folder.get_documents(doc_type = self.__checkup_doc_type)
		_log.info(checkups)

		text = _('There are no device checkup reports in the database.')
		if len(checkups) != 0:
			# since get_documents() is sorted I simply get the first one as the most recent one
			# for now assume that the xml file provide the cardiac device context.
			# that pretty much means logical connection of leads and generator is provided in the xml
			xml_fname = checkups[-1].parts[0].export_to_file()
			tree = etree.parse(xml_fname)
			DevicesDisplayed = gmDevices.device_status_as_text(tree)
			text = u''.join(DevicesDisplayed)

		self._TCTRL_current_status.SetValue(text)

		return True
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmLog2, gmDateTime, gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#------------------------------------------------------------
	def test_grid():
		pat = gmPersonSearch.ask_for_patient()
		app = wx.PyWidgetTester(size = (500, 300))
		lab_grid = cMeasurementsGrid(parent = app.frame, id = -1)
		lab_grid.patient = pat
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------
	def test_test_ea_pnl():
		pat = gmPersonSearch.ask_for_patient()
		gmPatSearchWidgets.set_active_patient(patient=pat)
		app = wx.PyWidgetTester(size = (500, 300))
		ea = cMeasurementEditAreaPnl(parent = app.frame, id = -1)
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		#test_grid()
		test_test_ea_pnl()

#================================================================
# $Log: gmDeviceWidgets.py,v $
# Revision 1.17  2009-07-18 19:26:35  shilbert
# - now actually returns the most recent interrogation
#
# Revision 1.16  2009/07/18 17:48:24  shilbert
# - debugging repopulate_ui()
#
# Revision 1.15  2009/07/18 14:33:02  ncq
# - some more cleanup
#
# Revision 1.14  2009/07/17 22:18:45  ncq
# - a *bit* of cleanup ;-)
#
# Revision 1.13  2009/07/17 21:08:07  shilbert
# - cleanup
#
# Revision 1.12  2009/07/17 19:57:06  shilbert
# - now gets xml data from database
#
# Revision 1.11  2009/07/16 20:25:08  shilbert
# - fixed typos and syntax errors
#
# Revision 1.10  2009/07/16 19:59:06  shilbert
# - xml should now be gotten from database
#
# Revision 1.9  2009/07/15 20:13:37  shilbert
# - first step to getting xml from database
#
# Revision 1.8  2009/06/04 16:30:30  ncq
# - use set active patient from pat search widgets
#
# Revision 1.7  2009/04/16 12:47:28  ncq
# - some cleanup
#
# Revision 1.6  2009/04/14 18:35:52  shilbert
# - cleanup
#
# Revision 1.5  2009/04/13 19:10:06  shilbert
# -
#
# Revision 1.4  2009/04/13 19:06:25  ncq
# - add missing )
#
# Revision 1.3  2009/04/13 18:37:14  shilbert
# - updated class/filename
#
# Revision 1.2  2009/04/13 18:22:08  ncq
# - a tiny bit of cleanup
#
#