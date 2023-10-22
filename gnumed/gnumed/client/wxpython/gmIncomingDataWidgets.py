# -*- coding: utf-8 -*-
"""GNUmed incoming data widgets."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmWorkerThread
from Gnumed.business import gmIncomingData
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.auto-in-ui')

#============================================================
class cIncomingDataListCtrl(gmListWidgets.cReportListCtrl):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if not self.EnableCheckBoxes(enable = True):
			_log.error('cannot enable list item checkboxes')
		self.set_columns(columns = [_('Item'), _('Patient')])
		self.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self.set_resize_column()

	#--------------------------------------------------------
	def repopulate(self, pk_patient=None) -> bool:
		list_rows = []
		data = []
		items = gmIncomingData.get_incoming_data()
		if pk_patient:
			items = [ i for i in items if i['pk_identity_disambiguated'] == pk_patient ]
		for i in items:
			if not i['comment']:
				continue
			parts = i['comment'].split('auto-import/', 1)
			if len(parts) == 1:
				comment = i['comment']
			else:
				if parts[1].strip():
					comment = parts[1].strip()
				else:
					comment = parts[0].strip()
			if not comment:
				continue
			pat = self._get_patient_column_value(i)
			list_rows.append([comment, pat])
			data.append(i)
		self.set_string_items(items = list_rows)
		self.set_data(data = data)
		self.set_column_widths()
		return True

	#--------------------------------------------------------
	def view_items_externally(self):
		if self.ItemCount == 0:
			return

		# only one page, show that, regardless of whether selected or not
		if self.ItemCount == 1:
			page_fname = self.get_item_data(0).save_to_file()
			(success, msg) = gmMimeLib.call_viewer_on_file(page_fname)
			if success:
				return

			gmGuiHelpers.gm_show_warning (
				aMessage = _('Cannot display item:\n%s') % msg,
				aTitle = _('displaying incoming item')
			)
			return

		items = self.selected_item_data
		if not items:
			return

		# did user select one of multiple pages ?
		page_fnames = [ i.save_to_file() for i in items ]
		if len(page_fnames) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Nothing selected for viewing.'), beep = True)
			return

		for page_fname in page_fnames:
			(success, msg) = gmMimeLib.call_viewer_on_file(page_fname)
			if not success:
				gmGuiHelpers.gm_show_warning (
					aMessage = _('Cannot display item:\n%s') % msg,
					aTitle = _('displaying incoming item')
				)

	#--------------------------------------------------------
	def _get_patient_column_value(self, item) -> str:
		if not item['pk_identity_disambiguated']:
			return ''

		return gmPerson.cPatient(item['pk_identity_disambiguated']).description_gender

#============================================================
class cCurrentPatientIncomingDataListCtrl(cIncomingDataListCtrl):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.set_resize_column(0)

	#--------------------------------------------------------
	def repopulate(self, pk_patient=None) -> bool:
		return super().repopulate(pk_patient = gmPerson.gmCurrentPatient().ID)

	#--------------------------------------------------------
	def _get_patient_column_value(self, item) -> str:
		return _('current')

#============================================================
from Gnumed.wxGladeWidgets import wxgIncomingPluginPnl

class cIncomingPluginPnl(wxgIncomingPluginPnl.wxgIncomingPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of items for assigning to a patient.

	Used as notebook page.
	"""
	def __init__(self, *args, **kwargs):
		wxgIncomingPluginPnl.wxgIncomingPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_table_mod)

	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.incoming_data_unmatched':
			return

		self._schedule_data_reget()

	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.select_callback = self.__on_item_selected

	#--------------------------------------------------------
	# reget-on-paint mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		return self._LCTRL_items.repopulate()

	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def __on_item_selected(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		self._PNL_previews.filename = item.save_to_file()

	#--------------------------------------------------------
#	def _on_toggle_item_checkbox_button_pressed(self, event):
#		event.Skip()
#		item_idx = self._LCTRL_items.get_selected_items(only_one = True)
#		if item_idx in [None, -1]:
#			return
#
#		self._LCTRL_items.CheckItem(item_idx, check = not self._LCTRL_items.IsItemChecked(item_idx))

	#--------------------------------------------------------
	def _on_remove_item_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		do_delete = gmGuiHelpers.gm_show_question (
			question = _('Irrevocably delete the selected item ?'),
			title = _('Deleting incoming data item')
		)
		if not do_delete:
			return

		gmIncomingData.delete_incoming_data(pk_incoming_data = item['pk_incoming_data_unmatched'])

	#--------------------------------------------------------
	def _on_assign_items2patient_button_pressed(self, event):
		event.Skip()
		pat = self._TCTRL_search_patient.person
		if pat is None:
			return

		for incoming_item in self._LCTRL_items.checked_items_data:
			incoming_item.patient = pat

	#--------------------------------------------------------
	def _on_unassign_patient_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		item.patient = None
		item.save()

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_plugin():
		wx.Log.EnableLogging(enable = False)
		gmGuiTest.test_widget(cIncomingPluginPnl, patient = 12)

	#--------------------------------------------------------
	test_plugin()
