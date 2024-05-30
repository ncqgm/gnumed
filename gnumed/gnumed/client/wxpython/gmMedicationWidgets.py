"""GNUmed medication handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import urllib
import datetime as pydt


import wx
import wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinicalCalculator
from Gnumed.business import gmPathLab

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmCfgWidgets


_log = logging.getLogger('gm.ui')

#============================================================
def configure_default_medications_lab_panel(parent=None):

	panels = gmPathLab.get_test_panels(order_by = 'description')
	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Select the measurements panel to show in the medications plugin.'
			'\n'
		),
		option = 'horstspace.medications_plugin.lab_panel',
		bias = 'user',
		default_value = None,
		choices = [ '%s%s' % (p['description'], gmTools.coalesce(p['comment'], '', ' (%s)')) for p in panels ],
		columns = [_('Measurements panel')],
		data = [ p['pk_test_panel'] for p in panels ],
		caption = _('Configuring medications plugin measurements panel')
	)

#============================================================
def configure_adr_url():

	def is_valid(value):
		value = value.strip()
		if value == '':
			return True, gmMedication.URL_drug_adr_german_default
		try:
			urllib.request.urlopen(value)
			return True, value
		except Exception:
			return True, value

	gmCfgWidgets.configure_string_option (
		message = _(
			'GNUmed will use this URL to access a website which lets\n'
			'you report an adverse drug reaction (ADR).\n'
			'\n'
			'If you leave this empty it will fall back\n'
			'to an URL for reporting ADRs in Germany.'
		),
		option = 'external.urls.report_ADR',
		bias = 'user',
		default_value = gmMedication.URL_drug_adr_german_default,
		validator = is_valid
	)

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
	def __refresh_lab(self, patient):

		self._GSZR_lab.Clear(True)		# also delete child windows
		self._HLINE_lab.Hide()

		if patient is None:
			self.Layout()
			return

		emr = patient.emr
		most_recent_results = {}

		# get most recent results for "LOINCs to monitor"
		loincs2monitor = set()
		loincs2monitor_data = {}
		loinc_max_age = {}
		loinc_max_age_str = {}
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
		loincs2monitor_missing = loincs2monitor.copy()
		for loinc in loincs2monitor:
			results = emr.get_most_recent_results_in_loinc_group(loincs = [loinc], max_no_of_results = 1)
			if len(results) == 0:
				continue
			loincs2monitor_missing.remove(loinc)
			# make unique
			result = results[0]
			most_recent_results[result['pk_test_result']] = result

		# get most recent results for "general medication monitoring lab panel"
		if self.__lab_panel is not None:
			for result in self.__lab_panel.get_most_recent_results (
				pk_patient = patient.ID,
				order_by = 'unified_abbrev',
				group_by_meta_type = True
			):
				try: loincs2monitor_missing.remove(result['loinc_tt'])
				except KeyError: pass
				try: loincs2monitor_missing.remove(result['loinc_meta'])
				except KeyError: pass
				# make unique
				most_recent_results[result['pk_test_result']] = result

		# those need special treatment
		gfrs = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		gfr = gfrs[0] if len(gfrs) > 0 else None
		creas = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		crea = creas[0] if len(creas) > 0 else None
		edc = emr.EDC

		# display EDC
		if edc is not None:
			if emr.EDC_is_fishy:
				lbl = wx.StaticText(self, -1, _('EDC (!?!):'))
				val = wx.StaticText(self, -1, gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
			else:
				lbl = wx.StaticText(self, -1, _('EDC:'))
				val = wx.StaticText(self, -1, gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
			lbl.SetForegroundColour('blue')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		# decide which among Crea or GFR to show
		if crea is None:
			gfr_3_months_older_than_crea = False
			if gfr is not None:
				most_recent_results = [gfr] + most_recent_results
		elif gfr is None:
			gfr_3_months_older_than_crea = True
		else:
			three_months = pydt.timedelta(weeks = 14)
			gfr_3_months_older_than_crea = (crea['clin_when'] - gfr['clin_when']) > three_months
			if not gfr_3_months_older_than_crea:
				most_recent_results = [gfr] + most_recent_results

		# if GFR not found in most_recent_results or old, then calculate
		now = gmDateTime.pydt_now_here()
		if gfr_3_months_older_than_crea:
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
			if subst2monitor is not None:
				tt.append(_('Why monitor: %s') % subst2monitor)
			if monitor_comment is not None:
				tt.append(' %s' % monitor_comment)
			if len(unhappy_reasons) > 0:
				indicate_attention = True
				tt.append(_('Problems:'))
				tt.extend(unhappy_reasons)
			tt = '%s\n\n%s' % (
				'\n'.join(tt),
				result.format()
			)
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

		# hint at missing, but required results (set to be
		# monitored under intakes based on LOINCs):
		for loinc in loincs2monitor_missing:
			#szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			loinc_data = gmLOINC.loinc2data(loinc)
			if loinc_data is None:
				loinc_str = loinc
			else:
				loinc_str = loinc_data['term']
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
					gmDateTime.pydt_strftime (
						gfr.date_valid,
						format = '%b %Y'
					)
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
				gmDateTime.pydt_strftime (
					gfr['clin_when'],
					format = '%b %Y'
				)
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

		if kwds['table'] == 'clin.intake':
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
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.wxpython import gmGuiTest

	#----------------------------------------
	gmGuiTest.test_widget(cCurrentSubstancesPnl, patient = 12)
