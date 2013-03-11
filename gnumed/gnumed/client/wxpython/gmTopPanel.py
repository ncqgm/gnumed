# GNUmed

#===========================================================
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys, os.path, datetime as pyDT, logging


import wx


from Gnumed.pycommon import gmGuiBroker, gmDispatcher, gmTools, gmCfg2, gmDateTime, gmI18N
from Gnumed.business import gmPerson, gmEMRStructItems, gmAllergy
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
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		wx.EVT_LEFT_DCLICK(self._TCTRL_allergies, self._on_allergies_dclicked)

		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'allg_mod_db', receiver = self._on_allergies_change)
		gmDispatcher.connect(signal = u'allg_state_mod_db', receiver = self._on_allergies_change)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'identity_tag_mod_db', receiver = self._on_tag_change)

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

		tt = _('Gender: %s (%s) - %s\n') % (
			self.curr_pat.gender_symbol,
			self.curr_pat['gender'],
			self.curr_pat.gender_string
		)
		tt += _('Born: %s\n') % self.curr_pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding())

		if self.curr_pat['deceased'] is None:

			if self.curr_pat.get_formatted_dob(format = '%m-%d') == pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone).strftime('%m-%d'):
				template = _('%s  %s (%s today !)')
				tt += _("\nToday is the patient's birtday !\n\n")
			else:
				template = u'%s  %s (%s)'

			tt += _('Age: %s\n') % self.curr_pat['medical_age']

			# FIXME: if the age is below, say, 2 hours we should fire
			# a timer here that updates the age in increments of 1 minute ... :-)
			age = template % (
				gmPerson.map_gender2symbol[self.curr_pat['gender']],
				self.curr_pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding()),
				self.curr_pat['medical_age']
			)

			# Easter Egg ;-)
			if self.curr_pat['lastnames'] == u'Leibner':
				if self.curr_pat['firstnames'] == u'Steffi':
					if self.curr_pat['preferred'] == u'Wildfang':
						age = u'%s %s' % (gmTools.u_black_heart, age)

		else:

			tt += _('Died: %s\n') % gmDateTime.pydt_strftime(self.curr_pat['deceased'], '%d.%b %Y')
			tt += _('At age: %s\n') % self.curr_pat['medical_age']

			template = u'%s  %s - %s (%s)'
			age = template % (
				gmPerson.map_gender2symbol[self.curr_pat['gender']],
				self.curr_pat.get_formatted_dob(format = '%d.%b %Y', encoding = gmI18N.get_encoding()),
				gmDateTime.pydt_strftime(self.curr_pat['deceased'], '%Y %b %d'),
				self.curr_pat['medical_age']
			)

		if self.curr_pat['dob_is_estimated']:
			tt += _(' (date of birth and age are estimated)\n')

		self._LBL_age.SetLabel(age)
		self._LBL_age.SetToolTipString(tt)
	#-------------------------------------------------------
	def __update_allergies(self, **kwargs):

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
		tmp = []
		for allergy in emr.get_allergies():
			# in field: "true" allergies only, not intolerances
			if allergy['type'] == 'allergy':
				tmp.append(allergy['descriptor'][:10].strip() + gmTools.u_ellipsis)
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

		if len(tmp) == 0:
			tmp = state.state_symbol
		else:
			tmp = ','.join(tmp)

		if state['last_confirmed'] is not None:
			tmp += state['last_confirmed'].strftime(' (%x)')

		self._TCTRL_allergies.SetValue(tmp)
		self._TCTRL_allergies.SetToolTipString(tt)

#===========================================================	
if __name__ == "__main__":
	wx.InitAllImageHandlers()
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.SetWidget(cTopPanel, -1)
	app.MainLoop()
#===========================================================
