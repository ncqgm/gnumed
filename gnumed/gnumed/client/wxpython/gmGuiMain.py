#!/usr/bin/python
#############################################################################
#
# gmGuiMain - The application framework and main window of the
#             all signing all dancing GNUMed reference client.
#             (WORK IN PROGRESS)
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @Date: $Date: 2002-08-07 14:59:19 $
# @version $Revision: 1.36 $ $Date: 2002-08-07 14:59:19 $ $Author: ncq $
# @change log:
#	10.06.2001 hherb initial implementation, untested
#	01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
#
# @TODO: all testing, most of the implementation
#
############################################################################
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.

"""GNUMed GUI client
The application framework and main window of the
all signing all dancing GNUMed reference client.
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmGuiMain.py,v $
__version__ = "$Revision: 1.36 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
               S. Tan <sjtan@bigpond.com>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   D. Guest <dguest@zeeclor.mine.nu>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

from wxPython.wx import *
from wxPython.html import *

import sys, time, os
import gmLogFrame, gmGuiBroker, gmPG, gmSQLSimpleSearch, gmSelectPerson, gmConf, gmLog, gmPlugin
import images
import images_gnuMedGP_Toolbar                 #bitmaps for use on the toolbar
import images_gnuMedGP_TabbedLists             #bitmaps for tabs on notebook
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmGP_PatientPicture                     #panel to display patients picture 
import gmGP_Toolbar                            #panel with two toolbars on top of the screen
#from wxPython.lib.mixins.listctrl import wxColumnSorterMixin

from gmI18N import gmTimeformat

myLog = gmLog.gmDefLog
email_logger = None

# widget IDs
ID_ABOUT = wxNewId ()
ID_EXIT = wxNewId ()
ID_HELP = wxNewId ()
ID_NOTEBOOK = wxNewId ()
#  talkback
ID_BUTTON_CANCEL = wxNewId()
ID_BUTTON_SEND = wxNewId()
#==================================================
class MainFrame(wxFrame):
	"""GNUmed client's main windows frame
	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""

	def __init__(self, parent, id, title, size=wxPyDefaultSize):
		"""You'll have to browse the source to understand what the constructor does
		"""

		wxFrame.__init__(self, parent, id, title, size, \
		                  style = wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
		self.SetAutoLayout( true )
		#self.log = self.CreateLog()
		
		
		#initialize the gui broker
		self.guibroker = gmGuiBroker.GuiBroker()
		#allow access to a safe exit function for all modules in case of "emergencies"
		self.guibroker['EmergencyExit'] = self.CleanExit
		self.guibroker['main.frame'] = self
		self.SetupStatusBar()
		# allow all modules to access our status bar
		self.guibroker['main.statustext'] = self.SetStatusText

		backend = gmPG.ConnectionPool()
		db = backend.GetConnection('default')

		cur = db.cursor()
		cur.execute('select CURRENT_USER')
		(user,) = cur.fetchone()

		self.guibroker['main.SetWindowTitle']= self.SetTitle
		self.SetTitle(_("You are logged in as [%s]") % user)

		self.SetupPlatformDependent()
		
		self.CreateMenu()
		self.SetupAccelerators()
		self.RegisterEvents()
        ###--------------------------------------------------------------------
		###now create the  the main sizer to contain all the others on the form
		###this is same as Horst's vbox
		###--------------------------------------------------------------------
		##self.szr_main_container = wxBoxSizer(wxVERTICAL)
                ##self.guibroker['main.szr_main_container']=self.szr_main_container
		#a top vertical box sizer for the main window
		self.vbox = wxBoxSizer( wxVERTICAL)
		self.guibroker['main.vbox']=self.vbox
	
		###-----------------------------------------------------------------------------
		###create a horizontal sizer which will contain all windows at the top of the
		###screen (ie menu's and picture panel - which are on sub sizers)
		###add a wxPanel to this sizer which sits on the left and occupies 90% of width
		###followed by panel for the patients picture which occupies 10%. Add labels for
		###demo patients
		###-----------------------------------------------------------------------------
		##self.szr_top_panel = wxBoxSizer(wxHORIZONTAL) 
		##self.guibroker['main.szr_top_panel']=self.szr_top_panel
		##toolbars = ToolBar_Panel(self,-1)
		##self.szr_top_panel.Add(toolbars,1,wxEXPAND)
		##self.szr_main_container.AddSizer(self.szr_top_panel, 0, wxEXPAND|wxALL, 1)
		
		# the "top row", where all important patient data is always on display
		#self.toprowpanel = gmtoprow.gmTopRow(self, 1)
		self.topbox = wxBoxSizer( wxHORIZONTAL)
		self.patientpicture = gmGP_PatientPicture.PatientPicture(self,-1)	
		self.tb = gmGP_Toolbar.Toolbar(self,-1)
		self.topbox.Add(self.patientpicture,1,wxEXPAND)
		self.topbox.Add(self.tb,12,wxEXPAND)
		self.guibroker['main.topbox']=self.topbox
		self.guibroker['main.patientpicture'] = self.patientpicture
		self.guibroker['main.toolbar'] = self.tb
		self.vbox.AddSizer(self.topbox, 1, wxEXPAND) #|wxALL, 1)
		# now set up the main notebook
		self.nb = wxNotebook (self, ID_NOTEBOOK, style=wxNB_BOTTOM)
		self.guibroker['main.notebook'] = self.nb
		# set change in toolbar
		EVT_NOTEBOOK_PAGE_CHANGED (self.nb, ID_NOTEBOOK, self.OnNotebook)
		self.vbox.Add (self.nb, 10, wxEXPAND|wxALL, 1)
		# this dictionary relates plugins to the notebook
		self.guibroker['main.notebook.numbers'] = {}
		for plugin in gmPlugin.GetAllPlugins ('gui'):
			gmPlugin.LoadPlugin ('gui', plugin,
						guibroker = self.guibroker,
						dbbroker = backend)
		self.SetStatusText(_("You are logged in as [%s]") % user)
		self.tb.ReFit ()
		self.SetSizer( self.vbox )
		self.vbox.Fit( self )
		#don't let the window get too small
		# FIXME: should load last used size here
		# setsizehints only allows minimum size, therefore window can't become small enough
		# effectively we need the font size to be configurable according to screen size
		#self.vbox.SetSizeHints(self)
		#position the Window on the desktop
		self.Fit ()
		self.Centre(wxBOTH)
		self.Show(true)
	
	def SetupPlatformDependent(self):
		#do the platform dependent stuff
		if wxPlatform == '__WXMSW__':
			#windoze specific stuff here
			pass
		elif wxPlatform == '__WXGTK__':
			#GTK (Linux etc.) specific stuff here
			myLog.Log(gmLog.lInfo,'running on GTK (probably Linux)')
		elif wxPlatform == '__WXMAC__':
			#Mac OS specific stuff here
			myLog.Log(gmLog.lInfo,'running on a Mac')
		else:
			myLog.Log(gmLog.lInfo,'running on an unknown platform')


	def OnNotebook (self, event):
		"""
		Called when notebook changes
		"""
		nb_no = event.GetSelection ()
		# show toolbar
		self.tb.ShowBar (nb_no)
		# tell module it is shown
		self.guibroker['main.notebook.numbers'][nb_no].Shown ()
	


	def RegisterEvents(self):
		#register events we want to react to
		EVT_IDLE(self, self.OnIdle)
		EVT_CLOSE(self, self.OnClose)
		EVT_ICONIZE(self, self.OnIconize)
		EVT_MAXIMIZE(self, self.OnMaximize)



	def OnAbout(self, event):
		" A simple 'about' dialog box"
		wxMessageBox(_("Message from GNUmed:\nPlease write a nice About box!"), _("About GNUmed"))



	def SetupAccelerators(self):
		acctbl = wxAcceleratorTable([(wxACCEL_ALT|wxACCEL_CTRL, ord('X'), ID_EXIT), \
		                             (wxACCEL_CTRL, ord('H'), ID_HELP)])
		self.SetAcceleratorTable(acctbl)

	def SetupStatusBar(self):
		self.CreateStatusBar(2, wxST_SIZEGRIP)
		#add time and date display to the right corner of the status bar
		self.timer = wxPyTimer(self.Notify)
		#update every second
		self.timer.Start(1000)
		self.Notify()
	
	def Notify(self):
		"Displays date and local time in the second slot of the status bar"

		t = time.localtime(time.time())
		st = time.strftime(gmTimeformat, t)
		self.SetStatusText(st,1)
	
	def CreateMenu(self):
		"""Create the main menu entries. Individual entries are
		farmed out to the modules"""
 			
		self.mainmenu = wxMenuBar()
		self.guibroker['main.mainmenu']=self.mainmenu
		self.menu_file = wxMenu()
		self.guibroker['main.filemenu']=self.menu_file
		self.menu_file.Append(ID_EXIT, _('E&xit\tAlt-X'), _('Close this GNUmed client'))
		EVT_MENU(self, ID_EXIT, self.OnFileExit)
		self.menu_view = wxMenu()
		self.guibroker['main.viewmenu']=self.menu_view
		self.menu_tools = wxMenu()
		self.guibroker['main.toolsmenu']=self.menu_tools
		self.menu_help = wxMenu()
		self.guibroker['main.helpmenu']=self.menu_help
		self.menu_help.Append(ID_ABOUT,"About gnuMedGP", "")
		EVT_MENU (self, ID_ABOUT, self.OnAbout)
		self.menu_help.AppendSeparator()
		self.mainmenu.Append(self.menu_file, "&File");
		self.mainmenu.Append(self.menu_view, "&View");
		self.mainmenu.Append(self.menu_tools, "&Tools");
		self.mainmenu.Append(self.menu_help, "&Help");
		self.SetMenuBar(self.mainmenu)
 
		 
	def Lock(self):
		"Lock GNUmed client against unauthorized access"
		#TODO
		for i in range(1, self.nb.GetPageCount()):
			self.nb.GetPage(i).Enable(false)



	def Unlock(self):
		"""Unlock the main notebook widgets
		As long as we are not logged into the database backend,
		all pages but the 'login' page of the main notebook widget
		are locked; i.e. not accessible by the user
		"""

		#unlock notebook pages
		for i in range(1, self.nb.GetPageCount()):
			self.nb.GetPage(i).Enable(true)
		# go straight to patient selection
		self.nb.AdvanceSelection()



	def OnFileExit(self, event):
		self.Close()

       

	def CleanExit(self):
		"""This function should ALWAYS be called when this
		program is to be terminated.
		ANY code that should be executed before a regular shutdown
		should go in here
		"""
		self.timer.Stop ()
		self.mainmenu=None
		self.window=None
		self.Destroy()



	def OnClose(self,event):
		self.CleanExit()


	def OnIdle(self, event):
		"""Here we can process any background tasks
		"""
		pass



	def OnIconize(self, event):
		myLog.Log(gmLog.lInfo, 'OnIconify')



	def OnMaximize(self, event):
		myLog.Log(gmLog.lInfo,'OnMaximize')



	def OnPageChanged(self, event):
		myLog.Log(gmLog.lInfo, "Notebook page changed - need code here!")


###########################################################################
class cTalkbackFrame(wxFrame):
	def __init__(self, *args, **kwds):
		kwds["style"] = wxCAPTION|wxMINIMIZE_BOX|wxMAXIMIZE_BOX|wxSYSTEM_MENU|wxRESIZE_BORDER
		wxFrame.__init__(self, *args, **kwds)
		self.szr_main = wxBoxSizer(wxVERTICAL)

		self.szr_btns = wxBoxSizer(wxHORIZONTAL)
		self.btn_CANCEL = wxButton(self, ID_BUTTON_CANCEL, _("Don't send"), size=(-1, -1))
		self.btn_SEND = wxButton(self, ID_BUTTON_SEND, _("Send"), size=(-1, -1))

		self.szr_adr = wxBoxSizer(wxHORIZONTAL)
		self.field_to = wxTextCtrl(self, -1, "bugs@gnumed.org", size=(-1, -1), style=0)
		self.label_to = wxStaticText(self, -1, _("Send to"), size=(-1, -1), style=wxALIGN_RIGHT)
		self.field_from = wxTextCtrl(self, -1, "", size=(-1, -1), style=0)
		self.label_from = wxStaticText(self, -1, _("Your email address"), size=(-1, -1), style=wxALIGN_RIGHT)

		self.szr_desc = wxBoxSizer(wxHORIZONTAL)
		self.field_desc = wxTextCtrl(self, -1, _("I hit the big red button and ..."), size=(-1, -1), style=wxTE_MULTILINE)
		self.label_desc = wxStaticText(self, -1, _("Description/  \nComment  "), size=(-1, -1), style=wxALIGN_RIGHT)

		self.szr_hint = wxBoxSizer(wxHORIZONTAL)
		self.label_hint = wxStaticText(self, -1, _("An error occured in GNUmed. You can send a bug report from the window below."), size=(-1, -1), style=wxALIGN_CENTER)

		self.szr_title = wxBoxSizer(wxHORIZONTAL)
		self.label_title = wxStaticText(self, -1, _("GNUmed Talkback Facility"), size=(-1, -1), style=wxALIGN_CENTER)

		EVT_BUTTON(self, ID_BUTTON_CANCEL, self.onNoSend)
		EVT_BUTTON(self, ID_BUTTON_SEND, self.onSend)

		self.__set_properties()
		self.__do_layout()
    #-----------------------------------------------
	def __set_properties(self):
		self.SetTitle(_("GNUmed Talkback"))
		self.label_title.SetFont(wxFont(16, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))
    #-----------------------------------------------
	def __do_layout(self):
		self.szr_title.Add(self.label_title, 1, wxBOTTOM|wxRIGHT|wxTOP|wxALIGN_CENTER_HORIZONTAL|wxLEFT|wxALIGN_CENTER_VERTICAL, 5)
		self.szr_main.Add(self.szr_title, 1, wxALIGN_CENTER_HORIZONTAL, 0)

		self.szr_hint.Add(self.label_hint, 0, wxRIGHT|wxALIGN_CENTER_HORIZONTAL|wxLEFT|wxALIGN_CENTER_VERTICAL, 6)
		self.szr_main.Add(self.szr_hint, 1, wxEXPAND, 0)

		self.szr_desc.Add(self.label_desc, 0, wxALIGN_RIGHT|wxLEFT, 6)
		self.szr_desc.Add(self.field_desc, 3, wxBOTTOM|wxRIGHT|wxEXPAND, 8)
		self.szr_main.Add(self.szr_desc, 3, wxEXPAND, 0)

		self.szr_adr.Add(self.label_from, 0, wxRIGHT|wxALIGN_RIGHT|wxLEFT, 5)
		self.szr_adr.Add(self.field_from, 1, 0, 0)
		self.szr_adr.Add(self.label_to, 0, wxRIGHT|wxLEFT, 5)
		self.szr_adr.Add(self.field_to, 2, wxRIGHT, 8)
		self.szr_main.Add(self.szr_adr, 1, wxEXPAND, 0)

		self.szr_btns.Add(self.btn_CANCEL, 0, wxALIGN_CENTER_HORIZONTAL, 0)
		self.szr_btns.Add(20, 20, 0, wxEXPAND, 0)
		self.szr_btns.Add(self.btn_SEND, 0, 0, 0)
		self.szr_main.Add(self.szr_btns, 1, wxALIGN_CENTER_HORIZONTAL, 0)

		self.SetAutoLayout(1)
		self.SetSizer(self.szr_main)
		self.szr_main.Fit(self)
    #-----------------------------------------------	
	def onNoSend(self,event):
		self.Close(true)
    #-----------------------------------------------
	def onSend(self, event):
		email_logger.setComment (self.field_desc.GetValue())
		email_logger.setFrom (self.field_from.GetValue ())
		email_logger.flush ()
		self.Close(true)
#==================================================
class gmApp(wxApp):

	__backend = None
	__guibroker = None

	def OnInit(self):
		#do platform dependent stuff
		if wxPlatform == '__WXMSW__':
			# windoze specific stuff here
			myLog.Log(gmLog.lInfo,'running on Microsoft Windows')
			# need to explicitely init image handlers on windows
			wxInitAllImageHandlers()

		# create a static GUI element dictionary;
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()
		import gmLogin
		self.__backend = gmLogin.Login()
		if self.__backend == None:
			# _("Login attempt unsuccesful\nCan't run GNUmed without database connetcion")
			myLog.Log(gmLog.lWarn, "Login attempt unsuccesful\nCan't run GNUmed without database connection")
			return false
		#create the main window
		frame = MainFrame(None, -1, _('GNUmed client'), size=(300,200))
		self.SetTopWindow(frame)
		#frame.Unlock()
		frame.Maximize(true)
		frame.CentreOnScreen(wxBOTH)
		frame.Show(true)
		return true
#=================================================
def main():
	"""GNUmed client written in Python
	to run this application simply call main() or run the module as "main"
	"""
	#create an instance of our GNUmed main application
	app = gmApp(0)
	#and enter the main event loop
	app.MainLoop()

#=================================================
def main_with_talkback():
	"""Alternative main() method to run talkback logger.
	"""
	# "bug-gnumed@gnu.org", anSMTPServer = "fencepost.gnu.org"
	# aTo = ("gnumed-bugs@gmx.net",), anSMTPServer = "mail.gmx.net"
	global email_logger
	email_logger = gmLog.cLogTargetEMail (gmLog.lInfo, aFrom = "GNUmed client", aTo = ("ncq@localhost",), anSMTPServer = "localhost")
	myLog.AddTarget (email_logger)

	# run normal main() but catch all exceptions and reraise them
	try:
		main()
	except:
		exc = sys.exc_info()
		myLog.LogException("Unhandled Exception caught !", exc)

	#---------------------------------------------
	class cTalkbackApp(wxApp):
		def OnInit(self):
			frame = cTalkbackFrame(NULL, -1, "GNUmed Talks Back", wxDefaultPosition, size=wxSize(-1,-1), style= wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
			frame.Show (true)
			self.SetTopWindow(frame)
			return true
	#---------------------------------------------

	# run email logger window
	app = cTalkbackApp(0)
	app.MainLoop()
#==================================================
# Main
#==================================================
if __name__ == '__main__':
	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	myLog.AddTarget(aLogTarget)
	myLog.Log(gmLog.lInfo, 'Starting up as main module.')
	main()
