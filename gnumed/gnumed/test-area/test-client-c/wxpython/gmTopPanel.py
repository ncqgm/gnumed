# GnuMed
# GPL

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/wxpython/Attic/gmTopPanel.py,v $
__version__ = "$Revision: 1.2 $"
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
#===========================================================
import sys, os.path, cPickle, zlib, string
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

import gmLog, gmGuiBroker, gmGP_PatientPicture, gmPatientSelector, gmDispatcher, gmSignals, gmPatient, gmPG, gmGuiHelpers
_log = gmLog.gmDefLog

from wxPython.wx import *

ID_BTN_pat_demographics = wxNewId()
ID_CBOX_consult_type = wxNewId()

# FIXME: need a better name here !
bg_col = wxColour(214,214,214)
fg_col = wxColour(0,0,131)
col_brightred = wxColour(255,0,0)
#===========================================================
class cMainTopPanel(wxPanel):

	__icons = {
"""icon_binoculars_form""": 'x\xdam\x8e\xb1\n\xc4 \x0c\x86\xf7>\x85p\x83\x07\x01\xb9.\xa7\xb3\x16W\x87.]\
K\xc7+x\xef?]L\xa2\xb5r!D\xbe\x9f/\xc1\xe7\xf9\x9d\xa7U\xcfo\x85\x8dCO\xfb\
\xaaA\x1d\xca\x9f\xfb\xf1!RH\x8f\x17\x96u\xc4\xa9\xb0u6\x08\x9b\xc2\x8b[\xc2\
\xc2\x9c\x0bG\x17Cd\xde\n{\xe7\x83wr\xef*\x83\xc5\xe1\xa6Z_\xe1_3\xb7\xea\
\xc3\x94\xa4\x07\x13\x00h\xdcL\xc8\x90\x12\x8e\xd1\xa4\xeaM\xa0\x94\xf7\x9bI\
\x92\xa8\xf5\x9f$\x19\xd69\xc43rp\x08\xb3\xac\xe7!4\xf5\xed\xd7M}kx+\x0c\xcd\
\x0fE\x94aS'
}

	def __init__(self, parent, id):

		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER)

		self.__load_consultation_types()
		self.__do_layout()
		del self.__consultation_types
		self.__register_interests()

		# init plugin toolbars dict
		self.subbars = {}
		self.curr_pat = gmPatient.gmCurrentPatient()

		# and actually display ourselves
		self.SetAutoLayout(true)
		self.Show(true)
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
		# .--------------------------------------.
		# | details | patient  | age | allergies |
		# | button  | selector |     |           |
		# `--------------------------------------'
		self.szr_top_row = wxBoxSizer (wxHORIZONTAL)

		#  - details button
		bmp = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(self.__icons[_("icon_binoculars_form")])))
		self.btn_pat_demographics = wxBitmapButton (
			parent = self,
			id = ID_BTN_pat_demographics,
			bitmap = bmp,
			style = wxBU_EXACTFIT | wxNO_BORDER
		)
		self.btn_pat_demographics.SetToolTip(wxToolTip(_("display patient demographics")))
		self.szr_top_row.Add (self.btn_pat_demographics, 0, wxEXPAND)

		#  - patient selector
		self.patient_selector = gmPatientSelector.cPatientSelector(self, -1)
		self.patient_selector.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		self.szr_top_row.Add (self.patient_selector, 5, wxEXPAND, 3)
		#  - age
		self.lbl_age = wxStaticText (self, -1, _("Age"), style = wxALIGN_CENTER_VERTICAL)
		self.lbl_age.SetFont (wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,''))
		self.txt_age = wxTextCtrl (self, -1, "", size = (40,-1), style = wxTE_READONLY)
		self.txt_age.SetFont (wxFont(12, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		self.txt_age.SetBackgroundColour(bg_col)
		self.szr_top_row.Add (self.lbl_age, 0, wxEXPAND | wxALIGN_CENTER_VERTICAL | wxALL, 3)
		self.szr_top_row.Add (self.txt_age, 0, wxEXPAND | wxALL, 3)
		#  - allergies (substances only, like "makrolides, penicillins, eggs")
		self.lbl_allergies = wxStaticText (self, -1, _("Allergies"), style = wxALIGN_CENTER_VERTICAL)
		self.lbl_allergies.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,''))
		self.lbl_allergies.SetBackgroundColour(bg_col)
		self.lbl_allergies.SetForegroundColour(col_brightred)
		self.txt_allergies = wxTextCtrl (self, -1, "", style = wxTE_READONLY)
		self.txt_allergies.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
		self.txt_allergies.SetBackgroundColour(bg_col)
		self.txt_allergies.SetForegroundColour (col_brightred)
		self.szr_top_row.Add (self.lbl_allergies, 0, wxEXPAND | wxALIGN_CENTER_VERTICAL | wxALL, 3)
		self.szr_top_row.Add (self.txt_allergies, 6, wxEXPAND | wxALL, 3)

		# - bottom row
		# (holds most of the buttons)
		self.szr_bottom_row = wxBoxSizer (wxHORIZONTAL)
		self.pnl_bottom_row = wxPanel(self, -1)
		self.szr_bottom_row.Add (self.pnl_bottom_row, 1, wxGROW)
		# consultation type selector
		self.combo_consultation_type = wxComboBox (
			self,
			ID_CBOX_consult_type,
			self.DEF_CONSULT_TYPE,
			wxDefaultPosition,
			wxDefaultSize,
			self.__consultation_types,
			wxCB_DROPDOWN
		)
		self.szr_bottom_row.Add(self.combo_consultation_type, 0, wxRIGHT, 0)

		# - stack them atop each other
		self.szr_stacked_rows = wxBoxSizer(wxVERTICAL)
		self.szr_stacked_rows.Add(1, 3, 0, wxEXPAND)	# ??? (IMHO: space is at too much of a premium for such padding)
		self.szr_stacked_rows.Add(self.szr_top_row, 1, wxEXPAND)
		self.szr_stacked_rows.Add(self.szr_bottom_row, 1, wxEXPAND | wxALL, 2)

		# create patient picture
		self.patient_picture = gmGP_PatientPicture.cPatientPicture(self, -1)
		gb = gmGuiBroker.GuiBroker()
		gb['main.patient_picture'] = self.patient_picture

		# create main sizer
		self.szr_main = wxBoxSizer(wxHORIZONTAL)
		# - insert patient picture
		self.szr_main.Add(self.patient_picture, 0, wxEXPAND)
		# - insert stacked rows
		self.szr_main.Add(self.szr_stacked_rows, 1, wxEXPAND)

		# associate ourselves with our main sizer
		self.SetSizer(self.szr_main)
		# and auto-size to minimum calculated size
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	# internal helpers
	#-------------------------------------------------------
	def __load_consultation_types(self):
		dbpool = gmPG.ConnectionPool()
		conn = dbpool.GetConnection(service = 'historica')
		rocurs = conn.cursor()
		cmd = "SELECT description from v_i18n_enum_encounter_type;"
		if not gmPG.run_query(rocurs, cmd):
			rocurs.close()
			dbpool.ReleaseConnection('historica')
			_log.Log(gmLog.lWarn, 'cannot load consultation types from backend')
			self.__consultation_types = [_('in surgery')]
			self.DEF_CONSULT_TYPE = self.__consultation_types[0]
			gmGuiHelpers.gm_show_error (
				_('Cannot load consultation types from backend.\nConsequently, the only available type is:\n[%s]') % self.__consultation_types[0],
				_('loading consultation types'),
				gmLog.lWarn
			)
			return None
		result = rocurs.fetchall()
		rocurs.close()
		dbpool.ReleaseConnection('historica')
		if len(result) == 0:
			self.__consultation_types = [_('in surgery')]
			self.DEF_CONSULT_TYPE = self.__consultation_types[0]
			gmGuiHelpers.gm_show_error (
				_('Cannot load consultation types from backend.\nConsequently, the only available type is:\n[%s]') % self.__consultation_types[0],
				_('loading consultation types'),
				gmLog.lWarn
			)
			return None
		self.__consultation_types = []
		for cons_type in result:
			self.__consultation_types.append(cons_type[0])
		self.DEF_CONSULT_TYPE = self.__consultation_types[0]
		return 1
	#-------------------------------------------------------
	# event handling
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		EVT_BUTTON(self, ID_BTN_pat_demographics, self.__on_display_demographics)
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
		gmDispatcher.connect(signal=gmSignals.allergy_updated(), receiver=self._update_allergies)
	#----------------------------------------------
	def _on_patient_selected(self, **kwargs):
		age = self.curr_pat['demographics'].getMedicalAge ()
		# FIXME: if the age is below, say, 2 hours we should fire
		# a timer here that updates the age in increments of 1 minute ... :-)
		name = self.curr_pat['demographics'].getActiveName()
		self.txt_age.SetValue(age)
		self.patient_selector.SetValue('%s, %s' % (name['last'], name['first']))
		self._update_allergies()
	#-------------------------------------------------------
	def __on_display_demographics(self, evt):
		print "display patient demographic window now"
	#-------------------------------------------------------
	def _update_allergies(self, **kwargs):
		epr = self.curr_pat['clinical record']
		allergy_names = epr['allergy names']
		_log.Log(gmLog.lData, "allergy names: %s" % allergy_names)
		tmp = []
		for allergy in allergy_names:
			tmp.append(allergy['name'])
		data = string.join(tmp, ',')
		if data == '':
			# needed because GUI stuff can't be called from a thread (and that's
			# where we are coming from via backend listener -> dispatcher)
			wxCallAfter(self.txt_allergies.SetValue, _('no allergies recorded'))
		else:
			wxCallAfter(self.txt_allergies.SetValue, data)
	#-------------------------------------------------------
	# remote layout handling
	#-------------------------------------------------------
	def AddWidgetRightBottom (self, widget):
		"""Insert a widget on the right-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Add(widget, 0, wxRIGHT, 0)
	#-------------------------------------------------------
	def AddWidgetLeftBottom (self, widget):
		"""Insert a widget on the left-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Prepend(widget, 0, wxALL, 0)
	#-------------------------------------------------------
	def AddBar (self, key):
		"""Creates and returns a new empty toolbar, referenced by key.

		Key should correspond to the notebook page number as defined
		by the notebook (see gmPlugin.py), so that gmGuiMain can
		display the toolbar with the notebook
		"""
		self.subbars[key] = wxToolBar (
			self.pnl_bottom_row,
			-1,
			size = self.pnl_bottom_row.GetClientSize(),
			style=wxTB_HORIZONTAL | wxNO_BORDER | wxTB_FLAT
		)

		self.subbars[key].SetToolBitmapSize((16,16))
		if len(self.subbars) == 1:
			self.subbars[key].Show(1)
			self.__current = key
		else:
			self.subbars[key].Hide()
		return self.subbars[key]
	#-------------------------------------------------------
	def ReFit (self):
		"""Refits the toolbar after its been changed
		"""
		tw = 0
		th = 0
		# get maximum size for the toolbar
		for i in self.subbars.values ():
			ntw, nth = i.GetSizeTuple ()
			if ntw > tw:
				tw = ntw
			if nth > th:
				th = nth
		#import pdb
		#pdb.set_trace ()
		sz = wxSize (tw, th)
		self.pnl_bottom_row.SetSize(sz)
		for i in self.subbars.values():
			i.SetSize (sz)
		self.szr_main.Layout()
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	def ShowBar (self, key):
		"""Displays the named toolbar.
		"""
		self.subbars[self.__current].Hide()
		try:
			self.subbars[key].Show(1)
			self.__current = key
		except KeyError:
			gmLog.gmDefLog.LogException("cannot show undefined toolbar [%s]" % key, sys.exc_info(), verbose=1)
	#-------------------------------------------------------
	def DeleteBar (self, key):
		"""Removes a toolbar.
		"""
		try:
			self.subbars[key].Destroy()
			del self.subbars[key]
			# FIXME: ??
			if self.__current == key and len(self.subbars):
				self.__current = self.subbars.keys()[0]
				self.subbars[self.__current].Show(1)
		except KeyError:
			gmLog.gmDefLog.LogException("cannot delete undefined toolbar [%s]" % key, sys.exc_info(), verbose=1)

#===========================================================	
if __name__ == "__main__":
	gb = gmGuiBroker.GuiBroker ()
	gb['gnumed_dir'] = '..'
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.MainLoop()
#===========================================================
# $Log: gmTopPanel.py,v $
# Revision 1.2  2003-10-27 14:01:26  sjtan
#
# syncing with main tree.
#
# Revision 1.19  2003/10/26 18:04:01  ncq
# - cleanup
#
# Revision 1.18  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.17  2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.16  2003/10/19 12:20:10  ncq
# - use GuiHelpers.py
#
# Revision 1.15  2003/07/07 08:34:31  ihaywood
# bugfixes on gmdrugs.sql for postgres 7.3
#
# Revision 1.14  2003/06/26 21:40:29  ncq
# - fatal->verbose
#
# Revision 1.13  2003/06/26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.12  2003/06/01 12:31:58  ncq
# - logging data is not by any means lInfo
#
# Revision 1.11  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.10  2003/05/05 00:21:00  ncq
# - make work with encounter types translation
#
# Revision 1.9  2003/05/05 00:00:21  ncq
# - do load encounter types again
#
# Revision 1.8  2003/05/04 23:33:56  ncq
# - comments bettered
#
# Revision 1.7  2003/05/03 14:18:06  ncq
# - must use wxCallAfter in _update_allergies since this can be called
#   indirectly from a thread listening to backend signals and one cannot use
#   wx GUI functions from Python threads other than main()
#
# Revision 1.6  2003/05/03 00:43:14  ncq
# - properly set allergies field on patient change
# - hot update of allergies in DB needs testing
#
# Revision 1.5  2003/05/01 15:04:10  ncq
# - connect allergies field to backend (need to filter out sensitivities, though)
# - update allergies on patient selection
# - listen to allergy change signal
#
# Revision 1.4  2003/04/28 12:05:21  ncq
# - use plugin.internal_name(), cleaner logging
#
# Revision 1.3  2003/04/25 13:37:22  ncq
# - moved combo box "consultation type" here from gmDemographics (still needs to be placed right-most)
# - helper __show_error()
# - connected "consultation type" to backend
#
# Revision 1.2  2003/04/19 15:00:30  ncq
# - display age, finally
#
# Revision 1.1  2003/04/08 21:24:14  ncq
# - renamed gmGP_Toolbar -> gmTopPanel
#
# Revision 1.13  2003/04/04 20:43:01  ncq
# - install new patient search widget
# - rework to be a more invariant top pane less dependant on gmDemographics
# - file should be renamed to gmTopPane.py
#
# Revision 1.12  2003/03/29 18:26:04  ncq
# - allow proportion/flag/border in AddWidgetTopLine()
#
# Revision 1.11  2003/03/29 13:46:44  ncq
# - make standalone work, cure sizerom
# - general cleanup, comment, clarify
#
# Revision 1.10  2003/01/12 00:24:02  ncq
# - CVS keywords
#
