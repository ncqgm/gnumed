"""GNUmed procedure widgets"""
#================================================================
__author__ = "cfmoro1976@yahoo.es, karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

# stdlib
import sys
import logging


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPerformedProcedure
from Gnumed.business import gmPerson
from Gnumed.business import gmHospitalStay

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmOrganizationWidgets
from Gnumed.wxpython import gmHospitalStayWidgets


_log = logging.getLogger('gm.ui')

#================================================================
# performed procedure related widgets/functions
#----------------------------------------------------------------
def manage_performed_procedures(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------------
	def get_tooltip(procedure=None):
		if procedure is None:
			return None
		return '\n'.join(procedure.format_maximum_information(left_margin = 1))

	#-----------------------------------------
	def edit(procedure=None):
		return edit_procedure(parent = parent, procedure = procedure)

	#-----------------------------------------
	def delete(procedure=None):
		if gmPerformedProcedure.delete_performed_procedure(procedure = procedure['pk_procedure']):
			return True

		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete performed procedure.'),
			beep = True
		)
		return False

	#-----------------------------------------
	def refresh(lctrl):
		procs = emr.get_performed_procedures()
		items = [
			[
				'%s%s' % (
					p['clin_when'].strftime('%Y-%m-%d'),
					gmTools.bool2subst (
						p['is_ongoing'],
						_(' (ongoing)'),
						gmTools.coalesce (
							value2test = p['clin_end'],
							return_instead = '',
							template4value = ' - %s',
							function4value = ('strftime', '%Y-%m-%d')
						)
					)
				),
				p['performed_procedure'],
				'%s @ %s' % (p['unit'], p['organization']),
				p['episode']
			] for p in procs
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = procs)

	#-----------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the procedure you want to edit !\n'),
		caption = _('Editing performed procedures ...'),
		columns = [_('When'), _('Procedure'), _('Where'), _('Episode')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
	)

#----------------------------------------------------------------
def edit_procedure(parent=None, procedure=None, single_entry=True):
	ea = cProcedureEAPnl(parent, -1)
	ea.data = procedure
	ea.mode = gmTools.coalesce(procedure, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(procedure, _('Adding a procedure'), _('Editing a procedure')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgProcedureEAPnl

class cProcedureEAPnl(wxgProcedureEAPnl.wxgProcedureEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		wxgProcedureEAPnl.wxgProcedureEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = None

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_hospital_stay.add_callback_on_lose_focus(callback = self._on_hospital_stay_lost_focus)
		self._PRW_hospital_stay.set_context(context = 'pat', val = gmPerson.gmCurrentPatient().ID)
		self._PRW_location.add_callback_on_lose_focus(callback = self._on_location_lost_focus)
		self._DPRW_date.add_callback_on_lose_focus(callback = self._on_start_lost_focus)
		self._DPRW_end.add_callback_on_lose_focus(callback = self._on_end_lost_focus)

		# procedure
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
"""
select distinct on (narrative) narrative, narrative
from clin.procedure
where narrative %(fragment_condition)s
order by narrative
limit 25
"""			]
		)
		mp.setThresholds(2, 4, 6)
		self._PRW_procedure.matcher = mp

	#----------------------------------------------------------------
	def _on_hospital_stay_lost_focus(self):
		stay = self._PRW_hospital_stay.GetData()
		if stay is None:
			self._PRW_hospital_stay.SetText()
			self._PRW_location.Enable(True)
			self._PRW_episode.Enable(True)
			self._LBL_hospital_details.SetLabel('')
		else:
			self._PRW_location.SetText()
			self._PRW_location.Enable(False)
			self._PRW_episode.SetText()
			self._PRW_episode.Enable(False)
			self._LBL_hospital_details.SetLabel(gmHospitalStay.cHospitalStay(aPK_obj = stay).format())

	#----------------------------------------------------------------
	def _on_location_lost_focus(self):
		loc = self._PRW_location.GetData()
		if loc is None:
			self._PRW_hospital_stay.Enable(True)
			self._PRW_episode.Enable(False)
		else:
			self._PRW_hospital_stay.SetText()
			self._PRW_hospital_stay.Enable(False)
			self._PRW_episode.Enable(True)

	#----------------------------------------------------------------
	def _on_start_lost_focus(self):
		if not self._DPRW_date.is_valid_timestamp():
			return
		end = self._DPRW_end.GetData()
		if end is None:
			return
		end = end.get_pydt()
		start = self._DPRW_date.GetData().get_pydt()
		if start < end:
			return
		self._DPRW_date.display_as_valid(False)

	#----------------------------------------------------------------
	def _on_end_lost_focus(self):
		end = self._DPRW_end.GetData()
		if end is None:
			self._CHBOX_ongoing.Enable(True)
			self._DPRW_end.display_as_valid(True)
		else:
			self._CHBOX_ongoing.Enable(False)
			end = end.get_pydt()
			now = gmDateTime.pydt_now_here()
			if end > now:
				self._CHBOX_ongoing.SetValue(True)
			else:
				self._CHBOX_ongoing.SetValue(False)
			start = self._DPRW_date.GetData()
			if start is None:
				self._DPRW_end.display_as_valid(True)
			else:
				start = start.get_pydt()
				if end > start:
					self._DPRW_end.display_as_valid(True)
				else:
					self._DPRW_end.display_as_valid(False)

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False

		if not self._DPRW_date.is_valid_timestamp():
			self._DPRW_date.display_as_valid(False)
			has_errors = True
		else:
			self._DPRW_date.display_as_valid(True)

		start = self._DPRW_date.GetData()
		end = self._DPRW_end.GetData()
		self._DPRW_end.display_as_valid(True)
		if end is not None:
			end = end.get_pydt()
			if start is not None:
				start = start.get_pydt()
				if end < start:
					has_errors = True
					self._DPRW_end.display_as_valid(False)
			if self._CHBOX_ongoing.IsChecked():
				now = gmDateTime.pydt_now_here()
				if end < now:
					has_errors = True
					self._DPRW_end.display_as_valid(False)

		if self._PRW_hospital_stay.GetData() is None:
			if self._PRW_episode.GetValue().strip() == '':
				self._PRW_episode.display_as_valid(False)
				has_errors = True
			else:
				self._PRW_episode.display_as_valid(True)
		else:
			self._PRW_episode.display_as_valid(True)

		if (self._PRW_procedure.GetValue() is None) or (self._PRW_procedure.GetValue().strip() == ''):
			self._PRW_procedure.display_as_valid(False)
			has_errors = True
		else:
			self._PRW_procedure.display_as_valid(True)

		invalid_location = (
			(self._PRW_hospital_stay.GetData() is None) and (self._PRW_location.GetData() is None)
				or
			(self._PRW_hospital_stay.GetData() is not None) and (self._PRW_location.GetData() is not None)
		)
		if invalid_location:
			self._PRW_hospital_stay.display_as_valid(False)
			self._PRW_location.display_as_valid(False)
			has_errors = True
		else:
			self._PRW_hospital_stay.display_as_valid(True)
			self._PRW_location.display_as_valid(True)

		if has_errors:
			self.StatusText = _('Cannot save procedure.')
		return (has_errors is False)

	#----------------------------------------------------------------
	def _save_as_new(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr

		stay = self._PRW_hospital_stay.GetData()
		if stay is None:
			epi = self._PRW_episode.GetData(can_create = True)
		else:
			epi = gmHospitalStay.cHospitalStay(aPK_obj = stay)['pk_episode']

		proc = emr.add_performed_procedure (
			episode = epi,
			location = self._PRW_location.GetData(),
			hospital_stay = stay,
			procedure = self._PRW_procedure.GetValue().strip()
		)

		proc['clin_when'] = self._DPRW_date.GetData().get_pydt()
		if self._DPRW_end.GetData() is None:
			proc['clin_end'] = None
		else:
			proc['clin_end'] = self._DPRW_end.GetData().get_pydt()
		proc['is_ongoing'] = self._CHBOX_ongoing.IsChecked()
		proc['comment'] = self._TCTRL_comment.GetValue()
		proc['pk_doc'] = self._PRW_document.GetData()
		proc.save()

		proc.generic_codes = [ c['data'] for c in self._PRW_codes.GetData() ]

		self.data = proc

		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['clin_when'] = self._DPRW_date.GetData().get_pydt()
		self.data['is_ongoing'] = self._CHBOX_ongoing.IsChecked()
		self.data['pk_org_unit'] = self._PRW_location.GetData()
		self.data['pk_hospital_stay'] = self._PRW_hospital_stay.GetData()
		self.data['performed_procedure'] = self._PRW_procedure.GetValue().strip()
		self.data['comment'] = self._TCTRL_comment.GetValue()
		self.data['pk_doc'] = self._PRW_document.GetData()
		if self._DPRW_end.GetData() is None:
			self.data['clin_end'] = None
		else:
			self.data['clin_end'] = self._DPRW_end.GetData().get_pydt()
		if self.data['pk_hospital_stay'] is None:
			self.data['pk_episode'] = self._PRW_episode.GetData()
		else:
			self.data['pk_episode'] = gmHospitalStay.cHospitalStay(aPK_obj = self._PRW_hospital_stay.GetData())['pk_episode']
		self.data.save()

		self.data.generic_codes = [ c['data'] for c in self._PRW_codes.GetData() ]

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._DPRW_date.SetText()
		self._DPRW_end.SetText()
		self._CHBOX_ongoing.SetValue(False)
		self._CHBOX_ongoing.Enable(True)
		self._PRW_hospital_stay.SetText()
		self._LBL_hospital_details.SetLabel('')
		self._PRW_location.SetText()
		self._PRW_episode.SetText()
		self._PRW_procedure.SetText()
		self._PRW_codes.SetText()
		self._PRW_document.SetText()
		self._TCTRL_comment.SetValue('')

		self._PRW_procedure.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._DPRW_date.SetData(data = self.data['clin_when'])
		if self.data['clin_end'] is None:
			self._DPRW_end.SetText()
			self._CHBOX_ongoing.Enable(True)
			self._CHBOX_ongoing.SetValue(self.data['is_ongoing'])
		else:
			self._DPRW_end.SetData(data = self.data['clin_end'])
			self._CHBOX_ongoing.Enable(False)
			now = gmDateTime.pydt_now_here()
			if self.data['clin_end'] > now:
				self._CHBOX_ongoing.SetValue(True)
			else:
				self._CHBOX_ongoing.SetValue(False)
		self._PRW_episode.SetText(value = self.data['episode'], data = self.data['pk_episode'])
		self._PRW_procedure.SetText(value = self.data['performed_procedure'], data = self.data['performed_procedure'])
		self._PRW_document.SetData(self.data['pk_doc'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))

		if self.data['pk_hospital_stay'] is None:
			self._PRW_hospital_stay.SetText()
			self._PRW_hospital_stay.Enable(False)
			self._LBL_hospital_details.SetLabel('')
			self._PRW_location.SetText(value = '%s @ %s' % (self.data['unit'], self.data['organization']), data = self.data['pk_org_unit'])
			self._PRW_location.Enable(True)
			self._PRW_episode.Enable(True)
		else:
			self._PRW_hospital_stay.SetText(value = '%s @ %s' % (self.data['unit'], self.data['organization']), data = self.data['pk_hospital_stay'])
			self._PRW_hospital_stay.Enable(True)
			self._LBL_hospital_details.SetLabel(gmHospitalStay.cHospitalStay(aPK_obj = self.data['pk_hospital_stay']).format())
			self._PRW_location.SetText()
			self._PRW_location.Enable(False)
			self._PRW_episode.Enable(False)

		val, data = self._PRW_codes.generic_linked_codes2item_dict(self.data.generic_codes)
		self._PRW_codes.SetText(val, data)

		self._PRW_procedure.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

		self._PRW_episode.SetText(value = self.data['episode'], data = self.data['pk_episode'])

		if self.data['pk_hospital_stay'] is None:
			self._PRW_hospital_stay.SetText()
			self._PRW_hospital_stay.Enable(False)
			self._LBL_hospital_details.SetLabel('')
			self._PRW_location.SetText(value = '%s @ %s' % (self.data['unit'], self.data['organization']), data = self.data['pk_org_unit'])
			self._PRW_location.Enable(True)
			self._PRW_episode.Enable(True)
		else:
			self._PRW_hospital_stay.SetText(value = '%s @ %s' % (self.data['unit'], self.data['organization']), data = self.data['pk_hospital_stay'])
			self._PRW_hospital_stay.Enable(True)
			self._LBL_hospital_details.SetLabel(gmHospitalStay.cHospitalStay(aPK_obj = self.data['pk_hospital_stay']).format())
			self._PRW_location.SetText()
			self._PRW_location.Enable(False)
			self._PRW_episode.Enable(False)

		self._PRW_procedure.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_add_hospital_stay_button_pressed(self, evt):
		# FIXME: this would benefit from setting the created stay
		gmHospitalStayWidgets.edit_hospital_stay(parent = self.GetParent())
		evt.Skip()

	#----------------------------------------------------------------
	def _on_add_location_button_pressed(self, event):
		gmOrganizationWidgets.manage_orgs(parent = self)	#self.GetParent())
		event.Skip()

	#----------------------------------------------------------------
	def _on_ongoing_checkbox_checked(self, event):
		if self._CHBOX_ongoing.IsChecked():
			end = self._DPRW_end.GetData()
			if end is None:
				self._DPRW_end.display_as_valid(True)
			else:
				end = end.get_pydt()
				now = gmDateTime.pydt_now_here()
				if end > now:
					self._DPRW_end.display_as_valid(True)
				else:
					self._DPRW_end.display_as_valid(False)
		else:
			self._DPRW_end.is_valid_timestamp()
		event.Skip()


#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmPatSearchWidgets

	#----------------------------------------------------------------
#	def test_edit_procedure()
#		app = wx.PyWidgetTester(size = (200, 300))
#		edit_procedure(parent=app.frame)

	#================================================================
	# obtain patient
	pat = gmPersonSearch.ask_for_patient()
	if pat is None:
		print("No patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=pat)

#	test_edit_procedure()
