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
# $Id: gmPregWidgets.py,v 1.5 2005-09-28 15:57:48 ncq Exp $
__version__ = "$Revision: 1.5 $"
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

ID_LMP = wx.NewId()
ID_DUE = wx.NewId()
ID_DAY = wx.NewId()
ID_WEEK = wx.NewId()
ID_MENU = wx.NewId()

GESTATION = 24192000
WEEK = 604800
DAY = 86400
US18_52 = 10886400	# 18 weeks in seconds (for 18/52 Ultrasound)

#====================================================================
class cPregCalcFrame (wx.Frame):
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
		myStyle = wxMINIMIZE_BOX | wx.CAPTION | wx.ALIGN_CENTER | \
			wxALIGN_CENTER_VERTICAL | wx.TAB_TRAVERSAL | wx.STAY_ON_TOP
		wx.Frame.__init__(self, parent, -1, _("Pregnancy Calculator"), style=myStyle)

		# initialization of variables used in the control & calculation
		self.xfer_cal_date_to=LMP_FIELD	# controls which variable (LMP or Ultrasound) a calendar event changes
					# (if == 0): {calendar selection modifies LMP}
					# (if == 1): {calendar selection modifies Ultrasound Date}

		self.ustxt=wx.DateTime_Today()	# avoids problem - one would have if the user clicked on
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
		icon = wx.EmptyIcon()
		icon.LoadFile(png_fname, wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		szr_rc = RowColSizer()

		#------------------------------
		# sizer holding the 'LMP' stuff
		#------------------------------
		label = wx.StaticText(self,-1,_("LMP"),size = (50,20))	#label Lmp
		label.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label.SetForegroundColour(wx.Colour(0,0,0))

		self.txt_lmp = wx.TextCtrl(self,-1,"",size=(100,20))  	# text for lmp
		self.txt_lmp.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.txt_lmp.SetToolTip(wx.ToolTip(_("Click on calendar to enter the last menstrual period date")))
		tiplmp=self.txt_lmp.GetToolTip()

		szr_row1 = wx.BoxSizer(wx.HORIZONTAL)
		szr_row1.Add(self.txt_lmp,1,wx.EXPAND|wx.ALL,2)
		EVT_SET_FOCUS(self.txt_lmp, self.OnSetFocus_lmp)

		szr_lmp = wx.BoxSizer(wx.HORIZONTAL)
		szr_lmp.Add(label, 1, 0, 0)
		szr_lmp.Add((10,1),0,0)
		szr_rc.Add(szr_lmp, flag=wx.EXPAND, row=0, col=1)
		szr_rc.Add(szr_row1, flag=wx.EXPAND, row=0, col=2, colspan=5)
		#------------------------------
		# sizer holding the 'Gest.' stuff
		#------------------------------
		label = wx.StaticText(self,-1,_("Gest."),size = (50,20))
		label.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label.SetForegroundColour(wx.Colour(0,0,0))

		self.txtgest = wx.TextCtrl(self,-1,"",size=(100,20))
		self.txtgest.Enable(False)
		self.txtgest.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.txtgest_szr  = wx.BoxSizer(wx.HORIZONTAL)
		self.txtgest_szr.Add(self.txtgest,1,wx.EXPAND|wx.ALL,2)

		szr_gest = wx.BoxSizer(wx.HORIZONTAL)
		szr_gest.Add(label, 1, 0, 0)
		szr_gest.Add((10,1),0,0)
		szr_rc.Add(szr_gest, flag=wx.EXPAND, row=1, col=1)
		szr_rc.Add(self.txtgest_szr, flag=wx.EXPAND, row=1, col=2, colspan=5)

		#------------------------------
		# sizer holding the 'EDC' stuff
		#------------------------------
		label = wx.StaticText(self,-1,_("EDC"),size = (50,20))
		label.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label.SetForegroundColour(wx.Colour(0,0,0))

  		self.txtedc = wx.TextCtrl(self,-1,"",size=(100,20))
		self.txtedc.Enable(False)
		self.txtedc.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		szr_txtedc = wx.BoxSizer(wx.HORIZONTAL)
		szr_txtedc.Add(self.txtedc,1,wx.EXPAND|wx.ALL,2)
		szr_edc = wx.BoxSizer(wx.HORIZONTAL)
		szr_edc.Add(label,1,0,0)
		szr_edc.Add((10,1),0,0)
		szr_rc.Add(szr_edc, flag=wx.EXPAND, row=2, col=1)
		szr_rc.Add(szr_txtedc, flag=wx.EXPAND, row=2, col=2, colspan=5)

		#------------------------------
		# "Ultrasound Scan" label
		#------------------------------
		us_label = wx.StaticText(self,-1,_("18 Week Ultrasound Scan"),size = (200,20))
		us_label.SetFont(wxFont(10,wxSWISS,wx.NORMAL,wx.BOLD,False,''))
		us_label.SetForegroundColour(wx.Colour(50,50,204))
		szr_backgrnd_18WkScanDue = wx.BoxSizer(wx.VERTICAL)
		szr_backgrnd_18WkScanDue.Add((1,3), 0)
		szr_backgrnd_18WkScanDue.Add(us_label,1,wx.EXPAND,1)
		szr_rc.Add(szr_backgrnd_18WkScanDue, flag=wx.ALIGN_CENTRE_HORIZONTAL, row=3, col=2, colspan=5)
		#------------------------------
		# sizer holding the 'Due' stuff
		#------------------------------
		label = wx.StaticText(self,-1,_("Due"),size = (100,20))
		label.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label.SetForegroundColour(wx.Colour(0,0,0))

  		self.txtdue = wx.TextCtrl(self,-1,"",size=(100,20))
		self.txtdue.Enable(False)
		self.txtdue.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.szr_txtdue  = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_txtdue.Add(self.txtdue,1,wx.EXPAND|wx.ALL,2)
		szr_due = wx.BoxSizer(wx.HORIZONTAL)
		szr_due.Add(label,1,0,0)
		szr_due.Add((10,1),0,0)
		szr_rc.Add(szr_due, flag=wx.EXPAND, row=4, col=1)
		szr_rc.Add(self.szr_txtdue, flag=wx.EXPAND, row=4, col=2, colspan=5)

		#------------------------------
		# "Ultrasound Scan - Revised EDC" label
		#------------------------------
		rev_edc_label = wx.StaticText(self,-1,_("Ultrasound Scan - Revised EDC"),size = (300,20))
		rev_edc_label.SetFont(wxFont(10,wxSWISS,wx.NORMAL,wx.BOLD,False,''))
		rev_edc_label.SetForegroundColour(wx.Colour(50,50,204))
		szr_backgrnd_RevEDCLabel = wx.BoxSizer(wx.VERTICAL)
		szr_backgrnd_RevEDCLabel.Add((1,3), 0)
		szr_backgrnd_RevEDCLabel.Add(rev_edc_label,1,wx.EXPAND,1)
		szr_rc.Add(szr_backgrnd_RevEDCLabel, flag=wx.ALIGN_CENTRE_HORIZONTAL, row=5, col=2, colspan=5)

		#------------------------------
		# sizer holding the 'newedc' stuff
		#------------------------------
		label1 = wx.StaticText(self,-1,_("Scan Date"),size = (25,20))
		label1.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label1.SetForegroundColour(wx.Colour(0,0,0))
  		self.txtdate = wx.TextCtrl(self,-1,"",size=(25,20))
		self.txtdate.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.txtdate.SetToolTip(wx.ToolTip(_("Click on this field and then the ultrasound scan date on the calendar")))
		tipdue=self.txtdate.GetToolTip()
		wx.ToolTip_Enable(1)
		self.szr_txtdate  = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_txtdate.Add(self.txtdate,1,wx.EXPAND|wx.ALL,2)
		EVT_SET_FOCUS(self.txtdate, self.OnSetFocus_USDate)

		szr_label1 = wx.BoxSizer(wx.HORIZONTAL)
		szr_label1.Add(label1,1,0,0)
		szr_label1.Add((10,1),0,0)
		szr_rc.Add(szr_label1, flag=wx.EXPAND, row=6, col=1)
		szr_rc.Add(self.szr_txtdate, flag=wx.EXPAND, row=6, col=2, colspan=5)

		#------------------------------

		label2 = wx.StaticText(self,-1,_("Weeks"),size = (25,20))
		label2.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label2.SetForegroundColour(wx.Colour(0,0,0))
		self.txtweeks = wx.SpinCtrl (self, -1, value = "0", min = 0, max = 42)
		EVT_SPINCTRL (self.txtweeks ,self.txtweeks.GetId(), self.EvtText_calcnewedc)
		self.txtweeks.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.szr_txtweeks  = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_txtweeks.Add(self.txtweeks,1,wx.EXPAND|wx.ALL,2)

		label3 = wx.StaticText(self,-1,_("Days"),size = (25,20))
		label3.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label3.SetForegroundColour(wx.Colour(0,0,0))
		self.txtdays = wx.SpinCtrl (self, -1, value = "0", min = 0, max = 6)
		EVT_SPINCTRL (self.txtdays ,self.txtdays.GetId(), self.EvtText_calcnewedc)
		self.txtdays.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.szr_txtdays  = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_txtdays.Add(self.txtdays,1,wx.EXPAND|wx.ALL,2)

		szr_label2 = wx.BoxSizer(wx.HORIZONTAL)
		szr_label2.Add(label2,1,wx.ALIGN_CENTRE_VERTICAL,0)
		szr_label2.Add((10,1),0,0)
		szr_label3 = wx.BoxSizer(wx.HORIZONTAL)
		szr_label3.Add((10,1),0,0)
		szr_label3.Add(label3,1,wx.ALIGN_CENTRE_VERTICAL,0)
		szr_label3.Add((10,1),0,0)
		szr_rc.Add(szr_label2, flag=wx.EXPAND, row=7, col=1)
		szr_rc.Add(self.szr_txtweeks, flag=wx.EXPAND, row=7, col=2, colspan=2)
		szr_rc.Add(szr_label3, flag=wx.EXPAND, row=7, col=4)
		szr_rc.Add(self.szr_txtdays, flag=wx.EXPAND, row=7, col=5, colspan=2)

		#------------------------------
		# sizer holding the new (or revised) 'EDC' stuff
		#------------------------------
		label = wx.StaticText(self,-1,_("Rev EDC"),size = (100,20))
		label.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		label.SetForegroundColour(wx.Colour(0,0,0))

  		self.txtnewedc = wx.TextCtrl(self,-1,"",size=(100,20))
		self.txtnewedc.Enable(False)
		self.txtnewedc.SetFont(wxFont(12,wxSWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.szr_txtnewedc  = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_txtnewedc.Add(self.txtnewedc,1,wx.EXPAND|wx.ALL,2)
		szr_label=wx.BoxSizer(wx.HORIZONTAL)
		szr_label.Add(label,1,0,0)
		szr_label.Add((10,1),0,0)
		szr_rc.Add(szr_label, flag=wx.EXPAND, row=8, col=1)
		szr_rc.Add(self.szr_txtnewedc, flag=wx.EXPAND, row=8, col=2, colspan=5)
		self.btnPrint = wx.Button(self,1011,_('&Print'))
		self.btnSave = wx.Button(self,1011,_('&Save'))
		szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
		szr_buttons.Add(self.btnPrint,0,wx.EXPAND)
		szr_buttons.Add(self.btnSave,0,wx.EXPAND)
		szr_rc.Add(szr_buttons, flag=wx.EXPAND,row=9, col=3, colspan=4)
		#------------------------------
		# Sizer holding stuff on the right
		#------------------------------
		szr_main_rt = wx.BoxSizer(wx.VERTICAL)
		szr_main_rt.Add(szr_rc)
		EVT_BUTTON(self,1010,self.EvtReset)
		EVT_BUTTON(self,1011,self.EvtPrint)
		EVT_BUTTON(self,1012,self.EvtSave)
		#------------------------------
		# Add calendar (stuff on the left)
		#------------------------------
		self.lmp_cal = wx.CalendarCtrl (self, ID_LMP,style = wx.RAISED_BORDER)
		EVT_CALENDAR_SEL_CHANGED(self.lmp_cal, ID_LMP, self.OnCalcByLMP)

		szr_main_lf = wx.BoxSizer(wx.VERTICAL)
		szr_main_lf.Add(self.lmp_cal,0,wx.ALIGN_CENTRE_HORIZONTAL)
		btn_reset = wx.Button(self, 1010, _('&Reset'))
		#szr_main_lf.Add(5,0,5)
		szr_main_lf.Add(btn_reset,0,wx.EXPAND)

		#--------------------------------------
		# Super-sizer holds all the stuff above
		#--------------------------------------
		szr_main_top= wx.BoxSizer(wx.HORIZONTAL)
		szr_main_top.Add(szr_main_lf,0,0)
		szr_main_top.Add((15,0),0,0)
		szr_main_top.Add(szr_main_rt,0,0)
		#szr_main_top.Add(15,1,0,0)

		#------------------------------
		# Put everything together in one big sizer
		#------------------------------
		szr_main= wx.BoxSizer(wx.HORIZONTAL)
		szr_main.Add(szr_main_top,1,wx.EXPAND|wx.ALL,10)
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
			today = wx.DateTime_Today().GetTicks()
			due = self.lmp + GESTATION
			gest = today - self.lmp
			self.ultrasound18_52 = self.lmp + US18_52

			# -----------------
			# FIXME: use gmDateInput in gmDateTimeInput.py
			lmp_txt = wx.DateTime()			# FIXME? - change format of date (?)
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
			edctxt = wx.DateTime()
			edctxt.SetTimeT(due)
			self.txtedc.SetValue(self.PurgeTime(edctxt))

			# -----------------
			self.ustxt = wx.DateTime()
			self.ustxt.SetTimeT(self.ultrasound18_52)
			self.txtdue.SetValue(self.PurgeTime(self.ustxt))

		else:
			# set Ultrasound Date
			self.usdate = self.lmp_cal.GetDate ().GetTicks ()
			usdatetxt = wx.DateTime()	# FIXME? - change format of date
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

			wx.D=wx.DateTime()
			wx.D.SetTimeT(newedc)
			self.txtnewedc.SetValue(self.PurgeTime(wx.D))
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
		self.ustxt=wx.DateTime_Today()

		self.txtweeks.SetValue(0)			# FIXME - MAKE IT RESET TO BLANK?
		self.txtdays.SetValue(0)
		self.txtnewedc.SetValue("")

		self.xfer_cal_date_to=LMP_FIELD
		self.lmp_cal.SetDate(wx.DateTime_Today())	# reset Calendar to current date

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
	wx.InitAllImageHandlers()
	# set up dummy app
	class TestApp (wx.App):
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
# Revision 1.5  2005-09-28 15:57:48  ncq
# - a whole bunch of wxFoo -> wx.Foo
#
# Revision 1.4  2005/09/26 18:01:51  ncq
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
