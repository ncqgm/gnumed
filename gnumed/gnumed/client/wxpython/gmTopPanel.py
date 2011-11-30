# GNUmed

#===========================================================
__version__ = "$Revision: 1.106 $"
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, os.path, datetime as pyDT, logging


import wx


from Gnumed.pycommon import gmGuiBroker, gmPG2, gmDispatcher, gmTools, gmCfg2, gmDateTime, gmI18N
from Gnumed.business import gmPerson, gmEMRStructItems, gmAllergy

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmPatPicWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)

[	ID_BTN_pat_demographics,
#	ID_CBOX_consult_type,
	ID_BMITOOL,
	ID_BMIMENU,
	ID_PREGTOOL,
	ID_PREGMENU,
	ID_LOCKBUTTON,
	ID_LOCKMENU,
] = map(lambda _init_ctrls: wx.NewId(), range(7))

# FIXME: need a better name here !
bg_col = wx.Colour(214,214,214)
fg_col = wx.Colour(0,0,131)
col_brightred = wx.Colour(255,0,0)
#===========================================================
class cMainTopPanel(wx.Panel):

	def __init__(self, parent, id):

		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER)

		self.__gb = gmGuiBroker.GuiBroker()

		self.__do_layout()
		self.__register_interests()

		# init plugin toolbars dict
		#self.subbars = {}
		self.curr_pat = gmPerson.gmCurrentPatient()

		# and actually display ourselves
		self.SetAutoLayout(True)
		self.Show(True)
	#-------------------------------------------------------
	def __do_layout(self):
		"""Create the layout.

		.--------------------------------.
		| patient | top row              |
		| picture |----------------------|
		|         | bottom row           |
		`--------------------------------'
		"""
		self.SetBackgroundColour(bg_col)

		# create rows
		# - top row
		# .----------------------------.
		# | patient  | age | allergies |
		# | selector |     |           |
		# `----------------------------'
		self.szr_top_row = wx.BoxSizer(wx.HORIZONTAL)

		#  - details button
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'binoculars_form.png')
#		img = wxImage(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_pat_demographics = wx.BitmapButton (
#			parent = self,
#			id = ID_BTN_pat_demographics,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wxNO_BORDER
#		)
#		self.btn_pat_demographics.SetToolTip(wxToolTip(_("display patient demographics")))
#		self.szr_top_row.Add (self.btn_pat_demographics, 0, wxEXPAND | wx.BOTTOM, 3)

		# padlock button - Dare I say HIPAA ?
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'padlock_closed.png')
#		img = wxImage(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_lock = wx.BitmapButton (
#			parent = self,
#			id = ID_LOCKBUTTON,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wxNO_BORDER
#		)
#		self.btn_lock.SetToolTip(wxToolTip(_('lock client')))
#		self.szr_top_row.Add(self.btn_lock, 0, wxALL, 3)

		#  - patient selector
		self.patient_selector = gmPatSearchWidgets.cActivePatientSelector(self, -1)
		cfg = gmCfg2.gmCfgData()
		if cfg.get(option = 'slave'):
			self.patient_selector.SetEditable(0)
			self.patient_selector.SetToolTip(None)
		self.patient_selector.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))

		#  - age
		self.lbl_age = wx.StaticText(self, -1, u'', style = wx.ALIGN_CENTER_VERTICAL)
		self.lbl_age.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))

		#  - allergies (substances only, like "makrolides, penicillins, eggs")
		self.lbl_allergies = wx.StaticText (self, -1, _('Caveat'), style = wx.ALIGN_CENTER_VERTICAL)
		self.lbl_allergies.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		self.lbl_allergies.SetBackgroundColour(bg_col)
		self.lbl_allergies.SetForegroundColour(col_brightred)
		self.txt_allergies = wx.TextCtrl (self, -1, "", style = wx.TE_READONLY)
		self.txt_allergies.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		self.txt_allergies.SetForegroundColour (col_brightred)

		self.szr_top_row.Add(self.patient_selector, 6, wx.LEFT | wx.BOTTOM, 3)
		self.szr_top_row.Add(self.lbl_age, 0, wx.ALL, 3)
		self.szr_top_row.Add(self.lbl_allergies, 0, wx.ALL, 3)
		self.szr_top_row.Add(self.txt_allergies, 8, wx.BOTTOM, 3)

		# - bottom row
		# .----------------------------------------------------------.
		# | plugin toolbar | bmi | edc |          | encounter | lock |
		# |                |     |     |          | type sel  |      |
		# `----------------------------------------------------------'
		#self.tb_lock.AddControl(wx.StaticBitmap(self.tb_lock, -1, getvertical_separator_thinBitmap(), wx.DefaultPosition, wx.DefaultSize))

		# (holds most of the buttons)
		self.szr_bottom_row = wx.BoxSizer(wx.HORIZONTAL)
		self._PNL_tags = gmDemographicsWidgets.cImageTagPresenterPnl(self, -1)
		self.szr_bottom_row.Add(self._PNL_tags, 2, wx.ALIGN_CENTER_VERTICAL, 0)

		# spacer
		self.szr_bottom_row.Add((20, 20), 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)

		pnl_enc = gmEMRStructWidgets.cActiveEncounterPnl(self, -1)
		self.szr_bottom_row.Add(pnl_enc, 1, wx.ALIGN_CENTER_VERTICAL, 0)

#		self.pnl_bottom_row = wx.Panel(self, -1)
#		self.szr_bottom_row.Add(self.pnl_bottom_row, 6, wx.GROW, 0)

		# BMI calculator button
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'bmi_calculator.png')
#		img = wx.Image(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_bmi = wx.BitmapButton (
#			parent = self,
#			id = ID_BMITOOL,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wx.NO_BORDER
#		)
#		self.btn_bmi.SetToolTip(wx.ToolTip(_("BMI Calculator")))
#		self.szr_bottom_row.Add(self.btn_bmi, 0)

#		tb = wxToolBar(self, -1, style=wx.TB_HORIZONTAL | wxNO_BORDER | wx.TB_FLAT)
#		tb.AddTool (
#			ID_BMITOOL,
#			gmImgTools.xpm2bmp(bmicalculator.get_xpm()),
#			shortHelpString = _("BMI Calculator")
#		)
#		self.szr_bottom_row.Add(tb, 0, wxRIGHT, 0)

		# pregnancy calculator button
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'preg_calculator.png')
#		img = wxImage(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_preg = wx.BitmapButton (
#			parent = self,
#			id = ID_PREGTOOL,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wxNO_BORDER
#		)
#		self.btn_preg.SetToolTip(wxToolTip(_("Pregnancy Calculator")))
#		self.szr_bottom_row.Add(self.btn_preg, 0)

		# - stack them atop each other
		self.szr_stacked_rows = wx.BoxSizer(wx.VERTICAL)
		# ??? (IMHO: space is at too much of a premium for such padding)
		# FIXME: deuglify
		try:
			self.szr_stacked_rows.Add(1, 1, 0)
		except:
			self.szr_stacked_rows.Add((1, 1), 0)

		# 0 here indicates the sizer cannot change its heights - which is intended
		self.szr_stacked_rows.Add(self.szr_top_row, 0, wx.EXPAND)
		self.szr_stacked_rows.Add(self.szr_bottom_row, 1, wx.EXPAND|wx.TOP, 5)

		# create patient picture
		self.patient_picture = gmPatPicWidgets.cPatientPicture(self, -1)
#		tt = wx.ToolTip(_('Patient picture.\nRight-click for context menu.'))
#		self.patient_picture.SetToolTip(tt)

		# create main sizer
		self.szr_main = wx.BoxSizer(wx.HORIZONTAL)
		# - insert patient picture
		self.szr_main.Add(self.patient_picture, 0, wx.LEFT | wx.TOP | wx.Right, 5)
		# - insert stacked rows
		self.szr_main.Add(self.szr_stacked_rows, 1)

		# associate ourselves with our main sizer
		self.SetSizer(self.szr_main)
		# and auto-size to minimum calculated size
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	# internal helpers
	#-------------------------------------------------------
	#-------------------------------------------------------
	# event handling
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		wx.EVT_BUTTON(self, ID_BTN_pat_demographics, self.__on_display_demographics)

#		tools_menu = self.__gb['main.toolsmenu']

		# - BMI calculator
#		wx.EVT_BUTTON(self, ID_BMITOOL, self._on_show_BMI)
#		tools_menu.Append(ID_BMIMENU, _("BMI"), _("Body Mass Index Calculator"))
#		wx.EVT_MENU(main_frame, ID_BMIMENU, self._on_show_BMI)

		# - pregnancy calculator
#		wx.EVT_BUTTON(self, ID_PREGTOOL, self._on_show_Preg_Calc)
#		tools_menu.Append(ID_PREGMENU, _("EDC"), _("Pregnancy Calculator"))
#		wx.EVT_MENU(main_frame, ID_PREGMENU, self._on_show_Preg_Calc)

		# - lock button
#		wx.EVT_BUTTON(self, ID_LOCKBUTTON, self._on_lock)
#		tools_menu.Append(ID_LOCKMENU, _("lock client"), _("locks client and hides data"))
#		wx.EVT_MENU(main_frame, ID_LOCKMENU, self._on_lock)

		wx.EVT_LEFT_DCLICK(self.txt_allergies, self._on_allergies_dclicked)

		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'allg_mod_db', receiver = self._update_allergies)
		gmDispatcher.connect(signal = u'allg_state_mod_db', receiver = self._update_allergies)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'identity_tag_mod_db', receiver = self._on_tag_change)
	#----------------------------------------------
#	def _on_lock(self, evt):
#		print "should be locking client now by obscuring data"
#		print "and popping up a modal dialog box asking for a"
#		print "password to reactivate"
	#----------------------------------------------
	def _on_allergies_dclicked(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send('statustext', msg = _('Cannot activate Allergy Manager. No active patient.'))
			return
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		dlg.ShowModal()
		return
	#----------------------------------------------
#	def _on_show_BMI(self, evt):
		# FIXME: update patient ID ?
#		bmi = gmBMIWidgets.BMI_Frame(self)
#		bmi.Centre(wx.BOTH)
#		bmi.Show(1)
	#----------------------------------------------
#	def _on_show_Preg_Calc(self, evt):
		# FIXME: update patient ID ?
#		pc = gmPregWidgets.cPregCalcFrame(self)
#		pc.Centre(wx.BOTH)
#		pc.Show(1)
	#----------------------------------------------
	def _on_tag_change(self):
		wx.CallAfter(self.__update_tags)
	#----------------------------------------------
	def _on_name_identity_change(self):
		wx.CallAfter(self.__on_name_identity_change)
	#----------------------------------------------
	def __on_name_identity_change(self):
		self.__update_age_label()
		self.Layout()
	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		# needed because GUI stuff can't be called from a thread (and that's
		# where we are coming from via backend listener -> dispatcher)
		wx.CallAfter(self.__on_post_patient_selection, **kwargs)
	#----------------------------------------------
	def __on_post_patient_selection(self, **kwargs):
		self.__update_age_label()
		self.__update_allergies()
		self.__update_tags()
		self.Layout()
	#-------------------------------------------------------
	def __on_display_demographics(self, evt):
		print "display patient demographic window now"
	#-------------------------------------------------------
	def _update_allergies(self, **kwargs):
		wx.CallAfter(self.__update_allergies)
	#-------------------------------------------------------
	# internal API
	#-------------------------------------------------------
	def __update_tags(self):
		self._PNL_tags.refresh(patient = self.curr_pat)
	#-------------------------------------------------------
	def __update_age_label(self):

		if self.curr_pat['deceased'] is None:

			if self.curr_pat.get_formatted_dob(format = '%m-%d') == pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone).strftime('%m-%d'):
				template = _('%s  %s (%s today !)')
			else:
				template = u'%s  %s (%s)'

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

			template = u'%s  %s - %s (%s)'
			age = template % (
				gmPerson.map_gender2symbol[self.curr_pat['gender']],
				self.curr_pat.get_formatted_dob(format = '%d.%b %Y', encoding = gmI18N.get_encoding()),
				self.curr_pat['deceased'].strftime('%d.%b %Y').decode(gmI18N.get_encoding()),
				self.curr_pat['medical_age']
			)

		self.lbl_age.SetLabel(age)
	#-------------------------------------------------------
	def __update_allergies(self, **kwargs):

		emr = self.curr_pat.get_emr()
		state = emr.allergy_state

		# state in tooltip
		if state['last_confirmed'] is None:
			confirmed = _('never')
		else:
			confirmed = state['last_confirmed'].strftime('%Y %B %d').decode(gmI18N.get_encoding())
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

		self.txt_allergies.SetValue(tmp)
		self.txt_allergies.SetToolTipString(tt)
	#-------------------------------------------------------
	# remote layout handling
	#-------------------------------------------------------
	def AddWidgetRightBottom (self, widget):
		"""Insert a widget on the right-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Add(widget, 0, wx.RIGHT, 0)
	#-------------------------------------------------------
	def AddWidgetLeftBottom (self, widget):
		"""Insert a widget on the left-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Prepend(widget, 0, wx.ALL, 0)
	#-------------------------------------------------------
#	def CreateBar(self):
#		"""Creates empty toolbar suited for adding to top panel."""
#		bar = wx.ToolBar (
#			self.pnl_bottom_row,
#			-1,
#			size = self.pnl_bottom_row.GetClientSize(),
#			style = wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT
#		)
#		return bar
	#-------------------------------------------------------
#	def AddBar(self, key=None, bar=None):
#		"""Creates and returns a new empty toolbar, referenced by key.
#
#		Key should correspond to the notebook page number as defined
#		by the notebook (see gmPlugin.py), so that gmGuiMain can
#		display the toolbar with the notebook
#		"""
#		bar.SetToolBitmapSize((16,16))
#		self.subbars[key] = bar
#		if len(self.subbars) == 1:
#			bar.Show(1)
#			self.__current = key
#		else:
#			bar.Hide()
#		return True
	#-------------------------------------------------------
#	def ReFit (self):
#		"""Refits the toolbar after its been changed
#		"""
#		tw = 0
#		th = 0
#		# get maximum size for the toolbar
#		for i in self.subbars.values ():
#			ntw, nth = i.GetSizeTuple ()
#			if ntw > tw:
#				tw = ntw
#			if nth > th:
#				th = nth
#		#import pdb
#		#pdb.set_trace ()
#		sz = wx.Size (tw, th)
#		self.pnl_bottom_row.SetSize(sz)
#		for i in self.subbars.values():
#			i.SetSize (sz)
#		self.szr_main.Layout()
#		self.szr_main.Fit(self)
	#-------------------------------------------------------
#	def ShowBar (self, key):
#		"""Displays the named toolbar.
#		"""
#		self.subbars[self.__current].Hide()
#		try:
#			self.subbars[key].Show(1)
#			self.__current = key
#		except KeyError:
#			_log.exception("cannot show undefined toolbar [%s]" % key)
	#-------------------------------------------------------
#	def DeleteBar (self, key):
#		"""Removes a toolbar.
#		"""
#		try:
#			self.subbars[key].Destroy()
#			del self.subbars[key]
#			# FIXME: ??
#			if self.__current == key and len(self.subbars):
#				self.__current = self.subbars.keys()[0]
#				self.subbars[self.__current].Show(1)
#		except KeyError:
#			_log.exception("cannot delete undefined toolbar [%s]" % key)

#===========================================================	
if __name__ == "__main__":
	wx.InitAllImageHandlers()
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.MainLoop()
#===========================================================
