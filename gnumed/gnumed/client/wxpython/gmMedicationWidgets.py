"""GNUmed medication handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import datetime as pydt


import wx
import wx.grid


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
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinicalCalculator
from Gnumed.business import gmPathLab

from Gnumed.wxpython import gmRegetMixin


_log = logging.getLogger('gm.ui')

#============================================================
from Gnumed.wxGladeWidgets import wxgCurrentSubstancesPnl

class cCurrentSubstancesPnl(wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl, gmRegetMixin.cRegetOnPaintMixin):

	"""Panel holding a grid with current substances. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__grouping_choice_labels = [
			{'label': _('Health issue'), 'data': 'issue'} ,
			{'label': _('Episode'), 'data': 'episode'},
			{'label': _('Started'), 'data': 'start'}
		]
		self.__lab_panel = None

		self.__init_ui()
		self.__register_interests()

	#-----------------------------------------------------
	def __init_ui(self):
		self._CHCE_grouping.Clear()
		for option in self.__grouping_choice_labels:
			self._CHCE_grouping.Append(option['label'], option['data'])
		self._CHCE_grouping.SetSelection(0)

	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		"""Populate cells with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self._grid_substances.patient = pat
			self.__refresh_gfr(pat)
			self.__refresh_lab(patient = pat)
		else:
			self._grid_substances.patient = None
			self.__clear_gfr()
			self.__refresh_lab(patient = None)
		return True

	#--------------------------------------------------------
	def __get_loincs2monitor(self) -> tuple:
		loincs2monitor = set()
		loincs2monitor_data = {}
		loinc_max_age:dict[str, int] = {}
		loinc_max_age_str:dict[str, str] = {}
		for intake in self._grid_substances.get_row_data():
			for l in intake['loincs']:
				loincs2monitor.add(l['loinc'])
				loincs2monitor_data[l['loinc']] = {
					'substance': intake['substance'],
					'comment': l['comment']
				}
				if l['max_age_in_secs'] is not None:
					try:
						if loinc_max_age[l['loinc']] > l['max_age_in_secs']:
							loinc_max_age[l['loinc']] = l['max_age_in_secs']
							loinc_max_age_str[l['loinc']] = l['max_age_str']
					except KeyError:
						loinc_max_age[l['loinc']] = l['max_age_in_secs']
						loinc_max_age_str[l['loinc']] = l['max_age_str']
		return loincs2monitor, loincs2monitor_data, loinc_max_age, loinc_max_age_str

	#--------------------------------------------------------
	def __get_most_recent_results2show(self, emr, loincs2monitor:list[str]) -> tuple:
		loincs_found = set()
		most_recent_results:dict[int, gmPathLab.cTestResult] = {}
		# get most recent results for "LOINCs to monitor"
		for loinc in loincs2monitor:
			results = emr.get_most_recent_results_in_loinc_group(loincs = [loinc], max_no_of_results = 1)
			if not results:
				continue
			loincs_found.add(loinc)
			result = results[0]
			most_recent_results[result['pk_test_result']] = result
		# get most recent results for "general medication monitoring lab panel"
		if self.__lab_panel:
			panel_results = self.__lab_panel.get_most_recent_results (
				pk_patient = emr.pk_patient,
				order_by = 'unified_abbrev',
				group_by_meta_type = True
			)
			for result in panel_results:
				loincs_found.add(result['loinc_tt'])
				loincs_found.add(result['loinc_meta'])
				most_recent_results[result['pk_test_result']] = result
		return most_recent_results, loincs_found

	#--------------------------------------------------------
	def __refresh_most_recent_results (self,
		most_recent_results:dict[int, gmPathLab.cTestResult],
		loinc_max_age:dict[str, int],
		loinc_max_age_str:dict[str, str],
		loincs2monitor_data:dict[str, dict]
	):
		now = gmDateTime.pydt_now_here()
		for pk_result in most_recent_results:
			result = most_recent_results[pk_result]
			# test type
			lbl = wx.StaticText(self, -1, '%s:' % result['unified_abbrev'])
			lbl.SetForegroundColour('blue')
			# calculate test result
			indicate_attention = False
			if result.is_considered_abnormal:
				indicate_attention = True
			# calculate tooltip data
			max_age = None
			try:
				max_age = loinc_max_age[result['loinc_tt']]
				max_age_str = loinc_max_age_str[result['loinc_tt']]
			except KeyError:
				try:
					max_age = loinc_max_age[result['loinc_meta']]
					max_age_str = loinc_max_age_str[result['loinc_meta']]
				except KeyError:
					pass
			subst2monitor = None
			try:
				subst2monitor = loincs2monitor_data[result['loinc_tt']]['substance']
			except KeyError:
				try:
					subst2monitor = loincs2monitor_data[result['loinc_meta']]['substance']
				except KeyError:
					pass
			monitor_comment = None
			try:
				monitor_comment = loincs2monitor_data[result['loinc_tt']]['comment']
			except KeyError:
				try:
					monitor_comment = loincs2monitor_data[result['loinc_meta']]['comment']
				except KeyError:
					pass
			result_age = now - result['clin_when']
			unhappy_reasons = []
			if result.is_considered_abnormal:
				indicator = result.formatted_abnormality_indicator
				if indicator == '':
					unhappy_reasons.append(_(' - abnormal'))
				else:
					unhappy_reasons.append(_(' - abnormal: %s') % indicator)
			if max_age is not None:
				if result_age.total_seconds() > max_age:
					unhappy_reasons.append(_(' - too old: %s ago (max: %s)') % (
						gmDateTime.format_interval_medically(result_age),
						max_age_str
					))
			# generate tooltip
			tt = [_('Most recent: %s ago') % gmDateTime.format_interval_medically(result_age)]
			if subst2monitor:
				tt.append(_('Why monitor: %s') % subst2monitor)
			if monitor_comment:
				tt.append(' %s' % monitor_comment)
			if unhappy_reasons:
				indicate_attention = True
				tt.append(_('Problems:'))
				tt.extend(unhappy_reasons)
			tt = '%s\n\n%s' % ('\n'.join(tt), result.format())
			# set test result and tooltip
			val = wx.StaticText(self, -1, '%s%s%s' % (
				result['unified_val'],
				gmTools.coalesce(result['val_unit'], '', ' %s'),
				gmTools.bool2subst(indicate_attention, gmTools.u_frowning_face, '', '')
			))
			val.SetToolTip(tt)
			if result.is_considered_abnormal:
				val.SetForegroundColour('red')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

	#--------------------------------------------------------
	def __refresh_edc(self, emr):
		edc = emr.EDC
		if not edc:
			return

		if emr.EDC_is_fishy:
			lbl = wx.StaticText(self, -1, _('EDC (!?!):'))
			val = wx.StaticText(self, -1, edc.strftime('%Y %b %d'))
		else:
			lbl = wx.StaticText(self, -1, _('EDC:'))
			val = wx.StaticText(self, -1, edc.strftime('%Y %b %d'))
		lbl.SetForegroundColour('blue')
		szr = wx.BoxSizer(wx.HORIZONTAL)
		szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
		szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
		self._GSZR_lab.Add(szr)

	#--------------------------------------------------------
	# hint at missing, but required results (set to be
	# monitored under intakes based on LOINCs):
	def __refresh_missing_by_loinc(self, loincs2monitor_missing:list, loincs2monitor_data:list):
		for loinc in loincs2monitor_missing:
			loinc_data = gmLOINC.loinc2data(loinc)
			loinc_str = loinc_data['term'] if loinc_data else loinc
			val = wx.StaticText(self, -1, '%s!' % loinc_str)
			tt = [
				_('No test result for: %s (%s)') % (loinc_str, loinc),
				'',
				_('Why monitor: %s' % loincs2monitor_data[loinc]['substance'])
			]
			try:
				tt.append(' %s' % loincs2monitor_data[loinc]['comment'])
			except KeyError:
				pass
			val.SetToolTip('\n'.join(tt))
			val.SetForegroundColour('orange')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

	#--------------------------------------------------------
	def __refresh_lab(self, patient):

		self._GSZR_lab.Clear(True)		# also delete child windows
		self._HLINE_lab.Hide()
		if not patient:
			self.Layout()
			return

		emr = patient.emr
		loincs2monitor, loincs2monitor_data, loinc_max_age, loinc_max_age_str = self.__get_loincs2monitor()
		most_recent_results, loincs_found = self.__get_most_recent_results2show(emr, loincs2monitor)
		self.__refresh_edc(emr)

		# decide which among Crea or GFR to show
		gfrs = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		gfr = gfrs[0] if gfrs else None
		creas = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		crea = creas[0] if creas else None
		if crea is None:
			gfr_3_months_older_than_crea = False
			if gfr:
				most_recent_results[gfr['pk_test_result']] = gfr
		elif gfr is None:
			gfr_3_months_older_than_crea = True
		else:
			three_months = pydt.timedelta(weeks = 14)
			gfr_3_months_older_than_crea = (crea['clin_when'] - gfr['clin_when']) > three_months
			if not gfr_3_months_older_than_crea:
				most_recent_results[gfr['pk_test_result']] = gfr
		# if GFR not found in most_recent_results or old, then calculate
		if gfr_3_months_older_than_crea:
			now = gmDateTime.pydt_now_here()
			calc = gmClinicalCalculator.cClinicalCalculator()
			calc.patient = patient
			gfr = calc.eGFR
			if gfr.numeric_value is None:
				gfr_msg = '?'
			else:
				gfr_msg = _('%.1f (%s ago)') % (
					gfr.numeric_value,
					gmDateTime.format_interval_medically(now - gfr.date_valid)
				)
			lbl = wx.StaticText(self, -1, _('eGFR:'))
			lbl.SetForegroundColour('blue')
			val = wx.StaticText(self, -1, gfr_msg)
			tts = []
			for egfr in calc.eGFRs:
				if egfr.numeric_value is None:
					continue
				tts.append(egfr.format (
					left_margin = 0,
					width = 50,
					eol = '\n',
					with_formula = False,
					with_warnings = True,
					with_variables = False,
					with_sub_results = False,
					return_list = False
				))
			val.SetToolTip('\n'.join(tts))
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)
		# eventually add most-recent results from monitoring panel and substances monitoring
		self.__refresh_most_recent_results(most_recent_results, loinc_max_age, loinc_max_age_str, loincs2monitor_data)
		self.__refresh_missing_by_loinc(loincs2monitor - loincs_found, loincs2monitor_data)

		self._HLINE_lab.Show()
		self.Layout()

	#--------------------------------------------------------
	def __refresh_gfr(self, patient):
		gfrs = patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		if len(gfrs) == 0:
			calc = gmClinicalCalculator.cClinicalCalculator()
			calc.patient = patient
			gfr = calc.eGFR
			if gfr.numeric_value is None:
				msg = _('GFR: ?')
				tt = gfr.message
			else:
				msg = _('eGFR: %.1f (%s)') % (
					gfr.numeric_value,
					gfr.date_valid.strftime('%b %Y')
				)
				egfrs = calc.eGFRs
				tts = []
				for egfr in egfrs:
					if egfr.numeric_value is None:
						continue
					tts.append(egfr.format (
						left_margin = 0,
						width = 50,
						eol = '\n',
						with_formula = False,
						with_warnings = True,
						with_variables = False,
						with_sub_results = False,
						return_list = False
					))
				tt = '\n'.join(tts)
		else:
			gfr = gfrs[0]
			msg = '%s: %s %s (%s)\n' % (
				gfr['unified_abbrev'],
				gfr['unified_val'],
				gmTools.coalesce(gfr['abnormality_indicator'], '', ' (%s)'),
				gfr['clin_when'].strftime('%b %Y')
			)
			tt = _('GFR reported by path lab')

		self._LBL_gfr.SetLabel(msg)
		self._LBL_gfr.SetToolTip(tt)
		self._LBL_gfr.Refresh()
		self.Layout()

	#--------------------------------------------------------
	def __clear_gfr(self):
		self._LBL_gfr.SetLabel(_('GFR: ?'))
		self._LBL_gfr.Refresh()
		self.Layout()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#--------------------------------------------------------
	def _on_database_signal(self, **kwds):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return True

		if kwds['pk_identity'] != pat.ID:
			return True

		if kwds['table'] in ['clin.intake', 'clin.intake_regimen']:
			self._schedule_data_reget()
		elif kwds['table'] == 'clin.test_result':
			self._on_test_result_mod()
		return True

	#--------------------------------------------------------
	def _on_test_result_mod(self):
		self.__refresh_lab(patient = self._grid_substances.patient)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		pk_panel = gmCfgDB.get4user (
			option = 'horstspace.medications_plugin.lab_panel',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
		if pk_panel is None:
			self.__lab_panel = None
		else:
			self.__lab_panel = gmPathLab.cTestPanel(aPK_obj = pk_panel)
		self._grid_substances.patient = None
		self.__refresh_lab(patient = None)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		self._grid_substances.add_substance()
	#--------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		self._grid_substances.edit_substance()
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		self._grid_substances.delete_intake()
	#--------------------------------------------------------
	def _on_info_button_pressed(self, event):
		self._grid_substances.show_info_on_entry()
	#--------------------------------------------------------
	def _on_interactions_button_pressed(self, event):
		self._grid_substances.check_interactions()
	#--------------------------------------------------------
	def _on_grouping_selected(self, event):
		event.Skip()
		selected_item_idx = self._CHCE_grouping.GetSelection()
		if selected_item_idx is wx.NOT_FOUND:
			return
		self._grid_substances.grouping_mode = self._CHCE_grouping.GetClientData(selected_item_idx)

	#--------------------------------------------------------
	def _on_show_discontinued_checked(self, event):
		self._grid_substances.filter_show_discontinued = self._CHBOX_show_discontinued.GetValue()

	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		self._grid_substances.print_medication_list()

	#--------------------------------------------------------
	def _on_allergy_button_pressed(self, event):
		self._grid_substances.create_allergy_from_substance()

	#--------------------------------------------------------
	def _on_kidneys_button_pressed(self, event):
		self._grid_substances.show_nephrological_info()

	#--------------------------------------------------------
	def _on_heart_button_pressed(self, event):
		self._grid_substances.show_cardiological_info()
	#----------------------------------------------------------------
	def _on_pregnancy_button_pressed(self, event):
		self._grid_substances.show_pregnancy_info()

	#----------------------------------------------------------------
	def _on_lungs_button_pressed(self, event):
		self._grid_substances.show_pulmological_info()

	#--------------------------------------------------------
	def _on_adr_button_pressed(self, event):
		self._grid_substances.report_ADR()

	#--------------------------------------------------------
	def _on_rx_button_pressed(self, event):
		self._grid_substances.prescribe()

#============================================================
# main
#------------------------------------------------------------
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

	#----------------------------------------
	gmGuiTest.test_widget(cCurrentSubstancesPnl, patient = 12)
