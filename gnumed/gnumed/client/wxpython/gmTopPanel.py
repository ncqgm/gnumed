"""GNUmed top banner
"""
#===========================================================
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import logging
import decimal


import wx


from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmExceptions

from Gnumed.business import gmPerson
from Gnumed.business import gmLOINC
from Gnumed.business import gmPathLab
from Gnumed.business import gmPraxis
from Gnumed.business import gmAllergy

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAllergyWidgets


_log = logging.getLogger('gm.ui')
if __name__ == '__main__':
	_ = lambda x:x

#===========================================================
from Gnumed.wxGladeWidgets import wxgTopPnl

class cTopPnl(wxgTopPnl.wxgTopPnl):

	def __init__(self, *args, **kwargs):

		wxgTopPnl.wxgTopPnl.__init__(self, *args, **kwargs)

		self.curr_pat = gmPerson.gmCurrentPatient()

		self.__init_ui()
		self.__register_interests()

	#-------------------------------------------------------
	def __init_ui(self):
		cfg = gmCfgINI.gmCfgData()
		if cfg.get(option = 'slave'):
			self._TCTRL_patient_selector.SetEditable(0)
			self._TCTRL_patient_selector.SetToolTip(None)

		if sys.platform == 'darwin':
			_log.debug('adjusting font size on Mac for top panel parts')
			for ctrl in [self._TCTRL_patient_selector, self._LBL_age, self._LBL_allergies, self._TCTRL_allergies]:
				curr_font = ctrl.GetFont()
				mac_font = wx.Font(curr_font.GetNativeFontInfo())
				mac_font.SetPointSize(pointSize = int(curr_font.GetPointSize() / 0.8))
				ctrl.SetFont(mac_font)

		self.__lab_panel = self.__get_lab_panel()

	#-------------------------------------------------------
	def __register_interests(self):
		# events
		self._TCTRL_allergies.Bind(wx.EVT_LEFT_DCLICK, self._on_allergies_dclicked)

		# client internal signals
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'focus_patient_search', receiver = self._on_focus_patient_search)

		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#----------------------------------------------
	# event handling
	#----------------------------------------------
	def _on_allergies_dclicked(self, evt):
		if not self.curr_pat.connected:
			gmDispatcher.send('statustext', msg = _('Cannot activate Allergy Manager. No active patient.'))
			return
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		dlg.ShowModal()
		return

	#----------------------------------------------
	def _on_database_signal(self, **kwds):

		if kwds['table'] not in ['dem.identity', 'dem.names', 'dem.identity_tag', 'clin.allergy', 'clin.allergy_state', 'clin.test_result', 'clin.patient']:
			return True

		if self.curr_pat.connected:
			# signal is not about our patient: ignore signal
			if kwds['pk_identity'] != self.curr_pat.ID:
				return True

		if kwds['table'] == 'dem.identity':
			# we don't care about newly INSERTed or DELETEd patients
			if kwds['operation'] != 'UPDATE':
				return True
			self.__update_age_label()
			return True

		if kwds['table'] == 'dem.names':
			self.__update_age_label()
			return True

		if kwds['table'] == 'dem.identity_tag':
			self.__update_tags()
			return True

		if kwds['table'] in ['clin.allergy', 'clin.allergy_state']:
			self.__update_allergies()
			return True

		if kwds['table'] in ['clin.test_result', 'clin.patient']:
			self.__update_lab()
			return True

		return True

	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		wx.CallAfter(self.__on_post_patient_selection)

	#-------------------------------------------------------
	def __on_post_patient_selection(self):
		self.__update_age_label()
		self.__update_allergies()
		self.__update_tags()
		self.__update_lab()
		self.Layout()

	#-------------------------------------------------------
	def _on_focus_patient_search(self, **kwargs):
		wx.CallAfter(self._TCTRL_patient_selector.SetFocus)

	#-------------------------------------------------------
	# internal API
	#-------------------------------------------------------
	def __get_lab_panel(self):
		# get panel to use
		pk_panel = gmCfgDB.get4user (
			option = u'horstspace.top_panel.lab_panel',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		)
		if pk_panel is None:
			return None

		try:
			panel = gmPathLab.cTestPanel(aPK_obj = pk_panel)
		except gmExceptions.ConstructorError:
			_log.exception('cannot load configured test panel')
			panel = None
		if panel is not None:
			return panel

		_log.error('Cannot load test panel [#%s] configured for patient pane (horstspace.top_panel.lab_panel).', pk_panel)
		gmGuiHelpers.gm_show_error (
			title = _('GNUmed startup'),
			error = _(
				'Cannot load test panel [#%s] configured\n'
				'for the top pane with option\n'
				'\n'
				' <horstspace.top_panel.lab_panel>\n'
				'\n'
				'Please reconfigure.'
			) % pk_panel
		)
		return None

	#-------------------------------------------------------
	def __update_tags(self):
		self._PNL_tags.refresh(patient = self.curr_pat)

	#-------------------------------------------------------
	def __update_lab(self):

		if not self.curr_pat.connected:
			self._LBL_lab.SetLabel('')
			self._LBL_lab.SetToolTip(None)
			return

		tests2show = []
		tooltip_lines = []

		RRs = self.curr_pat.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_rr_quantity, max_no_of_results = 1)
		if len(RRs) == 0:
			tests2show.append(_('BP ?'))
		else:
			tests2show.append(RRs[0]['unified_val'])
			tooltip_lines.append(_('BP: %s ago') % gmDateTime.format_apparent_age_medically (
				age = gmDateTime.calculate_apparent_age(start = RRs[0]['clin_when'])
			))

		HRs = self.curr_pat.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_heart_rate_quantity, max_no_of_results = 1)
		if len(HRs) > 0:
			tests2show.append('@ %s' % HRs[0]['unified_val'])
			tooltip_lines.append(_('%s (@) in bpm: %s ago') % (
				HRs[0]['abbrev_tt'],
				gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = HRs[0]['clin_when'])
				)
			))

		bmi = self.curr_pat.emr.bmi
		if bmi.numeric_value is not None:
			tests2show.append(_('BMI %s') % bmi.numeric_value.quantize(decimal.Decimal('1.')))
			tooltip_lines.append(_('BMI: %s ago') % gmDateTime.format_apparent_age_medically (
				age = gmDateTime.calculate_apparent_age(start = bmi.date_valid)
			))
		else:
			weights = self.curr_pat.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_weight, max_no_of_results = 1)
			if len(weights) == 0:
				tests2show.append(_('BMI ?'))
			else:
				tests2show.append('%s%s' % (weights[0]['unified_val'], weights[0]['val_unit']))
				tooltip_lines.append(_('weight: %s ago') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = weights[0]['clin_when'])
				))

		gfr_or_crea = self.curr_pat.emr.best_gfr_or_crea
		if gfr_or_crea is None:
			tests2show.append(_('GFR ?'))
		else:
			try:
				tests2show.append(_('GFR %s') % gfr_or_crea.numeric_value.quantize(decimal.Decimal('1.')))
				tooltip_lines.append(_('GFR: %s ago') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = gfr_or_crea.date_valid)
				))
			except AttributeError:
				tests2show.append('%s %s' % (gfr_or_crea['abbrev_tt'], gfr_or_crea['unified_val']))
				tooltip_lines.append(_('%s: %s ago') % (
					gfr_or_crea['abbrev_tt'],
					gmDateTime.format_apparent_age_medically (
						age = gmDateTime.calculate_apparent_age(start = gfr_or_crea['clin_when'])
					)
				))

		edc = self.curr_pat.emr.EDC
		if edc:
			if self.curr_pat.emr.EDC_is_fishy:
				tests2show.append(_('?EDC %s') % edc.strftime('%Y-%b-%d'))
			else:
				tests2show.append(_('EDC %s') % edc.strftime('%Y-%b-%d'))

		INRs = self.curr_pat.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_inr_quantity, max_no_of_results = 1)
		if len(INRs) > 0:
			tests2show.append('%s %s' % (INRs[0]['abbrev_tt'], INRs[0]['unified_val']))
			tooltip_lines.append(_('%s: %s ago') % (
				INRs[0]['abbrev_tt'],
				gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = INRs[0]['clin_when'])
				)
			))

		# include panel if configured, only show if exist
		if self.__lab_panel is not None:
			for result in self.__lab_panel.get_most_recent_results(pk_patient = self.curr_pat.ID, order_by = 'unified_abbrev', group_by_meta_type = True):
				tests2show.append('%s %s' % (result['abbrev_tt'], result['unified_val']))
				tooltip_lines.append(_('%s: %s ago') % (
					result['abbrev_tt'],
					gmDateTime.format_apparent_age_medically (
						age = gmDateTime.calculate_apparent_age(start = result['clin_when'])
					)
				))
		self._LBL_lab.Label = '; '.join(tests2show)
		self._LBL_lab.SetToolTip('\n'.join(tooltip_lines))

	#-------------------------------------------------------
	def __update_age_label(self):

		# no patient
		if not self.curr_pat.connected:
			self._LBL_age.SetLabel(_('<Age>'))
			self._LBL_age.SetToolTip(_('no patient selected'))
			return

		# gender is always known
		tt = _('Gender: %s (%s) - %s\n') % (
			self.curr_pat.gender_symbol,
			gmTools.coalesce(self.curr_pat['gender'], '?'),
			self.curr_pat.gender_string
		)

		# dob is not known
		if self.curr_pat['dob'] is None:
			age = '%s  %s' % (
				self.curr_pat.gender_symbol,
				self.curr_pat.get_formatted_dob()
			)
			self._LBL_age.SetLabel(age)
			self._LBL_age.SetToolTip(tt)
			return

		tt += _('Born: %s\n') % self.curr_pat.get_formatted_dob(format = '%d %b %Y')

		# patient is dead
		if self.curr_pat['deceased']:
			tt += _('Died: %s\n') % self.curr_pat['deceased'].strftime('%d %b %Y')
			tt += _('At age: %s\n') % self.curr_pat.medical_age
			age = '%s  %s - %s (%s)' % (
				self.curr_pat.gender_symbol,
				self.curr_pat.get_formatted_dob(format = '%d %b %Y'),
				self.curr_pat['deceased'].strftime('%d %b %Y'),
				self.curr_pat.medical_age
			)
			if self.curr_pat['dob_is_estimated']:
				tt += _(' (date of birth and age are estimated)\n')
			self._LBL_age.SetLabel(age)
			self._LBL_age.SetToolTip(tt)
			return

		# patient alive
		now = gmDateTime.pydt_now_here()

		# patient birthday ?
		if self.curr_pat.get_formatted_dob(format = '%m-%d', honor_estimation = False) == now.strftime('%m-%d'):
			template = _('%(sex)s  %(dob)s (%(age)s today !)')
			tt += _("\nToday is the patient's birthday !\n\n")
			tt += _('Age: %s\n') % self.curr_pat.medical_age
		else:
			tt += _('Age: %s, birthday:\n') % self.curr_pat.medical_age
			if self.curr_pat.current_birthday_passed is True:
				template = '%(sex)s  %(dob)s%(l_arr)s (%(age)s)'
				tt += ' ' + _('last: %s ago (this year)') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = self.curr_pat.birthday_this_year, end = now)
				) + '\n'
				tt += ' ' + _('next: in %s (next year)') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = now, end = self.curr_pat.birthday_next_year)
				) + '\n'
			elif self.curr_pat.current_birthday_passed is False:
				template = '%(sex)s  %(r_arr)s%(dob)s (%(age)s)'
				tt += ' ' + _('next: in %s (this year)') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = now, end = self.curr_pat.birthday_this_year)
				) + '\n'
				tt += ' ' + _('last: %s ago (last year)') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = self.curr_pat.birthday_last_year, end = now)
				) + '\n'
			else:	# None, unknown
				template = '%(sex)s  %(dob)s (%(age)s)'

		# FIXME: if the age is below, say, 2 hours we should fire
		# a timer here that updates the age in increments of 1 minute ... :-)
		age = template % {
			'sex': self.curr_pat.gender_symbol,
			'dob': self.curr_pat.get_formatted_dob(format = '%d %b %Y'),
			'age': self.curr_pat.medical_age,
			'r_arr': gmTools.u_arrow2right,
			'l_arr': gmTools.u_left_arrow
		}

		# Easter Egg ;-)
		if self.curr_pat['lastnames'] == 'Leibner':
			if self.curr_pat['firstnames'] == 'Steffi':
				if self.curr_pat['preferred'] == 'Wildfang':
					age = '%s %s' % (gmTools.u_black_heart, age)

		if self.curr_pat['dob_is_estimated']:
			tt += _(' (date of birth and age are estimated)\n')

		self._LBL_age.SetLabel(age)
		self._LBL_age.SetToolTip(tt)

	#-------------------------------------------------------
	def __update_allergies(self, **kwargs):

		if not self.curr_pat.connected:
			self._LBL_allergies.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
			self._TCTRL_allergies.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
			self._TCTRL_allergies.SetValue('')
			self._TCTRL_allergies.SetToolTip('')
			return

		color = 'red'
		emr = self.curr_pat.emr
		state = emr.allergy_state
		# state in tooltip
		if state:
			if state['last_confirmed'] is None:
				confirmed = _('never')
			else:
				confirmed = state['last_confirmed'].strftime('%Y %b %d')
			tt = (state.state_string + (90 * ' '))[:90] + '\n'
			tt += _('last confirmed %s\n') % confirmed
			tt += gmTools.coalesce(state['comment'], '', _('Comment (%s): %%s') % state['modified_by'])
		else:
			tt = _('allergy state not obtained')
		tt += '\n'
		# allergies
		display = []
		for allergy in emr.get_allergies():
			# in field: "true" allergies only, not intolerances
			if allergy['type'] == 'allergy':
				display.append(allergy['descriptor'][:10].strip() + gmTools.u_ellipsis)
			# in tooltip
			if allergy['definite']:
				certainty = _('definite')
			else:
				certainty = _('suspected')
			reaction = gmTools.coalesce(allergy['reaction'], _('reaction not recorded'))
			if len(reaction) > 50:
				reaction = reaction[:50] + gmTools.u_ellipsis
			tt += '%s (%s, %s): %s\n' % (
				allergy['descriptor'],
				allergy['l10n_type'],
				certainty,
				reaction
			)
		if display:
			display = ','.join(display)
		else:
			if state:
				if state['has_allergy'] == gmAllergy.ALLERGY_STATE_NONE:
					color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
				display = state.state_symbol
				if state['last_confirmed']:
					display += state['last_confirmed'].strftime(' (%Y %b)')
			else:
				color = 'yellow'
				display = _('obtain')
		self._LBL_allergies.SetForegroundColour(color)
		self._TCTRL_allergies.SetForegroundColour(color)
		self._TCTRL_allergies.SetValue(display)
		self._TCTRL_allergies.SetToolTip(tt)

#===========================================================	
if __name__ == "__main__":
	app = wx.PyWidgetTester(size = (400, 200))
	#app.SetWidget(cMainTopPanel, -1)
	app.SetWidget(cTopPnl, -1)
	app.MainLoop()
