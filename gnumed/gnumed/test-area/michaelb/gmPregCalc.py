#!/usr/bin/env python
#====================================================================
# GnuMed tool to calculate expected date of delivery
# licence: GPL
# Changelog:
# 11/7/02: inital version
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/michaelb/Attic/gmPregCalc.py,v $
# $Id: gmPregCalc.py,v 1.3 2003-07-04 14:48:23 michaelb Exp $
# Michael I have cut and pasted all my code - hope doesn't stuff up your stuff
__version__ = "$Revision: 1.3 $"
__author__ = "M. Bonert, R. Terry, I. Haywood"

from wxPython.wx import *
from wxPython.calendar import *
from wxPython.lib.rcsizer import RowColSizer
import math, zlib, cPickle
import random

ID_LNMP = wxNewId ()
ID_DUE = wxNewId ()
ID_DAY = wxNewId ()
ID_WEEK = wxNewId ()
ID_MENU = wxNewId ()

# Naegele's rule is easy for manual calculation, but a pain to code
# Enter Haywood's rule ;-), human gestation is defined as 24192000 seconds.
GESTATION = 24192000
# ideally, tool should query backend for parity, race, etc. for exact measurement
WEEK = 604800
DAY = 86400
US18_52=18*7*24*60*60	# 18 weeks in seconds (for 18/52 Ultrasound)
#====================================================================

_icons = {"""icon_Preg_calc""":
'x\xdaMP1\x0e\x830\x0c\xdcy\x85\xa5\x0et\xb2`h\x95\xb9H\xac\x0c,^\x11c\x91\
\xdc\xffO\xbd\xb3C\xc0\xb1\x02w\xf1]\xec<\x8f\xdf\xd8\xad\xfd\xf8\x16\xe4K\
\xc6\xbe\xdb\xd6\xded\x97\xcf\xb1\xed\xdf@\x0e\xf4\x98\x06\xae\xc0J\\\x06\
\xae\xc0B<\x97y\x9aK\xe0%\xf1\x80\xc8sU5\xb5H\x84T\x13A:"~\xb4\x92\x0e\x8aE\
\xa0],I%\'\xac\x03\xab\xad\x92%u\xabr\xa3\x15\x85Hx\xa6\xdc<]%X\xafr\xcf\xd0\
\xdcje\xa8\xa3\x94\xfaS\xeeI\xe4mv\xde\xae\xd9\xd2\x02\xcb[\xf3\x9ar\xf56Q\
\xb0\x11\xe4\xeec\xfa\xe9\x9c$\xa7`\x03No|\xda\xd3]\xe1|:\xfd\x03\xab\xf8h\
\xbf' }

class PregnancyFrame (wxFrame):
	"""
	A pregnancy calculator.
	"""

	def __init__ (self, parent):
		myStyle = wxMINIMIZE_BOX | wxSYSTEM_MENU | wxCAPTION | wxALIGN_CENTER | \
			wxALIGN_CENTER_VERTICAL | wxTAB_TRAVERSAL | wxSTAY_ON_TOP
		wxFrame.__init__(self, parent, -1, _("Pregnancy Calculator"), style=myStyle)

		icon = wxEmptyIcon()
		icon.CopyFromBitmap(wxBitmapFromXPMData(cPickle.loads(zlib.decompress( _icons[_("""icon_Preg_calc""")] ))) )
		self.SetIcon(icon)

		rcs = RowColSizer()

		#------------------------------
		# sizer holding the 'LNMP' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Lmp"),size = (50,20))                 #label Lmp
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label.SetForegroundColour(wxColour(0,0,0))

		self.txtlnmp = wxTextCtrl(self,-1,"",size=(100,20))                   # text for lmp
		self.txtlnmp.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
                szr_row1 = wxBoxSizer(wxHORIZONTAL)
		szr_row1.Add(self.txtlnmp,1,wxEXPAND|wxALL,2)
		#EVT_TEXT(self, self.txtlnmp.GetId(), self.EvtText_height)
		#EVT_SET_FOCUS(self.txtheight, self.OnSetFocus_height)
		#EVT_CHAR(self.txtheight, self.EvtChar_height)

		szr_lnmp = wxBoxSizer(wxHORIZONTAL)
		szr_lnmp.Add(label, 1, 0, 0)
		szr_lnmp.Add(10,1,0,0)
		rcs.Add(szr_lnmp, flag=wxEXPAND, row=0, col=1)
		rcs.Add(szr_row1, flag=wxEXPAND, row=0, col=2, colspan=5)
		#------------------------------
		# sizer holding the 'Gest.' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Gest."),size = (50,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label.SetForegroundColour(wxColour(0,0,0))

		self.txtgest = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtgest.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		self.txtgest_szr  = wxBoxSizer(wxHORIZONTAL)
		self.txtgest_szr.Add(self.txtgest,1,wxEXPAND|wxALL,2)
		#EVT_TEXT(self, self.txtmass.GetId(), self.EvtText_mass)
		#EVT_SET_FOCUS(self.txtmass, self.OnSetFocus_mass)
		#EVT_CHAR(self.txtmass, self.EvtChar_mass)

		szr_gest = wxBoxSizer(wxHORIZONTAL)
		szr_gest.Add(label, 1, 0, 0)
		szr_gest.Add(10,1,0,0)
		rcs.Add(szr_gest, flag=wxEXPAND, row=1, col=1)
		rcs.Add(self.txtgest_szr, flag=wxEXPAND, row=1, col=2, colspan=5)

		#------------------------------
		# sizer holding the 'EDC' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Edc"),size = (50,20))
		label.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label.SetForegroundColour(wxColour(0,0,0))
		
  		self.txtedc = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtedc.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		szr_txtedc = wxBoxSizer(wxHORIZONTAL)
		szr_txtedc.Add(self.txtedc,1,wxEXPAND|wxALL,2)
		szr_edc = wxBoxSizer(wxHORIZONTAL)
		szr_edc.Add(label,1,0,0)
		szr_edc.Add(10,1,0,0)
		rcs.Add(szr_edc, flag=wxEXPAND, row=2, col=1)
		rcs.Add(szr_txtedc, flag=wxEXPAND, row=2, col=2, colspan=5)

		#------------------------------
		# "Ultrasound Scan" label
		#------------------------------
		us_label = wxStaticText(self,-1,_("18/52 Ultrasound Scan"),size = (20,20))
		us_label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,''))
		us_label.SetForegroundColour(wxColour(50,50,204))
		szr_backgrnd_18WkScanDue = wxBoxSizer(wxVERTICAL)
		szr_backgrnd_18WkScanDue.Add(1,3, 0)
		szr_backgrnd_18WkScanDue.Add(us_label,1,wxEXPAND,1)
		#rcs.Add(us_label, flag=wxALIGN_CENTRE_HORIZONTAL, row=4, col=2, colspan=5)
		rcs.Add(szr_backgrnd_18WkScanDue, flag=wxALIGN_CENTRE_HORIZONTAL, row=3, col=2, colspan=5)
		#------------------------------
		# sizer holding the 'Due' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Due"),size = (100,20))
		label.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label.SetForegroundColour(wxColour(0,0,0))

  		self.txtdue = wxTextCtrl(self,-1,"",size=(100,20))
		#self.txtdue.Enable(false)
		self.txtdue.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		self.szr_txtdue  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtdue.Add(self.txtdue,1,wxEXPAND|wxALL,2)
		szr_due = wxBoxSizer(wxHORIZONTAL)
		szr_due.Add(label,1,0,0)
		szr_due.Add(10,1,0,0)
		rcs.Add(szr_due, flag=wxEXPAND, row=4, col=1)
		rcs.Add(self.szr_txtdue, flag=wxEXPAND, row=4, col=2, colspan=5)

		#------------------------------
		# "Ultrasound Scan - Revised EDC" label
		#------------------------------
		rev_edc_label = wxStaticText(self,-1,_("Ultrasound Scan - Revised EDC"),size = (100,20))
		rev_edc_label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,''))
		rev_edc_label.SetForegroundColour(wxColour(50,50,204))
		szr_backgrnd_RevEDCLabel = wxBoxSizer(wxVERTICAL)
		szr_backgrnd_RevEDCLabel.Add(1,3, 0)
		szr_backgrnd_RevEDCLabel.Add(rev_edc_label,1,wxEXPAND,1)
		#rcs.Add(rev_edc_label, flag=wxALIGN_CENTRE_HORIZONTAL, row=6, col=2, colspan=5)
		rcs.Add(szr_backgrnd_RevEDCLabel, flag=wxALIGN_CENTRE_HORIZONTAL, row=5, col=2, colspan=5)

		#------------------------------
		# sizer holding the 'newedc' stuff
		#------------------------------
		label1 = wxStaticText(self,-1,_("Date"),size = (25,20))
		label1.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label1.SetForegroundColour(wxColour(0,0,0))

  		self.txtdate = wxTextCtrl(self,-1,"",size=(25,20))
		#self.txtdate.Enable(false)
		self.txtdate.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		self.szr_txtdate  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtdate.Add(self.txtdate,1,wxEXPAND|wxALL,2)
		label2 = wxStaticText(self,-1,_("Weeks"),size = (25,20))
		label2.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label2.SetForegroundColour(wxColour(0,0,0))

		self.txtweeks = wxTextCtrl(self,-1,"",size=(25,20), style = wxTE_READONLY)
		#self.txtweeks.Enable(false)
		self.txtweeks.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		self.szr_txtweeks  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtweeks.Add(self.txtweeks,1,wxEXPAND|wxALL,2)
		label3 = wxStaticText(self,-1,_("Days"),size = (25,20))
		label3.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label3.SetForegroundColour(wxColour(0,0,0))
		
		self.txtdays = wxTextCtrl(self,-1,"",size=(25,20), style = wxTE_READONLY)
		#self.txtdays.Enable(false)
		self.txtdays.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		self.szr_txtdays  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtdays.Add(self.txtdays,1,wxEXPAND|wxALL,2)
		szr_label1 = wxBoxSizer(wxHORIZONTAL)
		szr_label1.Add(label1,1,0,0)
		szr_label1.Add(10,1,0,0)
		szr_label2 = wxBoxSizer(wxHORIZONTAL)
		szr_label2.Add(10,1,0,0)
		szr_label2.Add(label2,1,0,0)
		szr_label2.Add(10,1,0,0)
		szr_label3 = wxBoxSizer(wxHORIZONTAL)
		szr_label3.Add(10,1,0,0)
		szr_label3.Add(label3,1,0,0)
		szr_label3.Add(10,1,0,0)

		rcs.Add(szr_label1, flag=wxEXPAND, row=6, col=1)
		rcs.Add(self.szr_txtdate, flag=wxEXPAND, row=6, col=2)
		rcs.Add(szr_label2, flag=wxEXPAND, row=6, col=3)
		rcs.Add(self.szr_txtweeks, flag=wxEXPAND, row=6, col=4)
		rcs.Add(szr_label3, flag=wxEXPAND, row=6, col=5)
		rcs.Add(self.szr_txtdays, flag=wxEXPAND, row=6, col=6)

		#------------------------------
		# sizer holding the new 'EDC' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Edc"),size = (100,20))
		label.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label.SetForegroundColour(wxColour(0,0,0))

  		self.txtnewedc = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtnewedc.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		self.szr_txtnewedc  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtnewedc.Add(self.txtnewedc,1,wxEXPAND|wxALL,2)
		szr_label=wxBoxSizer(wxHORIZONTAL)
		szr_label.Add(label,1,0,0)
		szr_label.Add(10,1,0,0)
		rcs.Add(szr_label, flag=wxEXPAND, row=7, col=1)
		rcs.Add(self.szr_txtnewedc, flag=wxEXPAND, row=7, col=2, colspan=5)
		self.btnPrint = wxButton(self,1011,_('&Print'))
		self.btnSave = wxButton(self,1011,_('&Save'))
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btnPrint,0,wxEXPAND)
		szr_buttons.Add(self.btnSave,0,wxEXPAND)
		rcs.Add(szr_buttons, flag=wxEXPAND,row=9, col=3, colspan=4) 
		#------------------------------
		# Sizer holding stuff on the right
		#------------------------------
		szr_main_rt = wxBoxSizer(wxVERTICAL)
		szr_main_rt.Add(rcs)
		EVT_BUTTON(self,1010,self.EvtReset)
		EVT_BUTTON(self,1011,self.EvtPrint)
		EVT_BUTTON(self,1012,self.EvtSave)
		#------------------------------
		# Add calendar (stuff on the left)
		#------------------------------
		self.LNMPcal = wxCalendarCtrl (self, ID_LNMP,style = wxRAISED_BORDER)
		EVT_CALENDAR_SEL_CHANGED(self.LNMPcal, ID_LNMP, self.OnCalcByLNMP)

		szr_main_lf = wxBoxSizer(wxVERTICAL)
		szr_main_lf.Add(self.LNMPcal,0,wxALIGN_CENTRE_HORIZONTAL)
		btn_reset = wxButton(self, 1010, _('&Reset'))       
		#szr_main_lf.Add(5,0,5)
		szr_main_lf.Add(btn_reset,0,wxEXPAND)               

		#--------------------------------------
		# Super-sizer holds all the stuff above
		#--------------------------------------
		szr_main_top= wxBoxSizer(wxHORIZONTAL)
		szr_main_top.Add(szr_main_lf,0,0)
		szr_main_top.Add(15,0,0,0)
		szr_main_top.Add(szr_main_rt,0,0)
		#szr_main_top.Add(15,1,0,0)

		#------------------------------
		# Put everything together in one big sizer
		#------------------------------
		szr_main= wxBoxSizer(wxHORIZONTAL)
		szr_main.Add(szr_main_top,1,wxEXPAND|wxALL,10)
		self.SetSizer (szr_main)
		self.SetAutoLayout (1)
		szr_main.Fit (self)

		EVT_CLOSE (self, self.OnClose )
		self.Show(1)

	#-----------------------------------------
	def OnCalcByLNMP (self, event):
		# we do this the "UNIX Way" -- all dates are converted into seconds
		# since midnight 1 Jan, 1970.
		# .GetDate().GetTicks() returns time at 5AM.  The -18000 second correction adjusts LNMP to 12AM
		#	??? NOT NEEDED - BUG IN wxPython Day Light Savings/Standard Time Calc?

		#LNMP = self.LNMPcal.GetDate ().GetTicks () - 18000 	# Standard Time Fix (?)
		LNMP = self.LNMPcal.GetDate ().GetTicks ()		# Day Light Savings Problem
		today = wxGetCurrentTime ()
		due = LNMP + GESTATION
		gest = today - LNMP
		ultrasound18_52 = LNMP + US18_52

		"""
		print LNMP
		print today
		print due
		print gest
		"""
		LNMPtxt = wxDateTime()			# FIXME - remove time from date, change format of date (?)
		LNMPtxt.SetTimeT(LNMP)
		self.txtlnmp.SetValue(str(LNMPtxt))

		edctxt = wxDateTime()
		edctxt.SetTimeT(due)
		self.txtedc.SetValue(str(edctxt))

		ustxt = wxDateTime()
		ustxt.SetTimeT(ultrasound18_52)
		self.txtdue.SetValue(str(ustxt))

		#TODO
		# change "Gest."  split into days and weeks (?)	-- make with spin dials (similar to Ian's Preg Calc)?
		# remove time from txtlnmp, txtedc, txtdue
		# enlarge 'Date' field for when Ultrasound Scan was performed (?) OR rearrange fields (?)
		# add tooltips to wxTextCtrl fields to describe what they are and how to use the calculator
		#	e.g. "LNMP - Last Normal Menstral Period. Click on LNMP date in calendar to specify."

	#-----------------------------------------
	def EvtReset(self, event):
		# reset variables
		self.txtlnmp.SetValue("")
		self.txtedc.SetValue("")
		self.txtdue.SetValue("")		# TO COMPLETE

	#-----------------------------------------
	def EvtPrint(self, event):
		pass 					# TODO
	#-----------------------------------------
	def EvtSave(self, event):
		pass 					# TODO
	#-----------------------------------------
	def EvtHandout(self, event):
		pass 					# TODO
	#-------------------------------------------
	def OnClose (self, event):
		self.Destroy ()


#====================================================================
# Main
#====================================================================
if __name__ == '__main__':
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			frame = PregnancyFrame(None)
			frame.Show(1)
			return 1
	#---------------------
	import gettext
	_ = gettext.gettext
	gettext.textdomain ('gnumed')
	app = TestApp ()
	app.MainLoop ()
else:
	# plugin()ize
	import gmPlugin

	ID_CalcPreg_BUTTON = wxNewId()

	class gmCalcPreg (gmPlugin.wxBasePlugin):
		def name (self):
			return 'Pregnancy Calculator'
		#---------------------
		def register (self):
			menu = self.gb['main.toolsmenu']
			menu.Append (ID_MENU, _("Preg. Calc"), _("Pregnancy Calculator"))
			EVT_MENU (self.gb['main.frame'], ID_MENU, self.OnTool)
			self.tb = self.gb['main.toolbar']
			self.tool = wxToolBar (self.tb, -1, style=wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
			self.tool.AddTool(
				ID_CalcPreg_BUTTON,
				wxBitmapFromXPMData(cPickle.loads(zlib.decompress( _icons[_("""icon_Preg_calc""")] ))),
				shortHelpString = _("Pregnancy Calculator")
			)
			self.tb.AddWidgetRightBottom (self.tool)
			EVT_TOOL (self.tool, ID_CalcPreg_BUTTON, self.OnTool)
		#---------------------
		def unregister (self):
			menu = self.gb['main.toolsmenu']
			menu.Delete (ID_MENU)
		#---------------------
		def OnTool (self, event):
			frame = PregnancyFrame (self.gb['main.frame'])
			frame.Centre(wxBOTH)
			frame.Show (1)

#=====================================================================
# $Log: gmPregCalc.py,v $
# Revision 1.3  2003-07-04 14:48:23  michaelb
# some parts of the calculation is functional + some TODO notes added
#
# Revision 1.2  2003/07/04 06:56:32  rterry
# richards latest gui improvement to pregcalc
#
# Revision 1.1  2003/07/01 06:35:09  michaelb
# a new pregnancy calc
#

