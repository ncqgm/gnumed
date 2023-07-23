"""GNUmed waiting list widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# stdlib
import logging
import sys


# 3rd party
import wx

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPraxis
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmGuiHelpers


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
def edit_waiting_list_entry(parent=None, entry=None, patient=None):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	ea = cWaitingListEntryEditAreaPnl(parent, -1, patient = gmTools.bool2subst((entry is None), patient, None))
	ea.data = entry
	ea.mode = gmTools.coalesce(entry, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(gmTools.coalesce(entry, _('Adding new waiting list entry'), _('Editing waiting list entry')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

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

		praxis = gmPraxis.gmCurrentPraxisBranch()
		pats = praxis.waiting_list_patients
		zones = {}
		zones.update([ [p['waiting_zone'], None] for p in pats if p['waiting_zone'] is not None ])
		self._PRW_zone.update_matcher(items = list(zones))

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

		self._TCTRL_comment.SetValue('')
		self._PRW_zone.SetValue('')
		self._SPCTRL_urgency.SetValue(0)
	#--------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_patient.person = gmPerson.cPerson(aPK_obj = self.data['pk_identity'])
		self._PRW_patient.Enable(False)
		self._PRW_patient._display_name()

		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self._PRW_zone.SetValue(gmTools.coalesce(self.data['waiting_zone'], ''))
		self._SPCTRL_urgency.SetValue(self.data['urgency'])

		self._TCTRL_comment.SetFocus()
	#--------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		self.display_tctrl_as_valid(tctrl = self._PRW_patient, valid = (self._PRW_patient.person is not None))
		validity = (self._PRW_patient.person is not None)

		if validity is False:
			self.StatusText = _('Cannot add to waiting list. Missing essential input.')

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		# FIXME: filter out dupes ?
		self._PRW_patient.person.put_on_waiting_list (
			urgency = self._SPCTRL_urgency.GetValue(),
			comment = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), ''),
			zone = gmTools.none_if(self._PRW_zone.GetValue().strip(), '')
		)
		# dummy:
		self.data = {'pk_identity': self._PRW_patient.person.ID, 'comment': None, 'waiting_zone': None, 'urgency': 0}
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		gmPraxis.gmCurrentPraxisBranch().update_in_waiting_list (
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
		self.__id_most_recently_activated_patient = None
		self.__comment_most_recently_activated_patient = None

		self.__init_ui()
		self.__register_events()
	#--------------------------------------------------------
	# interal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_patients.set_columns ([
			_('Zone'),
			_('Urgency'),
			_('Registered'),
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
	def _check_RFE(self):
		"""
		This gets called when a patient has been activated, but
		only when the waiting list is actually in use (that is,
		the plugin is loaded)
		"""
		pat = gmPerson.gmCurrentPatient()
		enc = pat.emr.active_encounter
		if gmTools.coalesce(enc['reason_for_encounter'], '').strip() != '':
			return
		entries = pat.waiting_list_entries
		if len(entries) == 0:
			if self.__id_most_recently_activated_patient is None:
				return
			if self.__id_most_recently_activated_patient != pat.ID:
				return
			rfe = self.__comment_most_recently_activated_patient
		else:
			entry = entries[0]
			if gmTools.coalesce(entry['comment'], '').strip() == '':
				return
			rfe = entry['comment'].strip()
		enc['reason_for_encounter'] = rfe
		enc.save()
		self.__id_most_recently_activated_patient = None
	#--------------------------------------------------------
	def _on_get_list_tooltip(self, entry):

		dob = gmTools.coalesce (
			gmTools.coalesce(entry['dob'], '', function4value = ('strftime', '%d %b %Y')),
			'',
			' (%s)'
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
			'%s, %s (%s)' % (entry['lastnames'], entry['firstnames'], entry['l10n_gender']),
			dob,
			gmTools.coalesce(entry['waiting_zone'], '', _('Zone: %s\n')),
			entry['urgency'],
			gmDateTime.format_interval_medically(entry['waiting_time']),
			gmTools.coalesce(entry['comment'], '', '\n%s')
		)

		return tt
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'clin.waiting_list_mod_db', receiver = self._on_waiting_list_modified)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def __refresh_waiting_list(self):
		self.__id_most_recently_activated_patient = None
		col, ascending = self._LCTRL_patients.GetSortState()	# preserve sorting order

		praxis = gmPraxis.gmCurrentPraxisBranch()
		pats = praxis.waiting_list_patients

		# set matcher to all zones currently in use
		zones = {}
		zones.update([ [p['waiting_zone'], None] for p in pats if p['waiting_zone'] is not None ])
		self._PRW_zone.update_matcher(items = list(zones))

		# filter patient list by zone and set waiting list
		self.__current_zone = self._PRW_zone.GetValue().strip()
		if self.__current_zone == '':
			pats = [ p for p in pats ]
		else:
			pats = [ p for p in pats if p['waiting_zone'] == self.__current_zone ]

		# filter by "active patient only"
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			if self._CHBOX_active_patient_only.IsChecked():
				pats = [ p for p in pats if p['pk_identity'] == curr_pat.ID ]

		old_pks = [ d['pk_waiting_list'] for d in self._LCTRL_patients.get_selected_item_data() ]
		self._LCTRL_patients.set_string_items (
			[ [
				gmTools.coalesce(p['waiting_zone'], ''),
				p['urgency'],
				gmDateTime.pydt_strftime(p['registered'], format='%Y %b %d %H:%M'),
				gmDateTime.format_interval_medically(p['waiting_time']),
				'%s, %s (%s)' % (p['lastnames'], p['firstnames'], p['l10n_gender']),
				gmTools.coalesce (
					gmTools.coalesce (p['dob'], '', function4value = ('strftime', '%d %b %Y')),
					''
				),
				gmTools.coalesce(p['comment'], '').split('\n')[0]
			] for p in pats ]
		)
		self._LCTRL_patients.set_column_widths()
		self._LCTRL_patients.set_data(pats)
		new_selections = []
		new_pks = [ p['pk_waiting_list'] for p in pats ]
		for old_pk in old_pks:
			if old_pk in new_pks:
				new_selections.append(new_pks.index(old_pk))
		self._LCTRL_patients.selections = new_selections
		self._LCTRL_patients.Refresh()
		self._LCTRL_patients.SortListItems(col, ascending) # re-sort

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
		self.__id_most_recently_activated_patient = None
		if self.__current_zone == self._PRW_zone.GetValue().strip():
			return True
		wx.CallAfter(self.__refresh_waiting_list)
		return True
	#--------------------------------------------------------
	def _on_waiting_list_modified(self, *args, **kwargs):
		self.__id_most_recently_activated_patient = None
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_post_patient_selection(self, *args, **kwargs):
		self._CHBOX_active_patient_only.Enable()
		self._check_RFE()
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_list_item_activated(self, evt):
		self.__id_most_recently_activated_patient = None
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		try:
			pat = gmPerson.cPerson(aPK_obj = item['pk_identity'])
		except gmExceptions.ConstructorError:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Waiting list'),
				aMessage = _('Cannot activate patient.\n\nIt has probably been disabled.')
			)
			return
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			if curr_pat.ID == item['pk_identity']:
				edit_waiting_list_entry(parent = self, entry = item)
				return
		wx.CallAfter(gmPatSearchWidgets.set_active_patient, patient = pat)
	#--------------------------------------------------------
	def _on_activate_button_pressed(self, evt):
		self.__id_most_recently_activated_patient = None
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		try:
			pat = gmPerson.cPerson(aPK_obj = item['pk_identity'])
		except gmExceptions.ConstructorError:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Waiting list'),
				aMessage = _('Cannot activate patient.\n\nIt has probably been disabled.')
			)
			return
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			if curr_pat.ID == item['pk_identity']:
				return
		wx.CallAfter(gmPatSearchWidgets.set_active_patient, patient = pat)
	#--------------------------------------------------------
	def _on_activateplus_button_pressed(self, evt):
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		try:
			pat = gmPerson.cPerson(aPK_obj = item['pk_identity'])
		except gmExceptions.ConstructorError:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Waiting list'),
				aMessage = _('Cannot activate patient.\n\nIt has probably been disabled.')
			)
			return
		self.__id_most_recently_activated_patient = item['pk_identity']
		self.__comment_most_recently_activated_patient = gmTools.coalesce(item['comment'], '').strip()
		gmPraxis.gmCurrentPraxisBranch().remove_from_waiting_list(pk = item['pk_waiting_list'])
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			if curr_pat.ID == item['pk_identity']:
				return
		wx.CallAfter(gmPatSearchWidgets.set_active_patient, patient = pat)
	#--------------------------------------------------------
	def _on_add_patient_button_pressed(self, evt):
		self.__id_most_recently_activated_patient = None
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add waiting list entry: No patient selected.'), beep = True)
			return
		edit_waiting_list_entry(parent = self, patient = curr_pat)
	#--------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		self.__id_most_recently_activated_patient = None
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		edit_waiting_list_entry(parent = self, entry = item)
	#--------------------------------------------------------
	def _on_remove_button_pressed(self, evt):
		self.__id_most_recently_activated_patient = None
		item = self._LCTRL_patients.get_selected_item_data(only_one = True)
		if item is None:
			return
		cmt = gmTools.coalesce(item['comment'], '').split('\n')[0].strip()[:40]
		if cmt != '':
			cmt += '\n'
		question = _(
			'Are you sure you want to remove\n'
			'\n'
			' %s, %s (%s)\n'
			' born: %s\n'
			' %s'
			'\n'
			'from the waiting list ?'
		) % (
			item['lastnames'],
			item['firstnames'],
			item['l10n_gender'],
			gmTools.coalesce (
				item['dob'],
				'',
				function4value = ('strftime', '%d %b %Y')
			),
			cmt
		)
		do_delete = gmGuiHelpers.gm_show_question (
			title = _('Delete waiting list entry'),
			question = question
		)
		if not do_delete:
			return
		gmPraxis.gmCurrentPraxisBranch().remove_from_waiting_list(pk = item['pk_waiting_list'])
	#--------------------------------------------------------
	def _on_up_button_pressed(self, evt):
		self.__id_most_recently_activated_patient = None
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		gmPraxis.gmCurrentPraxisBranch().raise_in_waiting_list(current_position = item['list_position'])
	#--------------------------------------------------------
	def _on_down_button_pressed(self, evt):
		self.__id_most_recently_activated_patient = None
		item = self._LCTRL_patients.get_selected_item_data(only_one=True)
		if item is None:
			return
		gmPraxis.gmCurrentPraxisBranch().lower_in_waiting_list(current_position = item['list_position'])
	#--------------------------------------------------------
	def _on_active_patient_only_checked(self, evt):
		self.__refresh_waiting_list()
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
