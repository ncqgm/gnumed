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
# @Date: $Date: 2002-06-26 04:53:02 $
# @version $Revision: 1.3 $ $Date: 2002-06-26 04:53:02 $ $Author: ihaywood $
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
__version__ = "$Revision: 1.3 $"
__author__  = "H. Herb <hherb@gnumed.net>, S. Tan <sjtan@bigpond.com>, K. Hilbert <Karsten.Hilbert@gmx.net>"

# text translation function for localization purposes
import gettext
_ = gettext.gettext

from wxPython.wx import *
from wxPython.html import *
from gmI18N import *

import sys, time, os
import gmLogFrame, gmGuiBroker, gmPG, gmmanual, gmSQLSimpleSearch, gmSelectPerson, gmConf
import gmLog
import gmPlugin
import gmGP_MainWindowManager
import images
import images_gnuMedGP_Toolbar                 #bitmaps for use on the toolbar
import images_gnuMedGP_TabbedLists             #bitmaps for tabs on notebook
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmGP_PatientPicture                     #panel to display patients picture 
import gmGP_Toolbar                            #panel with two toolbars on top of the screen
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin

# widget IDs
ID_ABOUT = wxNewId ()
ID_EXIT = wxNewId ()
ID_HELP = wxNewId ()
ID_NOTEBOOK = wxNewId ()
 	


class MainFrame(wxFrame):
	"""GNUMed client's main windows frame
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
		if gmConf.config ['main.use_notebook']:
			# now set up the main notebook
			self.nb = wxNotebook (self, ID_NOTEBOOK, style=wxNB_BOTTOM)
			self.guibroker['main.notebook'] = self.nb
			self.vbox.Add (self.nb, 10, wxEXPAND|wxALL, 1)
			self.mwm = gmGP_MainWindowManager.MainWindowManager(self.nb)
			self.nb.AddPage (self.mwm, "Patient")
		else:
			self.mwm = gmGP_MainWindowManager.MainWindowManager(self)
			self.vbox.Add(self.mwm, 10, wxEXPAND|wxALL, 1)
		#
		self.guibroker['main.manager'] = self.mwm
		for plugin in gmPlugin.GetAllPlugins ('gui'):
			gmPlugin.LoadPlugin ('gui', plugin,
						guibroker = self.guibroker,
						dbbroker = backend)
		self.mwm.SetDefault ('Clinical Summary')
		self.mwm.Display (self.mwm.default)
		# realize the toolbars
		self.guibroker['main.top_toolbar'].Realize ()
		self.guibroker['main.bottom_toolbar'].Realize ()
		self.SetStatusText(_("You are logged in as [%s]") % user)

		self.SetSizer( self.vbox )
		self.vbox.Fit( self )
		#don't let the window get too small
		#self.vbox.SetSizeHints(self)
		#position the Window on the desktop
		self.Centre(wxBOTH)
		self.Show(true)
	
	def SetupPlatformDependent(self):
		#do the platform dependent stuff
		if wxPlatform == '__WXMSW__':
			#windoze specific stuff here
			myLog.Log(gmLog.lInfo,'running on Microsoft Windows')
			pass
		elif wxPlatform == '__WXGTK__':
			#GTK (Linux etc.) specific stuff here
			myLog.Log(gmLog.lInfo,'running on GTK (probably Linux)')
			pass
		elif wxPlatform == '__WXMAC__':
			#Mac OS specific stuff here
			myLog.Log(gmLog.lInfo,'running on a Mac')
			pass
		else:
			myLog.Log(gmLog.lInfo,'running on an unknown platform')



	def RegisterEvents(self):
		#register events we want to react to
		EVT_IDLE(self, self.OnIdle)
		EVT_CLOSE(self, self.OnClose)
		EVT_ICONIZE(self, self.OnIconize)
		EVT_MAXIMIZE(self, self.OnMaximize)



	def OnAbout(self, event):
		" A simple 'about' dialog box"
		wxMessageBox(_("Message from GNUMed:\nPlease write a nice About box!"), _("About GNUMed"))



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
		self.menu_file.Append(ID_EXIT, _('E&xit\tAlt-X'), _('Close this GNUMed client'))
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
		"Lock GNUMed client against unauthorized access"
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


#==================================================

class gmApp(wxApp):

	__backend = None
	__guibroker = None

	def OnInit(self):
		# create a static GUI element dictionary;
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()
		# ADDED CODE: Haywood 26/2/02
		# home directory for file resources, such
		# as images. Sets to .../gnumed/gnumed/client Is this
		if os.environ.has_key('GNUMED'):
			self.__guibroker['gnumed_dir'] = os.environ['GNUMED']
		else:
			self.__guibroker['gnumed_dir'] = os.path.abspath (os.path.split (sys.argv[0])[0])[:-9]
		myLog.Log(gmLog.lInfo, _("set resource path to: ") + self.__guibroker['gnumed_dir'])
		# END ADDED CODE
		#login first!
		import gmLogin
		self.__backend = gmLogin.Login()
		if self.__backend == None:
			# _("Login attempt unsuccesful\nCan't run GNUMed without database connetcion")
			myLog.Log(gmLog.lPanic, _("Login attempt unsuccesful\nCan't run GNUMed without database connection"))
			return false
		#create the main window
		frame = MainFrame(None, -1, _('GNUMed client'), size=(300,200))
		self.SetTopWindow(frame)
		#frame.Unlock()
		frame.Maximize(true)
		frame.CentreOnScreen(wxBOTH)
		frame.Show(true)
		return true




def main():
	"""GNUMed client written in Python
	to run this application simply call main() or run the module as "main"
	"""

	#create an instance of our GNUMed main application
	app = gmApp(0)

	#and enter the main event loop
	app.MainLoop()


#==================================================
# just for convenience, really
myLog = gmLog.gmDefLog

if __name__ == '__main__':
	# we may want to reset the log level, so keep a global reference to the log target
	# append only, log level "informational"
	myLogFile = gmLog.cLogTargetFile(gmLog.lInfo, 'gnumed.log', 'a')
	myLog.AddTarget(myLogFile)

	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	myLog.AddTarget(aLogTarget)

	myLog.Log(gmLog.lInfo, 'Starting up as main module.')

	main()
