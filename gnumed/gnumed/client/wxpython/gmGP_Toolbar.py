# GnuMed
# GPL

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmGP_Toolbar.py,v $
__version__ = "$Revision: 1.13 $"
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>"
#===========================================================
import sys, os.path, cPickle, zlib
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

import gmLog, gmGuiBroker
import gmGP_PatientPicture, gmPatientSelector

from wxPython.wx import *

ID_BTN_pat_demographics = wxNewId()

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

		gb = gmGuiBroker.GuiBroker ()
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER)
		self.SetBackgroundColour(bg_col)

		# layout:
		# .--------------------------------.
		# | patient | toolbar              |
		# | picture |----------------------|
		# |         | toolbar              |
		# `--------------------------------'

		# create toolbars
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
			style = wxBU_AUTODRAW
		)
		self.btn_pat_demographics.SetToolTip(wxToolTip(_("display patient demographics")))
		self.szr_top_row.Add (self.btn_pat_demographics, 0, wxEXPAND)
		EVT_BUTTON(self, ID_BTN_pat_demographics, self.__on_display_demographics)

#		self.tool_patient_search = self.tb_patient_search.AddTool (
#			ID_BUTTONFINDPATIENT,
#			getToolbar_FindPatientBitmap(),
#			shortHelpString = _("Patient Details")
#		)
#		EVT_TOOL (self.tb_patient_search, ID_BUTTONFINDPATIENT, self.OnTool)

		#  - patient selector
		self.patient_selector = gmPatientSelector.cPatientSelector(self, -1)
		self.patient_selector.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		self.szr_top_row.Add (self.patient_selector, 5, wxEXPAND, 3)
		#  - age
		self.lbl_age = wxStaticText (self, -1, _("Age"), style = wxALIGN_CENTER_VERTICAL)
		self.lbl_age.SetFont (wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,''))
#		self.lbl_age.SetForegroundColour (fg_col)
		self.txt_age = wxTextCtrl (self, -1, "", size = (40,-1), style = wxTE_READONLY)
		self.txt_age.SetFont (wxFont(12, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		self.txt_age.SetBackgroundColour(bg_col)
		self.szr_top_row.Add (self.lbl_age, 0, wxEXPAND | wxALIGN_CENTER_VERTICAL | wxALL, 3)
		self.szr_top_row.Add (self.txt_age, 0, wxEXPAND | wxALL, 3)
		#  - allergies
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

		# - stack them atop each other
		self.szr_toolbars = wxBoxSizer(wxVERTICAL)
		self.szr_toolbars.Add(1, 3, 0, wxEXPAND)	# ??? (IMHO: space is at too much of a premium for such padding)
		self.szr_toolbars.Add(self.szr_top_row, 1, wxEXPAND)
		self.szr_toolbars.Add(self.szr_bottom_row, 1, wxEXPAND | wxALL, 2)

		# create patient picture
		self.patient_picture = gmGP_PatientPicture.cPatientPicture(self, -1)
		gb['main.patient_picture'] = self.patient_picture

		# create main sizer
		self.szr_main = wxBoxSizer(wxHORIZONTAL)
		# - insert patient picture
		self.szr_main.Add(self.patient_picture, 0, wxEXPAND)
		# - insert stacked toolbars
		self.szr_main.Add(self.szr_toolbars, 1, wxEXPAND)

		# init toolbars dict
		self.subbars = {}

		self.SetSizer(self.szr_main)	#set the sizer
		self.szr_main.Fit(self)			#set to minimum size as calculated by sizer
		self.SetAutoLayout(true)		#tell frame to use the sizer
		self.Show(true)
	#-------------------------------------------------------
	# event handlers
	#-------------------------------------------------------
	def __on_display_demographics(self, evt):
		print "display patient demographic window now"
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
	def AddWidgetTopLine (self, widget, proportion = 0, flag = wxEXPAND, border = 0):
		"""Inserts a widget onto the top line.
		"""
		self.szr_top_row.Add(widget, proportion, flag, border)
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
			gmLog.gmDefLog.LogException("cannot show undefined toolbar [%s]" % key, sys.exc_info(), fatal=0)
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
			gmLog.gmDefLog.LogException("cannot delete undefined toolbar [%s]" % key, sys.exc_info(), fatal=0)

#===========================================================	
if __name__ == "__main__":
	gb = gmGuiBroker.GuiBroker ()
	gb['gnumed_dir'] = '..'
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.MainLoop()
#===========================================================
# $Log: gmGP_Toolbar.py,v $
# Revision 1.13  2003-04-04 20:43:01  ncq
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
