#!/usr/bin/python

# Tool to calculate expected date of delivery
# author: Ian Haywood
# licence: GPL
# Changelog:
# 11/7/02: inital version
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/Attic/gmCalcPreg.py,v $
__version__ = "$Revision"
__author__ = "Ian Haywood"

from wxPython.wx import *
from wxPython.calendar import *
import math
import random

import gmI18N

ID_LNMP = wxNewId ()
ID_DUE = wxNewId ()
ID_DAY = wxNewId ()
ID_WEEK = wxNewId ()
ID_MENU = wxNewId ()
ID_BUTTON = wxNewId ()

# Naegele's rule is easy for manual calculation, but a pain to code
# Enter Haywood's rule ;-), human gestation is defined as 24192000 seconds.
GESTATION = 24192000
# ideally, tool should query backend for parity, race, etc. for exact measurement
WEEK = 604800
DAY = 86400
#====================================================================
class PregnancyDialogue (wxFrame):
	"""
	Dialogue class to show dates.
	"""

	def __init__ (self, parent):
		wxFrame.__init__(self, parent, -1, _("Pregnancy Calculator"))
		vbox = wxBoxSizer (wxVERTICAL)
		vbox.Add (wxStaticText (self, -1, 'LNMP'), 0, wxALL, 5)
		self.LNMPcal = wxCalendarCtrl (self, ID_LNMP)
		vbox.Add (self.LNMPcal, 0, wxALL, 10)

		hbox = wxBoxSizer (wxHORIZONTAL)
		hbox.Add (wxStaticText (self, -1, 'Weeks:'), 0, wxALIGN_CENTRE)	  
		self.gest_week_ctrl = wxSpinCtrl (self, ID_WEEK, value = "0", min = 0, max = 42)
		hbox.Add (self.gest_week_ctrl, 1, wxALIGN_CENTRE)
		hbox.Add (wxStaticText (self, -1, 'Days:'), 0, wxALIGN_CENTRE)	 
		self.gest_day_ctrl = wxSpinCtrl (self, ID_DAY, value = "0", min = 0, max = 6)
		hbox.Add (self.gest_day_ctrl, 1, wxALIGN_CENTRE, 15)
		vbox.Add (hbox, 0, wxALL, 10)
		
		vbox.Add (wxStaticText (self, -1, 'Due date'), 0, wxALL, 5)
		self.due_cal = wxCalendarCtrl (self, ID_DUE)
		vbox.Add (self.due_cal, 0, wxALL, 10)
		
		self.SetSizer (vbox)
		self.SetAutoLayout (1)
		vbox.Fit (self)

		EVT_CALENDAR_SEL_CHANGED(self.LNMPcal, ID_LNMP, self.OnCalcByLNMP)
		EVT_SPINCTRL (self.gest_week_ctrl, ID_WEEK, self.OnCalcByGest)
		EVT_SPINCTRL (self.gest_day_ctrl, ID_DAY, self.OnCalcByGest)
		EVT_CLOSE (self, self.OnClose )
		self.Show(1)

	def OnClose (self, event):
		self.Destroy ()

	def OnCalcByLNMP (self, event):
		# we do this the "UNIX Way" -- all dates are converted into seconds
		# since midnight 1 Jan, 1970.
		LNMP = self.LNMPcal.GetDate ().GetTicks ()
		today = wxGetCurrentTime ()
		due = LNMP + GESTATION
		gest = today - LNMP
		if gest < 0:
			wxMessageDialog (self, 'LNMP is into the future!', style = wxICON_ERROR | wxOK).ShowModal ()
		else:
			self.gest_week_ctrl.SetValue (gest / WEEK)
			self.gest_day_ctrl.SetValue ((gest % WEEK) / DAY)
			duedate = wxDateTime ()
			duedate.SetTimeT (due)
			self.due_cal.SetDate (duedate)

	def OnCalcByGest (self, event):
		day = self.gest_day_ctrl.GetValue ()
		week = self.gest_week_ctrl.GetValue ()
		today = wxGetCurrentTime ()
		LNMP = today - (day*DAY) - (week*WEEK)
		due = LNMP + GESTATION
		date = wxDateTime ()
		date.SetTimeT (LNMP)
		self.LNMPcal.SetDate (date)
		date.SetTimeT (due)
		self.due_cal.SetDate (date)
#====================================================================
# Main
#====================================================================
if __name__ == '__main__':
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			frame = PregnancyDialogue (None)
			frame.Show (1)
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
	import images_gnuMedGP_Toolbar

	class gmCalcPreg (gmPlugin.wxBasePlugin):
		def name (self):
			return 'Pregnancy Calculator'
		#---------------------
		def register (self):
			menu = self.gb['main.toolsmenu']
			menu.Append (ID_MENU, "Preg. Calc", "Pregnancy Calculator")
			EVT_MENU (self.gb['main.frame'], ID_MENU, self.OnTool)
			self.tb = self.gb['main.toolbar']
			self.tool = wxBitmapButton (self.tb, ID_BUTTON, bitmap= images_gnuMedGP_Toolbar.getToolbar_PregcalcBitmap(), style=0)
			self.tool.SetToolTip (wxToolTip('Pregnancy Calculator'))
			self.tb.AddWidgetRightBottom (self.tool)
			EVT_BUTTON (self.tool, ID_BUTTON, self.OnTool)
		#---------------------
		def unregister (self):
			menu = self.gb['main.toolsmenu']
			menu.Delete (ID_MENU)
		#---------------------
		def OnTool (self, event):
			frame = PregnancyDialogue (self.gb['main.frame'])
			frame.Show (1)
		#---------------------
