#====================================================================
# GnuMed
# GPL
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/Attic/gmEditAreaTemplate.py,v $
# $Id: gmEditAreaTemplate.py,v 1.1 2003-10-09 23:50:09 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "R.Terry, K.Hilbert"

# TODO: standard SOAP edit area
#====================================================================
import sys, traceback

#if __name__ == "__main__":
sys.path.append ("../python-common/")
sys.path.append ("../../client/python-common/")
sys.path.append ("../../client/wxpython/")
sys.path.append ("../../client/business")

import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	import gmI18N

import gmExceptions, gmDateTimeInput, TestEvents

from wxPython.wx import *

ID_PROGRESSNOTES = wxNewId()
gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_VACCINATION = 6
gmSECTION_SCRIPT = 8

#--------------------------------------------
gmSECTION_REQUESTS = 9
ID_REQUEST_TYPE = wxNewId()
ID_REQUEST_COMPANY  = wxNewId()
ID_REQUEST_STREET  = wxNewId()
ID_REQUEST_SUBURB  = wxNewId()
ID_REQUEST_PHONE  = wxNewId()
ID_REQUEST_REQUESTS  = wxNewId()
ID_REQUEST_FORMNOTES = wxNewId()
ID_REQUEST_MEDICATIONS = wxNewId()
ID_REQUEST_INCLUDEALLMEDICATIONS  = wxNewId()
ID_REQUEST_COPYTO = wxNewId()
ID_REQUEST_BILL_BB = wxNewId()
ID_REQUEST_BILL_PRIVATE = wxNewId()
ID_REQUEST_BILL_wcover = wxNewId()
ID_REQUEST_BILL_REBATE  = wxNewId()
#---------------------------------------------
gmSECTION_MEASUREMENTS = 10
ID_MEASUREMENT_TYPE = wxNewId()
ID_MEASUREMENT_VALUE = wxNewId()
ID_MEASUREMENT_DATE = wxNewId()
ID_MEASUREMENT_COMMENT = wxNewId()
ID_MEASUREMENT_NEXTVALUE = wxNewId()
ID_MEASUREMENT_GRAPH   = wxNewId()
#---------------------------------------------
gmSECTION_REFERRALS = 11
ID_REFERRAL_CATEGORY        = wxNewId()
ID_REFERRAL_NAME        = wxNewId()
ID_REFERRAL_USEFIRSTNAME        = wxNewId()
ID_REFERRAL_ORGANISATION        = wxNewId()
ID_REFERRAL_HEADOFFICE        = wxNewId()
ID_REFERRAL_STREET1       = wxNewId()
ID_REFERRAL_STREET2        = wxNewId()
ID_REFERRAL_STREET3       = wxNewId()
ID_REFERRAL_SUBURB        = wxNewId()
ID_REFERRAL_POSTCODE        = wxNewId()
ID_REFERRAL_FOR        = wxNewId()
ID_REFERRAL_WPHONE        = wxNewId()
ID_REFERRAL_WFAX        = wxNewId()
ID_REFERRAL_WEMAIL        = wxNewId()
ID_REFERRAL_INCLUDE_MEDICATIONS        = wxNewId()
ID_REFERRAL_INCLUDE_SOCIALHISTORY       = wxNewId()
ID_REFERRAL_INCLUDE_FAMILYHISTORY        = wxNewId()
ID_REFERRAL_INCLUDE_PASTPROBLEMS        = wxNewId()
ID_REFERRAL_ACTIVEPROBLEMS       = wxNewId()
ID_REFERRAL_HABITS        = wxNewId()
ID_REFERRAL_INCLUDEALL        = wxNewId()
ID_BTN_PREVIEW = wxNewId()
ID_BTN_CLEAR = wxNewId()
ID_REFERRAL_COPYTO = wxNewId()
#----------------------------------------
gmSECTION_RECALLS = 12
ID_RECALLS_TOSEE  = wxNewId()
ID_RECALLS_TXT_FOR  = wxNewId()
ID_RECALLS_TXT_DATEDUE  = wxNewId()
ID_RECALLS_CONTACTMETHOD = wxNewId()
ID_RECALLS_APPNTLENGTH = wxNewId()
ID_RECALLS_TXT_ADDTEXT  = wxNewId()
ID_RECALLS_TXT_INCLUDEFORMS = wxNewId()
ID_RECALLS_TOSEE  = wxNewId()
ID_RECALLS_TXT_FOR  = wxNewId()
ID_RECALLS_TXT_DATEDUE  = wxNewId()
ID_RECALLS_CONTACTMETHOD = wxNewId()
ID_RECALLS_APPNTLENGTH = wxNewId()
ID_RECALLS_TXT_ADDTEXT  = wxNewId()
ID_RECALLS_TXT_INCLUDEFORMS = wxNewId()



PHX_CONDITION=wxNewId()
PHX_NOTES=wxNewId()
PHX_NOTES2=wxNewId()
PHX_LEFT=wxNewId()
PHX_RIGHT=wxNewId()
PHX_BOTH=wxNewId()
PHX_AGE=wxNewId()
PHX_YEAR=wxNewId()
PHX_ACTIVE=wxNewId()
PHX_OPERATION=wxNewId()
PHX_CONFIDENTIAL=wxNewId()
PHX_SIGNIFICANT=wxNewId()
PHX_PROGRESSNOTES=wxNewId()


richards_blue = wxColour(0,0,131)
richards_aqua = wxColour(0,194,197)
richards_dark_gray = wxColor(131,129,131)
richards_light_gray = wxColor(255,255,255)
richards_coloured_gray = wxColor(131,129,131)


class gmEditAreaLayoutManager:

	def __init__(self):
		pass
	
	def layout( self, panel, widgetConfigLines ):
		# make prompts
		#szr_prompts = self.__make_prompts(_prompt_defs[self._type])
		leftSide = []
		rightSide = []
		for line in widgetConfigLines:
			leftSide.append([line[0]])
			rightSide.append(line[1:])
			

		szr_prompts = self.makePrompts(panel, leftSide)
		# make editing area
		self.szr_editing_area = self.__make_editing_area(panel, rightSide)

		maxTextWidgetPerLine = 0
		for l in rightSide:
			textCount = self.factory.getTextWidgetCount(l)
			if textCount > maxTextWidgetPerLine:
				maxTextWidgetPerLine = textCount

		# stack prompts and fields horizontally
		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 1, wxEXPAND)
		self.szr_main_panels.Add(5, 0, 0, wxEXPAND)
		self.szr_main_panels.Add(self.szr_editing_area, 2 + 8 / maxTextWidgetPerLine, wxEXPAND) #weight is relative to other panels in sizer

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)
		return self.szr_central_container

		#return self.szr_main_panels



	def _make_prompt(self, parent, aLabel, aColor):
		# FIXME: style for centering in vertical direction ?
		prompt = wxStaticText(
			parent,
			-1,
			aLabel,
			wxDefaultPosition,
			wxDefaultSize,
			wxALIGN_RIGHT #| wxST_NO_AUTORESIZE
		)
		prompt.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		prompt.SetForegroundColour(aColor)
		return prompt
	#----------------------------------------------------------------
	def make_prompts(self,prompt_pnl,  prompt_labels):
		list = []
		for prompt in prompt_labels:
			label = self._make_prompt(prompt_pnl, "%s " % prompt, color)
			list.append(label)
		
		return self.makePrompts(prompt_pnl, list)

	def setFactory(self, factory):
		self.factory = factory

		
	def  makePrompts( self,parent, widgetDef):
		# prompts live on a panel
		prompt_pnl = wxPanel(parent, -1, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		gszr =wxBoxSizer(wxVERTICAL) #wxFlexGridSizer(0, 1, 0, 0) 
		#gszr.AddGrowableCol(0)
		color = richards_aqua
		for [defn] in widgetDef:
			prompt = self.factory.createWidget( prompt_pnl, defn)
			gszr.Add(prompt, 1, wxEXPAND | wxALIGN_RIGHT)
			prompt.SetForegroundColour(color)
			color = richards_blue
		# put sizer on panel
		prompt_pnl.SetSizer(gszr)
		gszr.Fit(prompt_pnl)
		prompt_pnl.SetAutoLayout(true)

		return self.lookAndFeel(parent, prompt_pnl)
	

	def lookAndFeel(self, parent, prompt_pnl):
		# make shadow below prompts in gray
		shadow_below_prompts = wxWindow(parent, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_below_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_below_prompts = wxBoxSizer (wxHORIZONTAL)
		szr_shadow_below_prompts.Add(10, 0, 0, wxEXPAND)
		szr_shadow_below_prompts.Add(shadow_below_prompts, 1, wxEXPAND)

		# stack prompt panel and shadow vertically
		vszr_prompts = wxBoxSizer(wxVERTICAL)
		vszr_prompts.Add(prompt_pnl, 2, wxEXPAND | wxALL)
		vszr_prompts.Add(szr_shadow_below_prompts, 0, wxEXPAND)

		# make shadow to the right of the prompts
		shadow_rightof_prompts = wxWindow(parent, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_rightof_prompts = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_prompts.Add(0,15,0,wxEXPAND)
		szr_shadow_rightof_prompts.Add(shadow_rightof_prompts,1,wxEXPAND)

		# stack vertical prompt sizer and shadow horizontally
		hszr_prompts = wxBoxSizer(wxHORIZONTAL)
		hszr_prompts.Add(vszr_prompts, 3, wxEXPAND)
		hszr_prompts.Add(szr_shadow_rightof_prompts, 0, wxEXPAND)

		return hszr_prompts
		
	#----------------------------------------------------------------
	def _make_edit_lines(self, parent, defLines):
		lines = []
		
		for l in defLines:
			lineSizer = wxBoxSizer(wxHORIZONTAL)
			for defn in l:
				widget = self.factory.createWidget(parent, defn)
				( propName, type, weight,displayName, newline, constrained) = defn
				lineSizer.Add(widget, weight , wxALIGN_RIGHT | wxEXPAND)
			lines.append(lineSizer)	
		return lines	
				
		if self.lineProducer <> None:
			return self.lineProducer.getLines()
		_log.Log(gmLog.lErr, 'programmer forgot to define edit area lines for [%s]' % self._type)
		_log.Log(gmLog.lInfo, 'child classes of gmEditArea *must* override this function')
		return []
	#----------------------------------------------------------------
	def __make_editing_area(self, parent, widgetDefs):
		# make edit fields
		fields_pnl = wxPanel(parent, -1, wxDefaultPosition, wxDefaultSize, style = wxRAISED_BORDER | wxTAB_TRAVERSAL)
		fields_pnl.SetBackgroundColour(wxColor(222,222,222))
		# rows, cols, hgap, vgap
		gszr = wxGridSizer(len(widgetDefs), 1, 0, 0)
		#gszr = wxFlexGridSizer( 0, 1, 0, 0)
		#gszr.AddGrowableCol(0)
		#gszr = wxBoxSizer(wxVERTICAL)
		# get lines
		lines = self._make_edit_lines( fields_pnl, widgetDefs)
		self.lines = lines
		for line in lines:
			gszr.Add(line, 8, wxEXPAND | wxALIGN_LEFT, 5 )
		# put them on the panel
		fields_pnl.SetSizer(gszr)
		gszr.Fit(fields_pnl)
		fields_pnl.SetAutoLayout(true)
		return self.lookAndFeel( parent, fields_pnl)


