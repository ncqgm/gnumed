"""GNUmed data pack related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# stdlib
import logging
import sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmI18N

from Gnumed.business import gmSurgery
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmRegetMixin


_log = logging.getLogger('gm.ui')
#============================================================
# waiting list widgets
#============================================================
class cWaitingZonePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_FixedList(aSeq = [])
		mp.setThresholds(1, 2, 2)
		self.matcher = mp
		self.selection_only = False

	#--------------------------------------------------------
	def update_matcher(self, items):
		self.matcher.set_items([ {'data': i, 'list_label': i, 'field_label': i, 'weight': 1} for i in items ])

#============================================================
from Gnumed.wxGladeWidgets import wxgWaitingListEntryEditAreaPnl

class cWaitingListEntryEditAreaPnl(wxgWaitingListEntryEditAreaPnl.wxgWaitingListEntryEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__ (self, *args, **kwargs):

		try:
			self.patient = kwargs['patient']
			del kwargs['patient']
		except KeyError:
			self.patient = None

		try:
			data = kwargs['entry']
			del kwargs['entry']
		except KeyError:
			data = None

		wxgWaitingListEntryEditAreaPnl.wxgWaitingListEntryEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		if data is None:
			self.mode = 'new'
		else:
			self.data = data
			self.mode = 'edit'

		praxis = gmSurgery.gmCurrentPractice()
		pats = praxis.waiting_list_patients
		zones = {}
		zones.update([ [p['waiting_zone'], None] for p in pats if p['waiting_zone'] is not None ])
		self._PRW_zone.update_matcher(items = zones.keys())
	#--------------------------------------------------------
	# edit area mixin API
	#--------------------------------------------------------
	def _refresh_as_new(self):
		if self.patient is None:
			self._PRW_patient.person = None
			self._PRW_patient.Enable(True)
			self._PRW_patient.SetFocus()
		else:
			self._PRW_patient.person = self.patient
			self._PRW_patient.Enable(False)
			self._TCTRL_comment.SetFocus()
		self._PRW_patient._display_name()

		self._TCTRL_comment.SetValue(u'')
		self._PRW_zone.SetValue(u'')
		self._SPCTRL_urgency.SetValue(0)
	#--------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_patient.person = gmPerson.cIdentity(aPK_obj = self.data['pk_identity'])
		self._PRW_patient.Enable(False)
		self._PRW_patient._display_name()

		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))
		self._PRW_zone.SetValue(gmTools.coalesce(self.data['waiting_zone'], u''))
		self._SPCTRL_urgency.SetValue(self.data['urgency'])

		self._TCTRL_comment.SetFocus()
	#--------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		self.display_tctrl_as_valid(tctrl = self._PRW_patient, valid = (self._PRW_patient.person is not None))
		validity = (self._PRW_patient.person is not None)

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add to waiting list. Missing essential input.'))

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		# FIXME: filter out dupes
		self._PRW_patient.person.put_on_waiting_list (
			urgency = self._SPCTRL_urgency.GetValue(),
			comment = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u''),
			zone = gmTools.none_if(self._PRW_zone.GetValue().strip(), u'')
		)
		# dummy:
		self.data = {'pk_identity': self._PRW_patient.person.ID, 'comment': None, 'waiting_zone': None, 'urgency': 0}
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		gmSurgery.gmCurrentPractice().update_in_waiting_list (
			pk = self.data['pk_waiting_list'],
			urgency = self._SPCTRL_urgency.GetValue(),
			comment = self._TCTRL_comment.GetValue().strip(),
			zone = self._PRW_zone.GetValue().strip()
		)
		return True
#============================================================
from Gnumed.wxGladeWidgets import wxgWaitingListPnl

class cWaitingListPnl(wxgWaitingListPnl.wxgWaitingListPnl, gmRegetMixin.cRegetOnPaintMixin):

	def __init__ (self, *args, **kwargs):

		wxgWaitingListPnl.wxgWaitingListPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__current_zone = None

		self.__init_ui()
		self.__register_events()
	#--------------------------------------------------------
	# interal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_patients.set_columns ([
			_('Zone'),
			_('Urgency'),
			#' ! ',
			_('Waiting time'),
			_('Patient'),
			_('Born'),
			_('Comment')
		])
		self._LCTRL_patients.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE_USEHEADER, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_patients.item_tooltip_callback = self._on_get_list_tooltip
		self._PRW_zone.add_callback_on_selection(callback = self._on_zone_selected)
		self._PRW_zone.add_callback_on_lose_focus(callback = self._on_zone_selected)
	#--------------------------------------------------------
	def _on_get_list_tooltip(self, entry):

		dob = gmTools.coalesce (
				gmTools.coalesce (
					entry['dob'],
					u'',
					function_initial = ('strftime', '%d %b %Y')
				),
				u'',
				u' (%s)',
				function_initial = ('decode', gmI18N.get_encoding())
		)

		tt = _(
			'%s patients are waiting.\n'
			'\n'
			'Doubleclick to activate (entry will stay in list).'
		) % self._LCTRL_patients.GetItemCount()

		tt += _(
			'\n'
			'%s\n'
			'Patient: %s%s\n'
			'%s'
			'Urgency: %s\n'
			'Time: %s\n'
			'%s'
		) % (
			gmTools.u_box_horiz_single * 50,
			u'%s, %s (%s)' % (entry['lastnames'], entry['firstnames'], entry['l10n_gender']),
			dob,
			gmTools.coalesce(entry['waiting_zone'], u'', _('Zone: %s\n')),
			entry['urgency'],
			entry['waiting_time_formatted'].replace(u'00 ', u'', 1).replace('00:', u'').lstrip('0'),
			gmTools.coalesce(entry['comment'], u'', u'\n%s')
		)

		return tt
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = u'waiting_list_generic_mod_db', receiver = self._on_waiting_list_modified)
	#--------------------------------------------------------
	def __refresh_waiting_list(self):

		praxis = gmSurgery.gmCurrentPractice()
		pats = praxis.waiting_list_patients

		# set matcher to all zones currently in use
		zones = {}
		zones.update([ [p['waiting_zone'], None] for p in pats if p['waiting_zone'] is not None ])
		self._PRW_zone.update_matcher(items = zones.keys())
		del zones

		# filter patient list by zone and set waiting list
		self.__current_zone = self._PRW_zone.GetValue().strip()
		if self.__current_zone == u'':
			pats = [ p for p in pats ]
		else:
			pats = [ p for p in pats if p['waiting_zone'] == self.__current_zone ]

		self._LCTRL_patients.set_string_items (
			[ [
				gmTools.coalesce(p['waiting_zone'], u''),
				p['urgency'],
				p['waiting_time_formatted'].replace(u'00 ', u'', 1).replace('00:', u'').lstrip('0'),
				u'%s, %s (%s)' % (p['lastnames'], p['firstnames'], p['l10n_gender']),
				gmTools.coalesce (
					gmTools.coalesce (
						p['dob'],
						u'',
						function_initial = ('strftime', '%d %b %Y')
					),
					u'',
					function_initial = ('decode', gmI18N.get_encoding())
				),
				gmTools.coalesce(p['comment'], u'').split('\n')[0]
			  ] for p in pats
			]
		)
		self._LCTRL_patients.set_column_widths()
		self._LCTRL_patients.set_data(pats)
		self._LCTRL_patients.Refresh()
#		self._LCTRL_patients.SetToolTipString ( _(
#			'%s patients are waiting.\n'
#			'\n'
#			'Doubleclick to activate (entry will stay in list).'
#		) % len(pats))

		self._LBL_no_of_patients.SetLabel(_('(%s patients)') % len(pats))

		if len(pats) == 0:
			self._BTN_activate.Enable(False)
			self._BTN_activateplus.Enable(False)
			self._BTN_remove.Enable(False)
			self._BTN_edit.Enable(False)
			self._BTN_up.Enable(False)
			self._BTN_down.Enable(False)
		else:
			self._BTN_activate.Enable(True)
			self._BTN_activateplus.Enable(True)
			self._BTN_remove.Enable(True)
			self._BTN_edit.Enable(True)
		if len(pats) > 1:
			self._BTN_up.Enable(True)
			self._BTN_down.Enable(True)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_zone_selected(self, zone=None):
		if self.__current_zone == self._PRW_zone.GetValue().strip():
			return True
		wx.CallAfter(self.__refresh_waiting_list)
		return True
	#--------------------------------------------------------
	def _on_waiting_list_modified(self, *args, **kwargs):
		wx.CallAfter(self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_list_item_activated(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		pat = gmPerson.cIdentity(aPK_obj = item['pk_identity'])
		wx.CallAfter(set_active_patient, patient = pat)
	#--------------------------------------------------------
	def _on_activate_button_pressed(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		pat = gmPerson.cIdentity(aPK_obj = item['pk_identity'])
		wx.CallAfter(set_active_patient, patient = pat)
	#--------------------------------------------------------
	def _on_activateplus_button_pressed(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		pat = gmPerson.cIdentity(aPK_obj = item['pk_identity'])
		gmSurgery.gmCurrentPractice().remove_from_waiting_list(pk = item['pk_waiting_list'])
		wx.CallAfter(set_active_patient, patient = pat)
	#--------------------------------------------------------
	def _on_add_patient_button_pressed(self, evt):

		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add waiting list entry: No patient selected.'), beep = True)
			return

		ea = cWaitingListEntryEditAreaPnl(self, -1, patient = curr_pat)
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.ShowModal()
		dlg.Destroy()
	#--------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		ea = cWaitingListEntryEditAreaPnl(self, -1, entry = item)
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.ShowModal()
		dlg.Destroy()
	#--------------------------------------------------------
	def _on_remove_button_pressed(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		gmSurgery.gmCurrentPractice().remove_from_waiting_list(pk = item['pk_waiting_list'])
	#--------------------------------------------------------
	def _on_up_button_pressed(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		gmSurgery.gmCurrentPractice().raise_in_waiting_list(current_position = item['list_position'])
	#--------------------------------------------------------
	def _on_down_button_pressed(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		gmSurgery.gmCurrentPractice().lower_in_waiting_list(current_position = item['list_position'])
	#--------------------------------------------------------
	# edit
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_waiting_list()
		return True
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
#	def test_generic_codes_prw():
#		gmPG2.get_connection()
#		app = wx.PyWidgetTester(size = (500, 40))
#		pw = cGenericCodesPhraseWheel(app.frame, -1)
#		#pw.set_context(context = u'zip', val = u'04318')
#		app.frame.Show(True)
#		app.MainLoop()
#	#--------------------------------------------------------
#	test_generic_codes_prw()

	app = wx.PyWidgetTester(size = (200, 40))
	app.SetWidget(cWaitingListPnl, -1)
	app.MainLoop()

#================================================================
