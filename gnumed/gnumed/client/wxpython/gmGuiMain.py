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
# @Date: $Date: 2002-11-30 11:09:55 $
# @version $Revision: 1.51 $ $Date: 2002-11-30 11:09:55 $ $Author: ncq $
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
__version__ = "$Revision: 1.51 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
               S. Tan <sjtan@bigpond.com>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

from wxPython.wx import *
from wxPython.html import *

import sys, time, os

import gmDispatcher, gmSignals, gmGuiBroker, gmPG, gmSQLSimpleSearch, gmSelectPerson, gmConf, gmLog, gmPlugin, gmCfg
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
_cfg = gmCfg.gmDefCfgFile

# widget IDs
ID_ABOUT = wxNewId ()
ID_EXIT = wxNewId ()
ID_HELP = wxNewId ()
ID_NOTEBOOK = wxNewId ()
#==================================================
class MainFrame(wxFrame):
	"""GNUmed client's main windows frame
	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""
	#----------------------------------------------
	def __init__(self, parent, id, title, size=wxPyDefaultSize):
		"""You'll have to browse the source to understand what the constructor does
		"""
		wxFrame.__init__(self, parent, id, title, size, \
		                  style = wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
		self.SetAutoLayout( true )
		
		#initialize the gui broker
		self.guibroker = gmGuiBroker.GuiBroker()
		#allow access to a safe exit function for all modules in case of "emergencies"
		self.guibroker['EmergencyExit'] = self.CleanExit
		self.guibroker['main.frame'] = self
		self.SetupStatusBar()
		# allow all modules to access our status bar
		self.guibroker['main.statustext'] = self.SetStatusText

		# set window title via template
		#  get user
		backend = gmPG.ConnectionPool()
		db = backend.GetConnection('default')
		curs = db.cursor()
		curs.execute('select CURRENT_USER')
		(user,) = curs.fetchone()
		curs.close()
		#  set it
		self.updateTitle(anActivity = _("idle"), aPatient = _("no patient"), aUser = user)
		#  let others have access, too
		self.guibroker['main.SetWindowTitle'] = self.updateTitle

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
		self.vbox.Add (self.nb, 10, wxEXPAND | wxALL, 1)

		# load plugins
		#  this dictionary relates plugins to the notebook
		self.guibroker['main.notebook.numbers'] = {}
		self.LoadPlugins(backend)

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
	#----------------------------------------------
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
	#----------------------------------------------
	def LoadPlugins(self, backend):
		plugin_list = gmPlugin.GetAllPlugins('gui')
		nr_plugins = len(plugin_list)
		#  set up a progress bar
		progress_bar = wxProgressDialog(
			title = _("GnuMed: loading %s plugins") % nr_plugins,
			message = _("loading list of plugins                    "),
			maximum = nr_plugins,
			parent = None,
			style = wxPD_ELAPSED_TIME
			)
		#  and load them
		last_plugin = ""
		result = ""
		for idx in range(len(plugin_list)):
			curr_plugin = plugin_list[idx]
			progress_bar.Update(
				idx,
				_("previous: %s - %s\ncurrent (%s/%s): %s") % (last_plugin, result, (idx+1), nr_plugins, curr_plugin)
			)
			if gmPlugin.LoadPlugin ('gui', curr_plugin, guibroker = self.guibroker, dbbroker = backend):
				result = _("success")
			else:
				myLog.Log(gmLog.lInfo,'failed to load plugin %s' % curr_plugin)
				result = _("failed")
			last_plugin = curr_plugin
		progress_bar.Destroy()
	#----------------------------------------------
	def OnNotebook (self, event):
		"""
		Called when notebook changes
		"""
		nb_no = event.GetSelection ()
		# show toolbar
		self.tb.ShowBar (nb_no)
		# tell module it is shown
		self.guibroker['main.notebook.numbers'][nb_no].Shown ()
	#----------------------------------------------
	def RegisterEvents(self):
		"""register events we want to react to"""
		# wxPython events
		EVT_IDLE(self, self.OnIdle)
		EVT_CLOSE(self, self.OnClose)
		EVT_ICONIZE(self, self.OnIconize)
		EVT_MAXIMIZE(self, self.OnMaximize)

		# intra-client signals
		gmDispatcher.connect(self.OnPatientChanged, gmSignals.patient_selected())
	#----------------------------------------------		
	def OnPatientChanged(self, **kwargs):
		kwds = kwargs['kwds']
		patient = "%(title)s %(firstnames)s %(lastnames)s (%(dob)10.10s) #%(ID)d" % (kwds)
		self.updateTitle(aPatient = patient)
	#----------------------------------------------
	def OnAbout(self, event):
		" A simple 'about' dialog box"
		wxMessageBox(_("Message from GnuMed:\nPlease write a nice About box!"), _("About GnuMed"))
	#----------------------------------------------
	def SetupAccelerators(self):
		acctbl = wxAcceleratorTable([(wxACCEL_ALT|wxACCEL_CTRL, ord('X'), ID_EXIT), \
		                             (wxACCEL_CTRL, ord('H'), ID_HELP)])
		self.SetAcceleratorTable(acctbl)
	#----------------------------------------------
	def SetupStatusBar(self):
		self.CreateStatusBar(2, wxST_SIZEGRIP)
		#add time and date display to the right corner of the status bar
		self.timer = wxPyTimer(self.Notify)
		#update every second
		self.timer.Start(1000)
		self.Notify()
	#----------------------------------------------	
	def Notify(self):
		"Displays date and local time in the second slot of the status bar"

		t = time.localtime(time.time())
		st = time.strftime(gmTimeformat, t)
		self.SetStatusText(st,1)
	#----------------------------------------------	
	def CreateMenu(self):
		"""Create the main menu entries. Individual entries are
		farmed out to the modules"""
 			
		self.mainmenu = wxMenuBar()
		self.guibroker['main.mainmenu']=self.mainmenu
		self.menu_file = wxMenu()
		self.guibroker['main.filemenu']=self.menu_file
		self.menu_file.Append(ID_EXIT, _('E&xit\tAlt-X'), _('Close this GnuMed client'))
		EVT_MENU(self, ID_EXIT, self.OnFileExit)
		self.menu_view = wxMenu()
		self.guibroker['main.viewmenu']=self.menu_view
		self.menu_tools = wxMenu()
		self.guibroker['main.toolsmenu']=self.menu_tools
		self.menu_help = wxMenu()
		self.guibroker['main.helpmenu']=self.menu_help
		self.menu_help.Append(ID_ABOUT, _("About GnuMed"), "")
		EVT_MENU (self, ID_ABOUT, self.OnAbout)
		self.menu_help.AppendSeparator()
		self.mainmenu.Append(self.menu_file, "&File");
		self.mainmenu.Append(self.menu_view, "&View");
		self.mainmenu.Append(self.menu_tools, "&Tools");
		self.mainmenu.Append(self.menu_help, "&Help");
		self.SetMenuBar(self.mainmenu)
	#---------------------------------------------- 		 
	def Lock(self):
		"Lock GNUmed client against unauthorized access"
		#TODO
		for i in range(1, self.nb.GetPageCount()):
			self.nb.GetPage(i).Enable(false)
	#----------------------------------------------
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
	#----------------------------------------------
	def OnFileExit(self, event):
		self.Close()
	#----------------------------------------------
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
	#----------------------------------------------
	def OnClose(self,event):
		self.CleanExit()
	#----------------------------------------------
	def OnIdle(self, event):
		"""Here we can process any background tasks
		"""
		pass
	#----------------------------------------------
	def OnIconize(self, event):
		pass
		#myLog.Log(gmLog.lInfo, 'OnIconify')
	#----------------------------------------------
	def OnMaximize(self, event):
		pass
		#myLog.Log(gmLog.lInfo,'OnMaximize')
	#----------------------------------------------
	def OnPageChanged(self, event):
		myLog.Log(gmLog.lInfo, "Notebook page changed - need code here!")
	#----------------------------------------------
	def updateTitle(self, anActivity = None, aPatient = None, aUser = None):
		"""Update title of main window based on template.

		This gives nice tooltips on iconified GnuMed instances.
		"""
		if not anActivity is None:
			self.title_activity = str(anActivity)
		if not aPatient is None:
			self.title_patient = str(aPatient)
		if not aUser is None:
			self.title_user = str(aUser)

		# generate title from template
		title = "GnuMed [%s@%s] %s: %s" % (self.title_user, self.guibroker['workplace_name'], self.title_activity, self.title_patient)

		# set it
		self.SetTitle(title)
#==================================================
class gmApp(wxApp):

	__backend = None
	__guibroker = None
	#----------------------------------------------
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
			myLog.Log(gmLog.lWarn, "Login attempt unsuccesful. Can't run GnuMed without database connection")
			return false
		#create the main window
		frame = MainFrame(None, -1, _('GnuMed client'), size=(600,440))
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
#==================================================
# Main
#==================================================
if __name__ == '__main__':
	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	myLog.AddTarget(aLogTarget)
	myLog.Log(gmLog.lInfo, 'Starting up as main module.')
	main()

myLog.Log(gmLog.lData, __version__)

#==================================================
# $Log: gmGuiMain.py,v $
# Revision 1.51  2002-11-30 11:09:55  ncq
# - refined title bar
# - comments
#
# Revision 1.50  2002/11/13 10:07:25  ncq
# - export updateTitle() via guibroker
# - internally set title according to template
#
# Revision 1.49  2002/11/12 21:24:51  hherb
# started to use dispatcher signals
#
# Revision 1.48  2002/11/09 18:14:38  hherb
# Errors / delay caused by loading plugin progess bar fixed
#
# Revision 1.47  2002/09/30 10:57:56  ncq
# - make GnuMed consistent spelling in user-visible strings
#
# Revision 1.46  2002/09/26 13:24:15  ncq
# - log version
#
# Revision 1.45  2002/09/12 23:21:38  ncq
# - fix progress bar
#
# Revision 1.44  2002/09/10 12:25:33  ncq
# - gimmicks rule :-)
# - display plugin_nr/nr_of_plugins on load in progress bar
#
# Revision 1.43  2002/09/10 10:26:03  ncq
# - properly i18n() strings
#
# Revision 1.42  2002/09/10 09:08:49  ncq
# - set a useful window title and add a comment regarding this item
#
# Revision 1.41  2002/09/09 10:07:48  ncq
# - long initial string so module names fit into progress bar display
#
# Revision 1.40  2002/09/09 00:52:55  ncq
# - show progress bar on plugin load :-)
#
# Revision 1.39  2002/09/08 23:17:37  ncq
# - removed obsolete reference to gmLogFrame.py
#
