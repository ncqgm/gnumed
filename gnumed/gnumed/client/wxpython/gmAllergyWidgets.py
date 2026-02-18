"""GNUmed allergy related widgets."""
############################################################################
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import sys
import datetime as pyDT
import logging


import wx


# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPerson
from Gnumed.business import gmAllergy


_log = logging.getLogger('gm.ui')

#======================================================================
def edit_allergies(parent=None, allergy=None, single_entry=False):
	"Fake wrapper, will always call the allergy manager."

	dlg = cAllergyManagerDlg(parent = parent, id = -1)
	result = dlg.ShowModal()
	dlg.DestroyLater()
	if result != wx.ID_OK:
		return False

	return True

#------------------------------------------------------------
def turn_substance_intake_into_allergy(parent=None, intake=None, emr=None):

	if not intake['discontinued']:
		intake['discontinued'] = gmDateTime.pydt_now_here()
	if intake['discontinue_reason'] is None:
		intake['discontinue_reason'] = '%s %s' % (_('not tolerated:'), _('discontinued due to allergy or intolerance'))
	else:
		if not intake['discontinue_reason'].endswith(_('; not tolerated')):
			intake['discontinue_reason'] += _('; not tolerated')
	if not intake.save():
		return False

	intake.turn_into_allergy(encounter_id = emr.active_encounter['pk_encounter'])
#	drug = intake.containing_drug
#	comps = [ c['substance'] for c in drug.components ]
#	if len(comps) > 1:
#		gmGuiHelpers.gm_show_info (
#			title = _('Documented an allergy'),
#			info = _(
#				'An allergy was documented against the substance:\n'
#				'\n'
#				'  [%s]\n'
#				'\n'
#				'This substance was taken with the multi-component drug product:\n'
#				'\n'
#				'  [%s (%s)]\n'
#				'\n'
#				'Note that ALL components of this product were discontinued.'
#			) % (
#				intake['substance'],
#				intake['drug_product'],
#				' & '.join(comps)
#			)
#		)
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	dlg = cAllergyManagerDlg(parent, -1)
	dlg.ShowModal()
	return True

#======================================================================
from Gnumed.wxGladeWidgets import wxgAllergyEditAreaPnl

class cAllergyEditAreaPnl(wxgAllergyEditAreaPnl.wxgAllergyEditAreaPnl):

	def __init__(self, *args, **kwargs):
		wxgAllergyEditAreaPnl.wxgAllergyEditAreaPnl.__init__(self, *args, **kwargs)

		try:
			self.__allergy = kwargs['allergy']
		except KeyError:
			self.__allergy = None

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = ["""
select substance, substance
from clin.allergy
where substance %(fragment_condition)s

	union

select generics, generics
from clin.allergy
where generics %(fragment_condition)s

	union

select allergene, allergene
from clin.allergy
where allergene %(fragment_condition)s

	union

select atc_code, atc_code
from clin.allergy
where atc_code %(fragment_condition)s
"""
			]
		)
		mp.setThresholds(2, 3, 5)
		self._PRW_trigger.matcher = mp

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = ["""
select narrative, narrative
from clin.allergy
where narrative %(fragment_condition)s
"""]
		)
		mp.setThresholds(2, 3, 5)
		self._PRW_reaction.matcher = mp

#		self._RBTN_type_sensitivity.MoveAfterInTabOrder(self._RBTN_type_allergy)
#		self._ChBOX_definite.MoveAfterInTabOrder(self._RBTN_type_sensitivity)

		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def clear(self):
		self.__allergy = None
		return self.refresh()
	#--------------------------------------------------------
	def refresh(self, allergy=None):

		if allergy is not None:
			self.__allergy = allergy

		if self.__allergy is None:
			ts = gmDateTime.cFuzzyTimestamp (
				timestamp = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone),
				accuracy = gmDateTime.ACC_DAYS
			)
			self._DPRW_date_noted.SetData(data = ts)
			self._PRW_trigger.SetText()
			self._TCTRL_product_name.SetValue('')
			self._TCTRL_generic.SetValue('')
			self._ChBOX_generic_specific.SetValue(0)
			self._TCTRL_atc_classes.SetValue('')
			self._PRW_reaction.SetText()
			self._RBTN_type_allergy.SetValue(1)
			self._RBTN_type_sensitivity.SetValue(0)
			self._ChBOX_definite.SetValue(1)
			return True

		if not isinstance(self.__allergy, gmAllergy.cAllergy):
			raise ValueError('[%s].refresh(): expected gmAllergy.cAllergy instance, got [%s] instead' % (self.__class__.__name__, self.__allergy))

		ts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__allergy['date'],
			accuracy = gmDateTime.ACC_DAYS
		)
		self._DPRW_date_noted.SetData(data=ts)
		self._PRW_trigger.SetText(value = self.__allergy['allergene'])
		self._TCTRL_product_name.SetValue(self.__allergy['substance'])
		self._TCTRL_generic.SetValue(gmTools.coalesce(self.__allergy['generics'], ''))
		self._ChBOX_generic_specific.SetValue(self.__allergy['generic_specific'])
		self._TCTRL_atc_classes.SetValue(gmTools.coalesce(self.__allergy['atc_code'], ''))
		self._PRW_reaction.SetText(value = gmTools.coalesce(self.__allergy['reaction'], ''))
		if self.__allergy['type'] == 'allergy':
			self._RBTN_type_allergy.SetValue(1)
		else:
			self._RBTN_type_sensitivity.SetValue(1)
		self._ChBOX_definite.SetValue(self.__allergy['definite'])
	#--------------------------------------------------------
	def __is_valid_for_save(self):

		if self._PRW_trigger.GetValue().strip() == '':
			#self._PRW_trigger.SetBackgroundColour('pink')
			#self._PRW_trigger.Refresh()
			self._PRW_trigger.display_as_valid(False)
			self._PRW_trigger.SetFocus()
			return False
		#self._PRW_trigger.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_trigger.display_as_valid(True)
		self._PRW_trigger.Refresh()

		if not self._DPRW_date_noted.is_valid_timestamp(empty_is_valid = False):
			self._DPRW_date_noted.display_as_valid(False)
			self._DPRW_date_noted.SetFocus()
			return False
		self._DPRW_date_noted.display_as_valid(True)

		return True
	#--------------------------------------------------------
	def save(self, can_create=True):
		if not self.__is_valid_for_save():
			return False

		if self.__allergy is None:
			if not can_create:
				gmDispatcher.send(signal='statustext', msg=_('Creating new allergy not allowed.'))
				return False

			pat = gmPerson.gmCurrentPatient()
			emr = pat.emr

			if self._RBTN_type_allergy.GetValue():
				allg_type = 'allergy'
			else:
				allg_type = 'sensitivity'
			self.__allergy = emr.add_allergy (
				allergene = self._PRW_trigger.GetValue().strip(),
				allg_type = allg_type
			)

		# and update it with known data
		self.__allergy['date'] = self._DPRW_date_noted.GetData().get_pydt()
		self.__allergy['allergene'] = self._PRW_trigger.GetValue().strip()
		# FIXME: determine product name/generic/etc from substance (trigger field)
		self.__allergy['generic_specific'] = (True and self._ChBOX_generic_specific.GetValue())
		self.__allergy['reaction'] = self._PRW_reaction.GetValue().strip()
		self.__allergy['definite'] = (True and self._ChBOX_definite.GetValue())
		if self._RBTN_type_allergy.GetValue():
			 self.__allergy['pk_type'] = 'allergy'
		else:
			self.__allergy['pk_type'] = 'sensitivity'

		self.__allergy.save_payload()

		return True

#======================================================================
from Gnumed.wxGladeWidgets import wxgAllergyEditAreaDlg

class cAllergyEditAreaDlg(wxgAllergyEditAreaDlg.wxgAllergyEditAreaDlg):

	def __init__(self, *args, **kwargs):

		try:
			allergy = kwargs['allergy']
			del kwargs['allergy']
		except KeyError:
			allergy = None

		wxgAllergyEditAreaDlg.wxgAllergyEditAreaDlg.__init__(self, *args, **kwargs)

		if allergy is None:
#			self._BTN_save.SetLabel(_('&Save'))
			self._BTN_clear.SetLabel(_('&Clear'))
		else:
#			self._BTN_save.SetLabel(_('Update'))
			self._BTN_clear.SetLabel(_('&Restore'))

		self._PNL_edit_area.refresh(allergy = allergy)
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PNL_edit_area.refresh()

#======================================================================
from Gnumed.wxGladeWidgets import wxgAllergyManagerDlg

class cAllergyManagerDlg(wxgAllergyManagerDlg.wxgAllergyManagerDlg):

	def __init__(self, *args, **kwargs):

		wxgAllergyManagerDlg.wxgAllergyManagerDlg.__init__(self, *args, **kwargs)

		self.Centre(direction = wx.BOTH)

		self.__set_columns()
		# MacOSX crashes on this with:
		#  exception type : wx._core.wxAssertionError
		#  exception value: C++ assertion "i" failed at /BUILD/wxPython-src-2.8.3.0/src/common/wincmn.cpp(2634) in DoMoveInTabOrder(): MoveBefore/AfterInTabOrder(): win is not a sibling
		# while Win/Linux work just fine
		#self._PNL_edit_area._ChBOX_definite.MoveAfterInTabOrder(self._BTN_save)
		self.__refresh_state_ui()
		self.__refresh_details_ui()
		print(self._PNL_edit_area.Parent)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __set_columns(self):
		self._LCTRL_allergies.set_columns (columns = [
			_('Type'),
			_('Certainty'),
			_('Trigger'),
			_('Reaction')
		])
	#--------------------------------------------------------
	def __refresh_state_ui(self):
		pat = gmPerson.gmCurrentPatient()
		state = gmAllergy.get_allergy_state(pk_patient = pat.ID)
		if state is None:
			self._TXT_current_state.SetLabel(_('<allergy state unasked>'))
			self._TXT_last_confirmed.SetLabel(_('<allergy state unasked>'))
			self._RBTN_unknown.SetValue(True)
			self._RBTN_none.SetValue(False)
			self._RBTN_some.SetValue(False)
			self._RBTN_unknown.Enable(True)
			self._RBTN_none.Enable(True)
			return

		self._TXT_current_state.SetLabel(state.state_string)
		self._TXT_last_confirmed.SetLabel(state['last_confirmed'].strftime('%x %H:%M'))
		if state['has_allergy'] is gmAllergy.ALLERGY_STATE_UNKNOWN:
			self._RBTN_unknown.SetValue(True)
			self._RBTN_unknown.Enable(True)
			self._RBTN_none.SetValue(False)
			self._RBTN_none.Enable(True)
			self._RBTN_some.SetValue(False)
		elif state['has_allergy'] == gmAllergy.ALLERGY_STATE_NONE:
			self._RBTN_unknown.SetValue(False)
			self._RBTN_unknown.Enable(True)
			self._RBTN_none.SetValue(True)
			self._RBTN_none.Enable(True)
			self._RBTN_some.SetValue(False)
		elif state['has_allergy'] == gmAllergy.ALLERGY_STATE_SOME:
			self._RBTN_unknown.SetValue(False)
			self._RBTN_unknown.Enable(True)
			self._RBTN_none.Enable(False)
			self._RBTN_none.SetValue(False)
			self._RBTN_some.SetValue(True)
		if state['comment']:
			self._TCTRL_state_comment.SetValue(state['comment'])

	#--------------------------------------------------------
	def __refresh_details_ui(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr
		allergies = emr.get_allergies()
		no_of_allergies = len(allergies)

		# display allergies
		self._LCTRL_allergies.DeleteAllItems()
		if no_of_allergies > 0:
			emr.allergy_state = gmAllergy.ALLERGY_STATE_SOME

			for allergy in allergies:
				row_idx = self._LCTRL_allergies.InsertItem(no_of_allergies, allergy['l10n_type'])
				if allergy['definite']:
					label = _('definite')
				else:
					label = ''
				self._LCTRL_allergies.SetItem(row_idx, 1, label)
				self._LCTRL_allergies.SetItem(row_idx, 2, allergy['descriptor'])
				self._LCTRL_allergies.SetItem(row_idx, 3, gmTools.coalesce(allergy['reaction'], ''))
			self._LCTRL_allergies.set_data(data=allergies)

			self._LCTRL_allergies.Enable(True)
			self._RBTN_some.SetValue(True)
			self._RBTN_unknown.Enable(False)
			self._RBTN_none.Enable(False)
		else:
			self._LCTRL_allergies.Enable(False)
			self._RBTN_unknown.Enable(True)
			self._RBTN_none.Enable(True)

		self._LCTRL_allergies.set_column_widths (widths = [
			wx.LIST_AUTOSIZE,
			wx.LIST_AUTOSIZE,
			wx.LIST_AUTOSIZE,
			wx.LIST_AUTOSIZE
		])

		self._PNL_edit_area.clear()
		self._BTN_delete.Enable(False)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_dismiss_button_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()

	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._LCTRL_allergies.deselect_selected_item()
		self._PNL_edit_area.clear()
		self._BTN_delete.Enable(False)
		self._LBL_message.SetLabel(_('Input new allergy item:'))

	#--------------------------------------------------------
	def _on_delete_button_pressed(self, evt):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr

		allergy = self._LCTRL_allergies.get_selected_item_data(only_one=True)
		if allergy is None:
			return
		emr.delete_allergy(pk_allergy = allergy['pk_allergy'])

		state = emr.allergy_state
		state['last_confirmed'] = 'now'
		state.save_payload()

		self.__refresh_state_ui()
		self.__refresh_details_ui()
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		allergy = self._LCTRL_allergies.get_selected_item_data(only_one=True)
		if allergy is None:
			return
		self._PNL_edit_area.refresh(allergy = allergy)
		self._BTN_delete.Enable(True)
		self._LBL_message.SetLabel(_('Edit the selected allergy item:'))
	#--------------------------------------------------------
	def _on_confirm_button_pressed(self, evt):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr
		state = emr.ensure_has_allergy_state()
		allergies = emr.get_allergies()

		cmt = self._TCTRL_state_comment.GetValue().strip()

		if self._RBTN_unknown.GetValue():
			if len(allergies) > 0:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot set allergy state to <unknown> because there are allergies stored for this patient.'), beep = True)
				self._RBTN_some.SetValue(True)
				state['has_allergy'] = 1
				return False
			else:
				state['has_allergy'] = None

		elif self._RBTN_none.GetValue():
			if len(allergies) > 0:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot set allergy state to <None> because there are allergies stored for this patient.'), beep = True)
				self._RBTN_some.SetValue(True)
				state['has_allergy'] = 1
				return False
			else:
				state['has_allergy'] = 0

		elif self._RBTN_some.GetValue():
			if (len(allergies) == 0) and (cmt == ''):
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot set allergy state to <some> because there are neither allergies nor a comment available for this patient.'), beep = True)
				return False
			else:
				state['has_allergy'] = 1

		state['comment'] = cmt
		state['last_confirmed'] = 'now'

		state.save_payload()
		self.__refresh_state_ui()
	#--------------------------------------------------------
	def _on_save_details_button_pressed(self, evt):

		if not self._PNL_edit_area.save():
			return False

		pat = gmPerson.gmCurrentPatient()
		state = pat.emr.ensure_has_allergy_state()
		state['last_confirmed'] = 'now'
		state.save_payload()

		self.__refresh_state_ui()
		self.__refresh_details_ui()

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	from Gnumed.wxpython import gmGuiTest

	#-----------------------------------------------
#	def test_allergy_edit_area_dlg():
#		app = wx.PyWidgetTester(size = (600, 600))
#		dlg = cAllergyEditAreaDlg(parent=app.frame, id=-1)
#		dlg.ShowModal()
#		emr = pat.emr
#		allergy = emr.get_allergies()[0]
#		dlg = cAllergyEditAreaDlg(parent=app.frame, id=-1, allergy=allergy)
#		dlg.ShowModal()
#		return
	#-----------------------------------------------
	def test_allergy_manager_dlg():
		main_frame = gmGuiTest.setup_widget_test_env(patient = 12)
		dlg = cAllergyManagerDlg(main_frame, size = (800, 600))
		#dlg.whatever_else_is_necessary(...)
		wx.CallLater(2000, dlg.ShowModal)
		wx.GetApp().MainLoop()

	#-----------------------------------------------
	test_allergy_manager_dlg()

	#test_allergy_edit_area_dlg()

