#!/usr/bin/python

# Tool to calculate expected date of delivery
# author: Ian Haywood
# licence: GPL
# Changelog:
# 11/7/02: inital version
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/Attic/gmCalcPreg.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "Ian Haywood"

from wxPython.wx import *
from wxPython.calendar import *
import math, zlib, cPickle
import random
#import images_gnuMedGP_Toolbar

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
	__icons = {
"""icon_Preg_calc""": 'x\xdaMP1\x0e\x830\x0c\xdcy\x85\xa5\x0et\xb2`h\x95\xb9H\xac\x0c,^\x11c\x91\
\xdc\xffO\xbd\xb3C\xc0\xb1\x02w\xf1]\xec<\x8f\xdf\xd8\xad\xfd\xf8\x16\xe4K\
\xc6\xbe\xdb\xd6\xded\x97\xcf\xb1\xed\xdf@\x0e\xf4\x98\x06\xae\xc0J\\\x06\
\xae\xc0B<\x97y\x9aK\xe0%\xf1\x80\xc8sU5\xb5H\x84T\x13A:"~\xb4\x92\x0e\x8aE\
\xa0],I%\'\xac\x03\xab\xad\x92%u\xabr\xa3\x15\x85Hx\xa6\xdc<]%X\xafr\xcf\xd0\
\xdcje\xa8\xa3\x94\xfaS\xeeI\xe4mv\xde\xae\xd9\xd2\x02\xcb[\xf3\x9ar\xf56Q\
\xb0\x11\xe4\xeec\xfa\xe9\x9c$\xa7`\x03No|\xda\xd3]\xe1|:\xfd\x03\xab\xf8h\
\xbf' 
}
	def __init__ (self, parent):
		wxFrame.__init__(self, parent, -1, _("Pregnancy Calculator"))

		icon=wxEmptyIcon()
		icon.CopyFromBitmap(self.getBitmap())
		self.SetIcon(icon)

		vbox = wxBoxSizer (wxVERTICAL)
		vbox.Add (wxStaticText (self, -1, _('LNMP')), 0, wxALL, 5)
		self.LNMPcal = wxCalendarCtrl (self, ID_LNMP)
		vbox.Add (self.LNMPcal, 0, wxALL, 10)

		hbox = wxBoxSizer (wxHORIZONTAL)
		hbox.Add (wxStaticText (self, -1, _('Weeks:')), 0, wxALIGN_CENTRE)
		self.gest_week_ctrl = wxSpinCtrl (self, ID_WEEK, value = "0", min = 0, max = 42)
		hbox.Add (self.gest_week_ctrl, 1, wxALIGN_CENTRE)
		hbox.Add (wxStaticText (self, -1, _('Days:')), 0, wxALIGN_CENTRE)
		self.gest_day_ctrl = wxSpinCtrl (self, ID_DAY, value = "0", min = 0, max = 6)
		hbox.Add (self.gest_day_ctrl, 1, wxALIGN_CENTRE, 15)
		vbox.Add (hbox, 0, wxALL, 10)

		vbox.Add (wxStaticText (self, -1, _('Due date')), 0, wxALL, 5)
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


	def getBitmap (self):
		# used for:
		# (1) defintion the window icon
		# (2) defintion of button used to activate the 'Pregnancy calculator'
		return wxBitmapFromXPMData(cPickle.loads(zlib.decompress( self.__icons[_("""icon_Preg_calc""")] )))

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
			wxMessageDialog (
				self,
				_('LNMP is into the future!'),
				style = wxICON_ERROR | wxOK
			).ShowModal()
		else:
			self.gest_week_ctrl.SetValue(gest / WEEK)
			self.gest_day_ctrl.SetValue((gest % WEEK) / DAY)
			duedate = wxDateTime()
			duedate.SetTimeT(due)
			self.due_cal.SetDate(duedate)

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
			frame = PregnancyDialogue(None)
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

	class gmCalcPreg (gmPlugin.wxBasePlugin, PregnancyDialogue): # Inherit 'PregnancyDialogue' so 'getBitmap()' is available
		def name (self):
			return 'Pregnancy Calculator'
		#---------------------
		def register (self):
			menu = self.gb['main.toolsmenu']
			menu.Append (ID_MENU, _("Preg. Calc"), _("Pregnancy Calculator"))
			EVT_MENU (self.gb['main.frame'], ID_MENU, self.OnTool)
			self.tb = self.gb['main.toolbar']
			self.tool = wxToolBar (self.tb, -1, style=wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
			self.tool.AddTool (ID_BUTTON, self.getBitmap(), shortHelpString = _("Pregnancy Calculator"))
			self.tb.AddWidgetRightBottom (self.tool)
			EVT_TOOL (self.tool, ID_BUTTON, self.OnTool)
		#---------------------
		def unregister (self):
			menu = self.gb['main.toolsmenu']
			menu.Delete (ID_MENU)
		#---------------------
		def OnTool (self, event):
			frame = PregnancyDialogue (self.gb['main.frame'])
			frame.Show (1)

#=====================================================================
# $Log: gmCalcPreg.py,v $
# Revision 1.8  2003-01-06 13:47:47  ncq
# - a bit of code cleanup
#
# Revision 1.7  2003/01/04 19:42:22  michaelb
# FIXED - shortHelpString = "Pregnancy caclulator")
# i18n text + the Preg Calc icon -- "icon_Preg_calc"
# removed dependence on 'images_gnuMedGP_Toolbar.py'
#
# Revision 1.6  2002/12/31 01:11:03  michaelb
# added custom window icon & locked size and removed maximize box
#
# Revision 1.5  2002/09/21 12:44:15  ncq
# - added changelog keyword
#
