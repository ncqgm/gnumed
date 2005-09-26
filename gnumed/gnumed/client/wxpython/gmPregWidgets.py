"""GnuMed pregnancy related dates caculcator.

Calculates from LMP:
 - EDC
 - 18th week ultrasound scan

Naegele's rule is easy for manual calculation, but a pain to code
Enter Haywood's rule ;-), human gestation is defined as 24192000 seconds.
(Ian, can you please explain a bit more ?)

TODO:
ideally, tool should query backend for parity, race, etc. for exact measurement
"""
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPregWidgets.py,v $
# $Id: gmPregWidgets.py,v 1.4 2005-09-26 18:01:51 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "M. Bonert, R. Terry, I. Haywood"
__licence__ = "GPL"

import math, zlib, cPickle, random, string, os.path

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx
	from wxPython import calender
	from wxPython.lib.rcsizer import RowColSizer

LMP_FIELD = 0
US_FIELD = 1

ID_LMP = wxNewId()
ID_DUE = wxNewId()
ID_DAY = wxNewId()
ID_WEEK = wxNewId()
ID_MENU = wxNewId()

GESTATION = 24192000
WEEK = 604800
DAY = 86400
US18_52 = 10886400	# 18 weeks in seconds (for 18/52 Ultrasound)

#====================================================================
class cPregCalcFrame (wxFrame):
	"""
	The new pregnancy calculator.
	"""

	#TODO
	# IMPROVE removal of time from txt_lmp, txtedc, txtdue (?)
	#	see: def PurgeTime(self, date):
	#
	# explore idea of 'status bar' across bottom -- something to make
	# 	clear how to use the calculator
	#
	# change the set-up of the RowColSizer(), shrink the size of the 'Weeks' & 'Days' fields
	#	make column on right side of preg. calc. more compact
	#
	# clean-up the names of the variables (some could be named more descriptively)
	#
	# add ability to type in LMP and Scan Date with keyboard (as opposed to only clicking on calendar)
	#	make movement between fields possible with 'tab' & 'enter'

	def __init__ (self, parent):
		myStyle = wxMINIMIZE_BOX | wxCAPTION | wxALIGN_CENTER | \
			wxALIGN_CENTER_VERTICAL | wxTAB_TRAVERSAL | wxSTAY_ON_TOP
		wxFrame.__init__(self, parent, -1, _("Pregnancy Calculator"), style=myStyle)

		# initialization of variables used in the control & calculation
		self.xfer_cal_date_to=LMP_FIELD	# controls which variable (LMP or Ultrasound) a calendar event changes
					# (if == 0): {calendar selection modifies LMP}
					# (if == 1): {calendar selection modifies Ultrasound Date}

		self.ustxt=wxDateTime_Today()	# avoids problem - one would have if the user clicked on
						# ultrasound date
						# BONUS: makes the preg. calculator useful for EDC calcs given
						# 	a date and the gestation time

		# get icon
		if __name__ == '__main__':
			png_fname = os.path.join('..', 'bitmaps', 'preg_calculator.png')
		else:
			from Gnumed.pycommon import gmGuiBroker
			gb = gmGuiBroker.GuiBroker()
			png_fname = os.path.join(gb['gnumed_dir'], 'bitmaps', 'preg_calculator.png')
		icon = wxEmptyIcon()
		icon.LoadFile(png_fname, wxBITMAP_TYPE_PNG)
		self.SetIcon(icon)

		szr_rc = RowColSizer()

		#------------------------------
		# sizer holding the 'LMP' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("LMP"),size = (50,20))	#label Lmp
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,0))

		self.txt_lmp = wxTextCtrl(self,-1,"",size=(100,20))  	# text for lmp
		self.txt_lmp.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.txt_lmp.SetToolTip(wxToolTip(_("Click on calendar to enter the last menstrual period date")))
		tiplmp=self.txt_lmp.GetToolTip()

		szr_row1 = wxBoxSizer(wxHORIZONTAL)
		szr_row1.Add(self.txt_lmp,1,wxEXPAND|wxALL,2)
		EVT_SET_FOCUS(self.txt_lmp, self.OnSetFocus_lmp)

		szr_lmp = wxBoxSizer(wxHORIZONTAL)
		szr_lmp.Add(label, 1, 0, 0)
		szr_lmp.Add((10,1),0,0)
		szr_rc.Add(szr_lmp, flag=wxEXPAND, row=0, col=1)
		szr_rc.Add(szr_row1, flag=wxEXPAND, row=0, col=2, colspan=5)
		#------------------------------
		# sizer holding the 'Gest.' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Gest."),size = (50,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,0))

		self.txtgest = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtgest.Enable(False)
		self.txtgest.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.txtgest_szr  = wxBoxSizer(wxHORIZONTAL)
		self.txtgest_szr.Add(self.txtgest,1,wxEXPAND|wxALL,2)

		szr_gest = wxBoxSizer(wxHORIZONTAL)
		szr_gest.Add(label, 1, 0, 0)
		szr_gest.Add((10,1),0,0)
		szr_rc.Add(szr_gest, flag=wxEXPAND, row=1, col=1)
		szr_rc.Add(self.txtgest_szr, flag=wxEXPAND, row=1, col=2, colspan=5)

		#------------------------------
		# sizer holding the 'EDC' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("EDC"),size = (50,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,0))

  		self.txtedc = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtedc.Enable(False)
		self.txtedc.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		szr_txtedc = wxBoxSizer(wxHORIZONTAL)
		szr_txtedc.Add(self.txtedc,1,wxEXPAND|wxALL,2)
		szr_edc = wxBoxSizer(wxHORIZONTAL)
		szr_edc.Add(label,1,0,0)
		szr_edc.Add((10,1),0,0)
		szr_rc.Add(szr_edc, flag=wxEXPAND, row=2, col=1)
		szr_rc.Add(szr_txtedc, flag=wxEXPAND, row=2, col=2, colspan=5)

		#------------------------------
		# "Ultrasound Scan" label
		#------------------------------
		us_label = wxStaticText(self,-1,_("18 Week Ultrasound Scan"),size = (200,20))
		us_label.SetFont(wxFont(10,wxSWISS,wxNORMAL,wxBOLD,False,''))
		us_label.SetForegroundColour(wxColour(50,50,204))
		szr_backgrnd_18WkScanDue = wxBoxSizer(wxVERTICAL)
		szr_backgrnd_18WkScanDue.Add((1,3), 0)
		szr_backgrnd_18WkScanDue.Add(us_label,1,wxEXPAND,1)
		szr_rc.Add(szr_backgrnd_18WkScanDue, flag=wxALIGN_CENTRE_HORIZONTAL, row=3, col=2, colspan=5)
		#------------------------------
		# sizer holding the 'Due' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Due"),size = (100,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,0))

  		self.txtdue = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtdue.Enable(False)
		self.txtdue.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.szr_txtdue  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtdue.Add(self.txtdue,1,wxEXPAND|wxALL,2)
		szr_due = wxBoxSizer(wxHORIZONTAL)
		szr_due.Add(label,1,0,0)
		szr_due.Add((10,1),0,0)
		szr_rc.Add(szr_due, flag=wxEXPAND, row=4, col=1)
		szr_rc.Add(self.szr_txtdue, flag=wxEXPAND, row=4, col=2, colspan=5)

		#------------------------------
		# "Ultrasound Scan - Revised EDC" label
		#------------------------------
		rev_edc_label = wxStaticText(self,-1,_("Ultrasound Scan - Revised EDC"),size = (300,20))
		rev_edc_label.SetFont(wxFont(10,wxSWISS,wxNORMAL,wxBOLD,False,''))
		rev_edc_label.SetForegroundColour(wxColour(50,50,204))
		szr_backgrnd_RevEDCLabel = wxBoxSizer(wxVERTICAL)
		szr_backgrnd_RevEDCLabel.Add((1,3), 0)
		szr_backgrnd_RevEDCLabel.Add(rev_edc_label,1,wxEXPAND,1)
		szr_rc.Add(szr_backgrnd_RevEDCLabel, flag=wxALIGN_CENTRE_HORIZONTAL, row=5, col=2, colspan=5)

		#------------------------------
		# sizer holding the 'newedc' stuff
		#------------------------------
		label1 = wxStaticText(self,-1,_("Scan Date"),size = (25,20))
		label1.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label1.SetForegroundColour(wxColour(0,0,0))
  		self.txtdate = wxTextCtrl(self,-1,"",size=(25,20))
		self.txtdate.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.txtdate.SetToolTip(wxToolTip(_("Click on this field and then the ultrasound scan date on the calendar")))
		tipdue=self.txtdate.GetToolTip()
		wxToolTip_Enable(1)
		self.szr_txtdate  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtdate.Add(self.txtdate,1,wxEXPAND|wxALL,2)
		EVT_SET_FOCUS(self.txtdate, self.OnSetFocus_USDate)

		szr_label1 = wxBoxSizer(wxHORIZONTAL)
		szr_label1.Add(label1,1,0,0)
		szr_label1.Add((10,1),0,0)
		szr_rc.Add(szr_label1, flag=wxEXPAND, row=6, col=1)
		szr_rc.Add(self.szr_txtdate, flag=wxEXPAND, row=6, col=2, colspan=5)

		#------------------------------

		label2 = wxStaticText(self,-1,_("Weeks"),size = (25,20))
		label2.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label2.SetForegroundColour(wxColour(0,0,0))
		self.txtweeks = wxSpinCtrl (self, -1, value = "0", min = 0, max = 42)
		EVT_SPINCTRL (self.txtweeks ,self.txtweeks.GetId(), self.EvtText_calcnewedc)
		self.txtweeks.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.szr_txtweeks  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtweeks.Add(self.txtweeks,1,wxEXPAND|wxALL,2)

		label3 = wxStaticText(self,-1,_("Days"),size = (25,20))
		label3.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label3.SetForegroundColour(wxColour(0,0,0))
		self.txtdays = wxSpinCtrl (self, -1, value = "0", min = 0, max = 6)
		EVT_SPINCTRL (self.txtdays ,self.txtdays.GetId(), self.EvtText_calcnewedc)
		self.txtdays.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.szr_txtdays  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtdays.Add(self.txtdays,1,wxEXPAND|wxALL,2)

		szr_label2 = wxBoxSizer(wxHORIZONTAL)
		szr_label2.Add(label2,1,wxALIGN_CENTRE_VERTICAL,0)
		szr_label2.Add((10,1),0,0)
		szr_label3 = wxBoxSizer(wxHORIZONTAL)
		szr_label3.Add((10,1),0,0)
		szr_label3.Add(label3,1,wxALIGN_CENTRE_VERTICAL,0)
		szr_label3.Add((10,1),0,0)
		szr_rc.Add(szr_label2, flag=wxEXPAND, row=7, col=1)
		szr_rc.Add(self.szr_txtweeks, flag=wxEXPAND, row=7, col=2, colspan=2)
		szr_rc.Add(szr_label3, flag=wxEXPAND, row=7, col=4)
		szr_rc.Add(self.szr_txtdays, flag=wxEXPAND, row=7, col=5, colspan=2)

		#------------------------------
		# sizer holding the new (or revised) 'EDC' stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Rev EDC"),size = (100,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,0))

  		self.txtnewedc = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtnewedc.Enable(False)
		self.txtnewedc.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.szr_txtnewedc  = wxBoxSizer(wxHORIZONTAL)
		self.szr_txtnewedc.Add(self.txtnewedc,1,wxEXPAND|wxALL,2)
		szr_label=wxBoxSizer(wxHORIZONTAL)
		szr_label.Add(label,1,0,0)
		szr_label.Add((10,1),0,0)
		szr_rc.Add(szr_label, flag=wxEXPAND, row=8, col=1)
		szr_rc.Add(self.szr_txtnewedc, flag=wxEXPAND, row=8, col=2, colspan=5)
		self.btnPrint = wxButton(self,1011,_('&Print'))
		self.btnSave = wxButton(self,1011,_('&Save'))
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btnPrint,0,wxEXPAND)
		szr_buttons.Add(self.btnSave,0,wxEXPAND)
		szr_rc.Add(szr_buttons, flag=wxEXPAND,row=9, col=3, colspan=4)
		#------------------------------
		# Sizer holding stuff on the right
		#------------------------------
		szr_main_rt = wxBoxSizer(wxVERTICAL)
		szr_main_rt.Add(szr_rc)
		EVT_BUTTON(self,1010,self.EvtReset)
		EVT_BUTTON(self,1011,self.EvtPrint)
		EVT_BUTTON(self,1012,self.EvtSave)
		#------------------------------
		# Add calendar (stuff on the left)
		#------------------------------
		self.lmp_cal = wxCalendarCtrl (self, ID_LMP,style = wxRAISED_BORDER)
		EVT_CALENDAR_SEL_CHANGED(self.lmp_cal, ID_LMP, self.OnCalcByLMP)

		szr_main_lf = wxBoxSizer(wxVERTICAL)
		szr_main_lf.Add(self.lmp_cal,0,wxALIGN_CENTRE_HORIZONTAL)
		btn_reset = wxButton(self, 1010, _('&Reset'))
		#szr_main_lf.Add(5,0,5)
		szr_main_lf.Add(btn_reset,0,wxEXPAND)

		#--------------------------------------
		# Super-sizer holds all the stuff above
		#--------------------------------------
		szr_main_top= wxBoxSizer(wxHORIZONTAL)
		szr_main_top.Add(szr_main_lf,0,0)
		szr_main_top.Add((15,0),0,0)
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

	#-----------------------------------------
	def OnCalcByLMP (self, event):

		if(self.xfer_cal_date_to==LMP_FIELD):
			# we do this the "UNIX Way" -- all dates are converted into seconds
			# since midnight 1 Jan, 1970.
			# .GetDate().GetTicks() returns time at 5AM.  The -18000 second
			#	correction adjusts LMP to 12AM ??? NOT NEEDED
			#	is it possible there is a BUG in the wxPython
			#	Day Light Savings/Standard Time Calc?

			#LMP = self.lmp_cal.GetDate ().GetTicks () - 18000 	# Standard Time Fix (?)
			self.lmp = self.lmp_cal.GetDate ().GetTicks ()		# Correct for Day Light Saving Time
			today = wxDateTime_Today().GetTicks()
			due = self.lmp + GESTATION
			gest = today - self.lmp
			self.ultrasound18_52 = self.lmp + US18_52

			# -----------------
			# FIXME: use gmDateInput in gmDateTimeInput.py
			lmp_txt = wxDateTime()			# FIXME? - change format of date (?)
			lmp_txt.SetTimeT(self.lmp)
			self.txt_lmp.SetValue(self.PurgeTime(lmp_txt))

			# -----------------
			gest_week = gest / WEEK
			gest_day = (gest % WEEK) / DAY
			if(gest_day==1):
				days_label=_('day')
			else:
				days_label=_('days')
			if(gest_week==1):
				weeks_label=_('week')
			else:
				weeks_label=_('weeks')
#			txtgest_str = "%s %s, %s %s" % (gest_week, weeks_label, gest_day, days_label)
			txtgest_str=str(gest_week)+" "+weeks_label+", "+str(gest_day)+" "+days_label
			self.txtgest.SetValue(txtgest_str)

			# -----------------
			edctxt = wxDateTime()
			edctxt.SetTimeT(due)
			self.txtedc.SetValue(self.PurgeTime(edctxt))

			# -----------------
			self.ustxt = wxDateTime()
			self.ustxt.SetTimeT(self.ultrasound18_52)
			self.txtdue.SetValue(self.PurgeTime(self.ustxt))

		else:
			# set Ultrasound Date
			self.usdate = self.lmp_cal.GetDate ().GetTicks ()
			usdatetxt = wxDateTime()	# FIXME? - change format of date
			usdatetxt.SetTimeT(self.usdate)
			self.txtdate.SetValue(self.PurgeTime(usdatetxt))

			# recalculate 'Rev EDC' if Ultrasound Scan Date is changed
			if( self.txtnewedc.GetValue() !=""):
				self.EvtText_calcnewedc(self)

	#-----------------------------------------
	def EvtText_calcnewedc (self, event):
		try:
			weeks=self.txtweeks.GetValue()
			days=self.txtdays.GetValue()

			# get date of ultrasound
			newedc=self.usdate+GESTATION-WEEK*weeks-DAY*days

			wxD=wxDateTime()
			wxD.SetTimeT(newedc)
			self.txtnewedc.SetValue(self.PurgeTime(wxD))
		except:
			pass	# error handling - FIXME is 'try' statement necessary (?)

	#-----------------------------------------
	def EvtReset(self, event):
		# reset variables
		self.txt_lmp.SetValue("")
		self.txtgest.SetValue("")
		self.txtedc.SetValue("")
		self.txtdue.SetValue("")

		self.txtdate.SetValue("")
		self.ustxt=wxDateTime_Today()

		self.txtweeks.SetValue(0)			# FIXME - MAKE IT RESET TO BLANK?
		self.txtdays.SetValue(0)
		self.txtnewedc.SetValue("")

		self.xfer_cal_date_to=LMP_FIELD
		self.lmp_cal.SetDate(wxDateTime_Today())	# reset Calendar to current date

	#-----------------------------------------
	def EvtPrint(self, event):
		pass 					# TODO
	#-----------------------------------------
	def EvtSave(self, event):
		pass 					# TODO
	#-----------------------------------------
	#def EvtHandout(self, event):
	#	pass 					# TODO
	#-------------------------------------------
	def OnClose (self, event):
		self.Destroy ()

	#-------------------------------------------
	def PurgeTime(self, date):			# a not so elegant way of removing the time
		time_loc=string.find(str(date),":00:00")
		date_str=str(date)
		return date_str[:(time_loc-3)]

	#-------------------------------------------
	def OnSetFocus_lmp (self, event):
		self.xfer_cal_date_to=LMP_FIELD
		event.Skip()				# required so wxTextCtrl box is selected

	#-------------------------------------------
	def OnSetFocus_USDate (self, event):
		self.lmp_cal.SetDate(self.ustxt)	# flip calendar to 18/52 date
		self.xfer_cal_date_to=US_FIELD
		event.Skip()



#====================================================================
# Main
#====================================================================
if __name__ == '__main__':
	wxInitAllImageHandlers()
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			frame = cPregCalcFrame(None)
			frame.Show(1)
			return 1
	#---------------------
	import gettext
	_ = gettext.gettext
	gettext.textdomain ('gnumed')
	app = TestApp()
	app.MainLoop()

#=====================================================================
# $Log: gmPregWidgets.py,v $
# Revision 1.4  2005-09-26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.3  2005/07/16 22:49:52  ncq
# - cleanup
#
# Revision 1.2  2005/06/16 07:39:46  rterry
# Fixed spacer values to run under wxPython 2.6
# e.g .Add(10,0,0,0) now .Add((10,0),0,0)
# Richard Terry
#
# Revision 1.1  2004/08/08 21:45:10  ncq
# - moved here
#
# Revision 1.9  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.8  2004/06/13 22:31:50  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.7  2004/03/19 09:05:55  ncq
# - fix imports
#
# Revision 1.6  2003/11/17 10:56:42  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.5  2003/07/10 03:57:07  michaelb
# bugfix - 'OnSetfocus_lmp' to 'OnSetFocus_lmp'
#
# Revision 1.4  2003/07/08 10:11:04  ncq
# - lnmp -> lmp and some cleanup
#
# Revision 1.3  2003/07/07 22:20:48  michaelb
# recalculate 'Rev EDC' if Ultrasound Scan Date is changed
#
# Revision 1.2  2003/07/07 03:35:43  michaelb
# making changes Richard made (Made labels for revised EDC more explanatory)
#
# Revision 1.1  2003/07/07 02:59:57  michaelb
# a new preg calc (obsoletes "gmCalcPreg.py"), developed in test-area/michaelb/, spelling fix in LMP wxToolTip
#
# Revision 1.8  2003/07/06 23:14:35  rterry
# 18/52 changed to 18 Week as per list suggestion
#
# Revision 1.7  2003/07/06 21:36:30  michaelb
# fixed ultrasound scan date bug, added tooltips to 'LMP' and 'Date' fields
#
# Revision 1.5  2003/07/05 06:44:28  michaelb
# fixed "Revised EDC" calc, on reset LMP selected & calendar put on current date
#
# Revision 1.4  2003/07/05 06:14:41  michaelb
# calculation fully functional!
#
# Revision 1.2  2003/07/04 06:56:32  rterry
# richards latest gui improvement to pregcalc
#
# Revision 1.1  2003/07/01 06:35:09  michaelb
# a new pregnancy calc
#
# 11/7/02: inital version
