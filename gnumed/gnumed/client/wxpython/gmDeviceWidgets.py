"""GNUmed device management widgets.
"""
#================================================================
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL"

import sys
import logging
from lxml import etree

#import wx	#, wx.grid

if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.business import gmPerson
from Gnumed.business import gmDevices
from Gnumed.business import gmDocuments
from Gnumed.business import gmPersonSearch
from Gnumed.pycommon import gmDispatcher
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxGladeWidgets import wxgCardiacDevicePluginPnl


_log = logging.getLogger('gm.ui')
#================================================================
class cCardiacDevicePluginPnl(wxgCardiacDevicePluginPnl.wxgCardiacDevicePluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of widgets to manage implanted cardiac devices. Used as notebook page."""
	def __init__(self, *args, **kwargs):
		wxgCardiacDevicePluginPnl.wxgCardiacDevicePluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		# check if report types exist in db, if not create them
		self.__checkup_doc_type = 'cardiac device checkup report'
		dtype = gmDocuments.create_document_type(self.__checkup_doc_type)
		# cannot reuse self.__checkup_doc_type here or else it wouldn't get translated
		dtype.set_translation(_('cardiac device checkup report'))

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
			xml_fname = checkups[-1].parts[0].save_to_file()
			tree = etree.parse(xml_fname)
			DevicesDisplayed = gmDevices.device_status_as_text(tree)
			text = ''.join(DevicesDisplayed)

		self._TCTRL_current_status.SetValue(text)

		return True
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmDateTime, gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#------------------------------------------------------------
	def test_grid():
		gmPersonSearch.ask_for_patient()
#		app = wx.PyWidgetTester(size = (500, 300))
#		lab_grid = cMeasurementsGrid(app.frame, -1)
#		lab_grid.patient = pat
#		app.frame.Show()
#		app.MainLoop()
	#------------------------------------------------------------
	def test_test_ea_pnl():
		pat = gmPersonSearch.ask_for_patient()
		gmPatSearchWidgets.set_active_patient(patient=pat)
#		app = wx.PyWidgetTester(size = (500, 300))
#		ea = cMeasurementEditAreaPnl(app.frame, -1)
#		app.frame.Show()
#		app.MainLoop()
	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		#test_grid()
		test_test_ea_pnl()

#================================================================
#