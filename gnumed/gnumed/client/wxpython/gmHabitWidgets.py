"""GNUmed habits widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools

from Gnumed.business import gmATC
from Gnumed.business import gmMedication

from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets

_log = logging.getLogger('gm.ui')

#================================================================
def edit_substance_abuse(parent=None, intake=None, patient=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cSubstanceAbuseEAPnl(parent, -1, intake = intake, patient = patient)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = (intake is not None))
	dlg.SetTitle(gmTools.coalesce(intake, _('Adding substance abuse'), _('Editing substance abuse')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def manage_substance_abuse(parent=None, patient=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

#	#------------------------------------------------------------
#	def add_from_db(substance):
#		drug_db = get_drug_database(parent = parent, patient = gmPerson.gmCurrentPatient())
#		if drug_db is None:
#			return False
#		drug_db.import_drugs()
#		return True
#	#------------------------------------------------------------
	def edit(intake=None):
		return edit_substance_abuse(parent = parent, intake = intake, patient = patient)

	#------------------------------------------------------------
	def delete(intake):
		return intake.delete()

	#------------------------------------------------------------
	def get_tooltip(intake=None):
		return intake.format(single_line = False)

	#------------------------------------------------------------
	def refresh(lctrl):
		intakes = patient.emr.abused_substances
		items = []
		for i in intakes:
			items.append ([
				i['substance'],
				i.use_type_string,
				i['last_checked_when'].strftime('%b %Y')
			])
		lctrl.set_string_items(items)
		lctrl.set_data(intakes)

	#------------------------------------------------------------
	if len(patient.emr.abused_substances) == 0:
		edit()

	msg = _('Substances abused by the patient:')

	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing abused substances.'),
		columns = [ _('Intake'), _('Status'), _('Last confirmed') ],
		single_selection = False,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
	)

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgSubstanceAbuseEAPnl

class cSubstanceAbuseEAPnl(wxgSubstanceAbuseEAPnl.wxgSubstanceAbuseEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		try:
			data = kwargs['intake']
			del kwargs['intake']
		except KeyError:
			data = None

		self.__patient = kwargs['patient']
		del kwargs['patient']

		if data is not None:
			if data['pk_patient'] != self.__patient.ID:
				_log.error('intake: %s', data)
				_log.error('patient: %s', self.__patient)
				raise ValueError('<intake> does not belong to <patient>')

		wxgSubstanceAbuseEAPnl.wxgSubstanceAbuseEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()

#	#----------------------------------------------------------------
#	def __init_ui(self):
#		if self.mode == 'new':
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if not self._DPRW_quit_when.is_valid_timestamp(empty_is_valid = True):
			validity = False
			self._DPRW_quit_when.SetFocus()

		if self._RBTN_other_substance.GetValue() is True:
			if self._PRW_substance.GetValue().strip() == '':
				validity = False
				self._PRW_substance.display_as_valid(valid = False)
				self._PRW_substance.SetFocus()
			else:
				self._PRW_substance.display_as_valid(valid = True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):

		if self._RBTN_tobacco.GetValue() is True:
			pk_substance = gmMedication.get_tobacco()['pk_substance']

		elif self._RBTN_c2.GetValue() is True:
			pk_substance = gmMedication.get_alcohol()['pk_substance']

		elif self._RBTN_other_substance.GetValue() is True:
			#xxxxxxxxx
			#PRW_substance -> _dose
			pk_substance = gmMedication.get_other_drug (
				name = self._PRW_substance.GetValue().strip(),
				pk_dose = self._PRW_substance.GetData()
			)['pk_substance']

		pk_encounter = self.__patient.emr.active_encounter['pk_encounter']
		intake = gmMedication.create_substance_intake (
			pk_encounter = pk_encounter,
			pk_episode = gmMedication.create_default_medication_history_episode(encounter = pk_encounter)['pk_episode'],
			pk_substance = pk_substance
		)

		if self._RBTN_nonharmful_use.GetValue() is True:
			intake['use_type'] = 0
		elif self._RBTN_harmful_use.GetValue() is True:
			intake['use_type'] = 1
		elif self._RBTN_presently_addicted.GetValue() is True:
			intake['use_type'] = 2
		elif self._RBTN_previously_addicted.GetValue() is True:
			intake['use_type'] = 3
		intake['notes'] = self._TCTRL_comment.GetValue().strip()
		if self._DPRW_quit_when.is_valid_timestamp(empty_is_valid = False):
			intake['discontinued'] = self._DPRW_quit_when.date
		intake.save()

		self.data = intake

		return True

	#----------------------------------------------------------------
	def _save_as_update(self):

		if self._RBTN_nonharmful_use.GetValue() is True:
			self.data['use_type'] = 0
		elif self._RBTN_harmful_use.GetValue() is True:
			self.data['use_type'] = 1
		elif self._RBTN_presently_addicted.GetValue() is True:
			self.data['use_type'] = 2
		elif self._RBTN_previously_addicted.GetValue() is True:
			self.data['use_type'] = 3
		self.data['notes'] = self._TCTRL_comment.GetValue().strip()
		if self._DPRW_quit_when.is_valid_timestamp(empty_is_valid = False):
			self.data['discontinued'] = self._DPRW_quit_when.date
		if self._CHBOX_confirm.GetValue() is True:
			self.data['pk_encounter'] = self.__patient.emr.active_encounter['pk_encounter']

		self.data.save()

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):

		self._RBTN_tobacco.SetValue(False)
		self._RBTN_c2.SetValue(False)
		self._RBTN_other_substance.SetValue(True)
		self._PRW_substance.SetText('', None)
		self._PRW_substance.Enable()
		self._RBTN_nonharmful_use.SetValue(True)
		self._RBTN_harmful_use.SetValue(False)
		self._RBTN_presently_addicted.SetValue(False)
		self._RBTN_previously_addicted.SetValue(False)
		self._TCTRL_comment.SetValue('')
		self._DPRW_quit_when.SetText('', None)
		self._LBL_confirm_date.SetLabel('<%s>' % _('today'))
		self._CHBOX_confirm.SetValue(True)
		self._CHBOX_confirm.Disable()

		if gmMedication.substance_intake_exists_by_atc(pk_identity = self.__patient.ID, atc = gmATC.ATC_NICOTINE):
			self._RBTN_tobacco.Disable()
		else:
			self._RBTN_tobacco.Enable()

		if gmMedication.substance_intake_exists_by_atc(pk_identity = self.__patient.ID, atc = gmATC.ATC_ETHANOL):
			self._RBTN_c2.Disable()
		else:
			self._RBTN_c2.Enable()

		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._RBTN_tobacco.Disable()
		self._RBTN_c2.Disable()
		self._RBTN_other_substance.Disable()
		self._PRW_substance.Disable()

		if self.data['atc_substance'] == gmATC.ATC_NICOTINE:
			self._RBTN_tobacco.SetValue(True)
			self._RBTN_c2.SetValue(False)
			self._RBTN_other_substance.SetValue(False)
			self._PRW_substance.SetText('', None)
		elif self.data['atc_substance'] == gmATC.ATC_ETHANOL:
			self._RBTN_tobacco.SetValue(False)
			self._RBTN_c2.SetValue(True)
			self._RBTN_other_substance.SetValue(False)
			self._PRW_substance.SetText('', None)
		else:
			self._RBTN_tobacco.SetValue(False)
			self._RBTN_c2.SetValue(False)
			self._RBTN_other_substance.SetValue(True)
			self._PRW_substance.SetText(self.data['substance'], self.data['pk_substance'])

		if self.data['use_type'] == 0:			# FIXME: use constant
			self._RBTN_nonharmful_use.SetValue(True)
			self._RBTN_harmful_use.SetValue(False)
			self._RBTN_presently_addicted.SetValue(False)
			self._RBTN_previously_addicted.SetValue(False)
		elif self.data['use_type'] == 1:
			self._RBTN_nonharmful_use.SetValue(False)
			self._RBTN_harmful_use.SetValue(True)
			self._RBTN_presently_addicted.SetValue(False)
			self._RBTN_previously_addicted.SetValue(False)
		elif self.data['use_type'] == 2:
			self._RBTN_nonharmful_use.SetValue(False)
			self._RBTN_harmful_use.SetValue(False)
			self._RBTN_presently_addicted.SetValue(True)
			self._RBTN_previously_addicted.SetValue(False)
		elif self.data['use_type'] == 3:
			self._RBTN_nonharmful_use.SetValue(False)
			self._RBTN_harmful_use.SetValue(False)
			self._RBTN_presently_addicted.SetValue(False)
			self._RBTN_previously_addicted.SetValue(True)

		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['notes'], ''))
		self._DPRW_quit_when.SetText(data = self.data['discontinued'])
		self._LBL_confirm_date.SetLabel(self.data['last_checked_when'].strftime('%Y %b %d'))
		self._CHBOX_confirm.Enable()
		self._CHBOX_confirm.SetValue(True)

		self._TCTRL_comment.SetFocus()

	#----------------------------------------------------------------
	def _on_substance_rbutton_selected(self, event):
		event.Skip()
		if self._RBTN_other_substance.GetValue() is True:
			self._PRW_substance.Enable(True)
			return
		self._PRW_substance.Disable()

#================================================================
# main
#================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	def test_message_inbox():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cProviderInboxPnl, -1)
#		app.MainLoop()

#	def test_msg_ea():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cInboxMessageEAPnl, -1)
#		app.MainLoop()


	#test_message_inbox()
	#test_msg_ea()
