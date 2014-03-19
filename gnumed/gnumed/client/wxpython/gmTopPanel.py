# GNUmed

#===========================================================
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import os.path
import datetime as pyDT
import logging


import wx


from Gnumed.pycommon import gmGuiBroker
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmI18N

from Gnumed.business import gmPerson
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmAllergy

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
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		wx.EVT_LEFT_DCLICK(self._TCTRL_allergies, self._on_allergies_dclicked)

		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'clin.allgergy_mod_db', receiver = self._on_allergies_change)
		gmDispatcher.connect(signal = u'clin.allergy_state_mod_db', receiver = self._on_allergies_change)
		gmDispatcher.connect(signal = u'dem.names_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'dem.identity_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'dem.identity_tag_mod_db', receiver = self._on_tag_change)

		gmDispatcher.connect(signal = u'focus_patient_search', receiver = self._on_focus_patient_search)
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
	def _on_tag_change(self):
		wx.CallAfter(self.__update_tags)
	#----------------------------------------------
	def _on_name_identity_change(self):
		wx.CallAfter(self.__update_age_label)
	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		# needed because GUI stuff can't be called from a thread (and that's
		# where we are coming from via backend listener -> dispatcher)
		wx.CallAfter(self.__on_post_patient_selection, **kwargs)
	#-------------------------------------------------------
	def _on_allergies_change(self, **kwargs):
		wx.CallAfter(self.__update_allergies)
	#-------------------------------------------------------
	def _on_focus_patient_search(self, **kwargs):
		wx.CallAfter(self._TCTRL_patient_selector.SetFocus)
	#-------------------------------------------------------
	# internal API
	#-------------------------------------------------------
	def __on_post_patient_selection(self, **kwargs):
		self.__update_age_label()
		self.__update_allergies()
		self.__update_tags()
	#-------------------------------------------------------
	def __update_tags(self):
		self._PNL_tags.refresh(patient = self.curr_pat)
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
			tt += _("\nToday is the patient's birtday !\n\n")
		else:
			if self.curr_pat.current_birthday_passed():
				template = u'%(sex)s  %(dob)s%(l_arr)s (%(age)s)'
				tt += _(u'Birthday: %s ago\n') % gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = self.curr_pat.birthday_this_year, end = now)
				)
			else:
				template = u'%(sex)s  %(r_arr)s%(dob)s (%(age)s)'
				tt += _(u'Birtday: in %s\n') % gmDateTime.format_apparent_age_medically (
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
	wx.InitAllImageHandlers()
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.SetWidget(cTopPanel, -1)
	app.MainLoop()
#===========================================================
