# GNUmed

#===========================================================
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import os.path
import datetime as pyDT
import logging
import decimal


import wx


from Gnumed.pycommon import gmGuiBroker
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmI18N

from Gnumed.business import gmPerson
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmAllergy
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinicalCalculator
from Gnumed.business import gmPathLab
from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmPatPicWidgets


_log = logging.getLogger('gm.ui')

#===========================================================
from Gnumed.wxGladeWidgets import wxgTopPnl

class cTopPnl(wxgTopPnl.wxgTopPnl):

	def __init__(self, *args, **kwargs):

		wxgTopPnl.wxgTopPnl.__init__(self, *args, **kwargs)

		self.__gb = gmGuiBroker.GuiBroker()

		self.curr_pat = gmPerson.gmCurrentPatient()

		self.__init_ui()
		self.__register_interests()
	#-------------------------------------------------------
	def __init_ui(self):
		cfg = gmCfg2.gmCfgData()
		if cfg.get(option = 'slave'):
			self._TCTRL_patient_selector.SetEditable(0)
			self._TCTRL_patient_selector.SetToolTip(None)

		if sys.platform == u'darwin':
			_log.debug('adjusting font size on Mac for top panel parts')
			for ctrl in [self._TCTRL_patient_selector, self._LBL_age, self._LBL_allergies, self._TCTRL_allergies]:
				curr_font = ctrl.GetFont()
				mac_font = wx.FontFromNativeInfo(curr_font.NativeFontInfo)
				mac_font.SetPointSize(pointSize = int(curr_font.GetPointSize() / 0.8))
				ctrl.SetFont(mac_font)

		# get panel to use
		dbcfg = gmCfg.cCfgSQL()
		pk_panel = dbcfg.get2 (
			option = u'horstspace.top_panel.lab_panel',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user'
		)
		if pk_panel is None:
			self.__lab_panel = None
		else:
			self.__lab_panel = gmPathLab.cTestPanel(aPK_obj = pk_panel)
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		wx.EVT_LEFT_DCLICK(self._TCTRL_allergies, self._on_allergies_dclicked)

		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'focus_patient_search', receiver = self._on_focus_patient_search)

		gmDispatcher.connect(signal = u'gm_table_mod', receiver = self._on_database_signal)

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

		if kwds['table'] not in [u'dem.identity', u'dem.names', u'dem.identity_tag', u'clin.allergy', u'clin.allergy_state', u'clin.test_result', u'clin.patient']:
			return True

		if self.curr_pat.connected:
			# signal is not about our patient: ignore signal
			if kwds['pk_identity'] != self.curr_pat.ID:
				return True

		if kwds['table'] == u'dem.identity':
			# we don't care about newly INSERTed or DELETEd patients
			if kwds['operation'] != 'UPDATE':
				return True
			self.__update_age_label()
			return True

		if kwds['table'] == u'dem.names':
			self.__update_age_label()
			return True

		if kwds['table'] == u'dem.identity_tag':
			self.__update_tags()
			return True

		if kwds['table'] in [u'clin.allergy', u'clin.allergy_state']:
			self.__update_allergies()
			return True

		if kwds['table'] in [u'clin.test_result', u'clin.patient']:
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
	def __update_tags(self):
		self._PNL_tags.refresh(patient = self.curr_pat)
	#-------------------------------------------------------
	def __update_lab(self):

		if not self.curr_pat.connected:
			self._LBL_lab.SetLabel(u'')
			return

		tests2show = []

		rr = self.curr_pat.emr.get_most_recent_results(loinc = gmLOINC.LOINC_rr_quantity, no_of_results = 1)
		if rr is None:
			tests2show.append(_(u'RR ?'))
		else:
			#tests2show.append(_(u'%s%s') % (rr['unified_val'], rr['val_unit']))
			tests2show.append(rr['unified_val'])

		hr = self.curr_pat.emr.get_most_recent_results(loinc = gmLOINC.LOINC_heart_rate_quantity, no_of_results = 1)
		if hr is not None:
			tests2show.append(u'%s %s' % (hr['abbrev_tt'], hr['unified_val']))

		bmi = self.curr_pat.emr.bmi
		if bmi.numeric_value is not None:
			tests2show.append(_(u'BMI %s') % bmi.numeric_value.quantize(decimal.Decimal('1.')))
		else:
			weight = self.curr_pat.emr.get_most_recent_results(loinc = gmLOINC.LOINC_weight, no_of_results = 1)
			if weight is None:
				tests2show.append(_(u'BMI ?'))
			else:
				tests2show.append(u'%s%s' % (weight['unified_val'], weight['val_unit']))

		gfr_or_crea = self.curr_pat.emr.best_gfr_or_crea
		if gfr_or_crea is None:
			tests2show.append(_(u'GFR ?'))
		else:
			try:
				tests2show.append(_(u'GFR %s') % gfr_or_crea.numeric_value.quantize(decimal.Decimal('1.')))
			except AttributeError:
				tests2show.append(u'%s %s' % (gfr_or_crea['abbrev_tt'], gfr_or_crea['unified_val']))

		edc = self.curr_pat.emr.EDC
		if edc is not None:
			if self.curr_pat.emr.EDC_is_fishy:
				tests2show.append(_(u'?EDC %s') % gmDateTime.pydt_strftime(edc, '%Y-%b-%d', accuracy = gmDateTime.acc_days))
			else:
				tests2show.append(_(u'EDC %s') % gmDateTime.pydt_strftime(edc, '%Y-%b-%d', accuracy = gmDateTime.acc_days))

		inr = self.curr_pat.emr.get_most_recent_results(loinc = gmLOINC.LOINC_inr_quantity, no_of_results = 1)
		if inr is not None:
			tests2show.append(u'%s %s' % (hr['abbrev_tt'], hr['unified_val']))

		# include panel if configured, only show if exist
		if self.__lab_panel is not None:
			for result in self.__lab_panel.get_most_recent_results(pk_patient = self.curr_pat.ID, order_by = u'unified_abbrev', group_by_meta_type = True):
				tests2show.append(u'%s %s' % (result['abbrev_tt'], result['unified_val']))

		self._LBL_lab.SetLabel(u'; '.join(tests2show))

	#-------------------------------------------------------
	def __update_age_label(self):

		# no patient
		if not self.curr_pat.connected:
			self._LBL_age.SetLabel(_('<Age>'))
			self._LBL_age.SetToolTipString(_('no patient selected'))
			return

		# gender is always known
		tt = _(u'Gender: %s (%s) - %s\n') % (
			self.curr_pat.gender_symbol,
			gmTools.coalesce(self.curr_pat[u'gender'], u'?'),
			self.curr_pat.gender_string
		)

		# dob is not known
		if self.curr_pat['dob'] is None:
			age = u'%s  %s' % (
				self.curr_pat.gender_symbol,
				self.curr_pat.get_formatted_dob()
			)
			self._LBL_age.SetLabel(age)
			self._LBL_age.SetToolTipString(tt)
			return

		tt += _('Born: %s\n') % self.curr_pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding())

		# patient is dead
		if self.curr_pat['deceased'] is not None:
			tt += _('Died: %s\n') % gmDateTime.pydt_strftime(self.curr_pat['deceased'], '%d %b %Y')
			tt += _('At age: %s\n') % self.curr_pat['medical_age']
			age = u'%s  %s - %s (%s)' % (
				self.curr_pat.gender_symbol,
				self.curr_pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding()),
				gmDateTime.pydt_strftime(self.curr_pat['deceased'], '%d %b %Y'),
				self.curr_pat['medical_age']
			)
			if self.curr_pat['dob_is_estimated']:
				tt += _(' (date of birth and age are estimated)\n')
			self._LBL_age.SetLabel(age)
			self._LBL_age.SetToolTipString(tt)
			return

		# patient alive
		now = gmDateTime.pydt_now_here()

		# patient birthday ?
		if self.curr_pat.get_formatted_dob(format = '%m-%d') == now.strftime('%m-%d'):
			template = _('%(sex)s  %(dob)s (%(age)s today !)')
			tt += _("\nToday is the patient's birthday !\n\n")
		else:
			if self.curr_pat.current_birthday_passed():
				template = u'%(sex)s  %(dob)s%(l_arr)s (%(age)s)'
				tt += _(u'Birthday: %s ago\n') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = self.curr_pat.birthday_this_year, end = now)
				)
			else:
				template = u'%(sex)s  %(r_arr)s%(dob)s (%(age)s)'
				tt += _(u'Birthday: in %s\n') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = now, end = self.curr_pat.birthday_this_year)
				)

		tt += _('Age: %s\n') % self.curr_pat['medical_age']

		# FIXME: if the age is below, say, 2 hours we should fire
		# a timer here that updates the age in increments of 1 minute ... :-)
		age = template % {
			u'sex': self.curr_pat.gender_symbol,
			u'dob': self.curr_pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding()),
			u'age': self.curr_pat['medical_age'],
			u'r_arr': gmTools.u_right_arrow,
			u'l_arr': gmTools.u_left_arrow
		}

		# Easter Egg ;-)
		if self.curr_pat['lastnames'] == u'Leibner':
			if self.curr_pat['firstnames'] == u'Steffi':
				if self.curr_pat['preferred'] == u'Wildfang':
					age = u'%s %s' % (gmTools.u_black_heart, age)

		if self.curr_pat['dob_is_estimated']:
			tt += _(' (date of birth and age are estimated)\n')

		self._LBL_age.SetLabel(age)
		self._LBL_age.SetToolTipString(tt)
	#-------------------------------------------------------
	def __update_allergies(self, **kwargs):

		show_red = True

		emr = self.curr_pat.get_emr()
		state = emr.allergy_state

		# state in tooltip
		if state['last_confirmed'] is None:
			confirmed = _('never')
		else:
			confirmed = gmDateTime.pydt_strftime(state['last_confirmed'], '%Y %b %d')
		tt = (state.state_string + (90 * u' '))[:90] + u'\n'
		tt += _('last confirmed %s\n') % confirmed
		tt += gmTools.coalesce(state['comment'], u'', _('Comment (%s): %%s') % state['modified_by'])
		tt += u'\n'

		# allergies
		display = []
		for allergy in emr.get_allergies():
			# in field: "true" allergies only, not intolerances
			if allergy['type'] == u'allergy':
				display.append(allergy['descriptor'][:10].strip() + gmTools.u_ellipsis)
			# in tooltip
			if allergy['definite']:
				certainty = _('definite')
			else:
				certainty = _('suspected')
			reaction = gmTools.coalesce(allergy['reaction'], _('reaction not recorded'))
			if len(reaction) > 50:
				reaction = reaction[:50] + gmTools.u_ellipsis
			tt += u'%s (%s, %s): %s\n' % (
				allergy['descriptor'],
				allergy['l10n_type'],
				certainty,
				reaction
			)

		if len(display) == 0:
			display = state.state_symbol
			if display == gmTools.u_diameter:
				show_red = False
		else:
			display = ','.join(display)

		if state['last_confirmed'] is not None:
			display += gmDateTime.pydt_strftime(state['last_confirmed'], ' (%Y %b)')

		if show_red:
			self._LBL_allergies.SetForegroundColour('red')
			self._TCTRL_allergies.SetForegroundColour('red')
		else:
			self._LBL_allergies.SetForegroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT))
			self._TCTRL_allergies.SetForegroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT))

		self._TCTRL_allergies.SetValue(display)
		self._TCTRL_allergies.SetToolTipString(tt)

#===========================================================	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.SetWidget(cTopPanel, -1)
	app.MainLoop()
#===========================================================
