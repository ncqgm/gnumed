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
# @Date: $Date: 2003-02-01 06:41:03 $
# @version $Revision: 1.62 $ $Date: 2003-02-01 06:41:03 $ $Author: michaelb $
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
__version__ = "$Revision: 1.62 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
               S. Tan <sjtan@bigpond.com>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

from wxPython.wx import *
from wxPython.html import *

import sys, time, os, cPickle, zlib

import gmDispatcher, gmSignals, gmGuiBroker, gmPG, gmSQLSimpleSearch, gmSelectPerson, gmLog, gmPlugin, gmCfg
import images
import images_gnuMedGP_Toolbar                 #bitmaps for use on the toolbar
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
ID_MENU = wxNewId ()
#==================================================
class MainFrame(wxFrame):
	"""GNUmed client's main windows frame.

	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""
	
	icon_gui_main='x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec'

	#----------------------------------------------
	def __init__(self, parent, id, title, size=wxPyDefaultSize):
		"""You'll have to browse the source to understand what the constructor does
		"""
		wxFrame.__init__(
			self,
			parent,
			id,
			title,
			size,
			style = wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE
		)
		self.SetAutoLayout(true)
		
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
		self.guibroker['main.vbox'] = self.vbox

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
		# add popup menu to notebook
		EVT_RIGHT_UP(self.nb, self.OnNotebookPopup)
		self.vbox.Add (self.nb, 10, wxEXPAND | wxALL, 1)
		#  this list relates plugins to the notebook
		self.guibroker['main.notebook.numbers'] = []
		# load plugins
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
	def OnNotebookPopup(self, evt):
		load_menu = wxMenu()
		show_menu = wxMenu()
		any_loadable = 0
		any_showable = 0
		plugin_list = gmPlugin.GetPluginLoadList('gui')
		myLog.Log(gmLog.lData, str(type(plugin_list)) + ": " + str(plugin_list))
		for plugin_name in plugin_list:
			plugin = gmPlugin.InstPlugin ('gui', plugin_name, guibroker = self.guibroker)
			if isinstance (plugin, gmPlugin.wxNotebookPlugin): 
				if not (plugin.name() in self.guibroker['modules.gui'].keys()):
					# if not installed
					id = wxNewId ()
					load_menu.AppendItem(wxMenuItem(load_menu, id, plugin.name()))
					EVT_MENU (load_menu, id, plugin.OnLoad)
					any_loadable = 1
					# else
				        #show_menu.AppendItem(wxMenuItem (show_menu, id, plugin.name ()))
				        #EVT_MENU (show_menu, id, plugin.OnShow)
				        #any_showable = 1

		menu = wxMenu()
		ID_LOAD = wxNewId ()
		ID_SHOW = wxNewId ()
		ID_DROP = wxNewId ()
		ID_HIDE = wxNewId ()
		if any_loadable:
			menu.AppendMenu(ID_LOAD, _("Load New"), load_menu)
		if any_showable:
			menu.AppendMenu (ID_SHOW, _("Show"), show_menu)
		menu.AppendItem(wxMenuItem(menu, ID_DROP, "Drop Window ..."))
		menu.AppendItem(wxMenuItem(menu, ID_HIDE, "Hide Window ..."))
		EVT_MENU (menu, ID_DROP, self.OnPluginDrop)
		EVT_MENU (menu, ID_HIDE, self.OnPluginHide)
		self.PopupMenu(menu, evt.GetPosition())
		menu.Destroy()
		evt.Skip()
	#----------------------------------------------		
	def OnPluginDrop (self, evt):
		# this dictionary links notebook page numbers to plugin objects
		nbns = self.guibroker['main.notebook.numbers']
		# get the widget of the currently selected window
		nbns[self.nb.GetSelection ()].unregister ()
		# FIXME:"dropping" means talking to configurator so not reloaded
	#----------------------------------------------
	def OnPluginHide (self, evt):
		# this dictionary links notebook page numbers to plugin objects
		nbns = self.guibroker['main.notebook.numbers']
		# get the widget of the currently selected window
		nbns[self.nb.GetSelection ()].unregister ()
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
		# get plugin list
		plugin_list = gmPlugin.GetPluginLoadList('gui')
		if plugin_list is None:
			_log.Log(gmLog.lWarn, "no plugins to load")
			return 1
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
				_("previous: %s - %s\ncurrent (%s/%s): %s") % (
					last_plugin,
					result,
					(idx+1),
					nr_plugins,
					curr_plugin)
			)

			try:
				p = gmPlugin.InstPlugin ('gui', curr_plugin, guibroker = self.guibroker, dbbroker = backend)
				p.register()
				result = _("success")
			except:
				myLog.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info())
				result = _("failed")

			last_plugin = curr_plugin

		progress_bar.Destroy()
	#----------------------------------------------
	def OnNotebook (self, event):
		"""
		Called when notebook changes
		"""
		nb_no = event.GetSelection ()
		nbns = self.guibroker['main.notebook.numbers']
		# show toolbar
		self.tb.ShowBar (nbns[nb_no].name ())
		# tell module it is shown
		nbns[nb_no].Shown ()
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
		gmAbout=AboutFrame(self, -1, _("About GnuMed"), size=wxSize(300, 250), style = wxMAXIMIZE_BOX)
		gmAbout.Centre(wxBOTH)
    		MainFrame.otherWin = gmAbout
		gmAbout.Show(true)
	#----------------------------------------------
	def SetupAccelerators(self):
		acctbl = wxAcceleratorTable([
			(wxACCEL_ALT | wxACCEL_CTRL, ord('X'), ID_EXIT),
			(wxACCEL_CTRL, ord('H'), ID_HELP)
		])
		self.SetAcceleratorTable(acctbl)
	#----------------------------------------------
	def SetupStatusBar(self):
		self.CreateStatusBar(2, wxST_SIZEGRIP)
		#add time and date display to the right corner of the status bar
		self.timer = wxPyTimer(self.Callback_UpdateTime)
		self.Callback_UpdateTime()
		#update every second
		self.timer.Start(1000)
	#----------------------------------------------
	def Callback_UpdateTime(self):
		"""Displays date and local time in the second slot of the status bar"""

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
		# FIXME: we should maximize the amount of title bar information here
		pass
		#myLog.Log(gmLog.lInfo, 'OnIconify')
	#----------------------------------------------
	def OnMaximize(self, event):
		# FIXME: we should change the amount of title bar information here
		pass
		#myLog.Log(gmLog.lInfo,'OnMaximize')
	#----------------------------------------------
	def OnPageChanged(self, event):
		# FIXME: we can maybe change title bar information here
		myLog.Log(gmLog.lInfo, "Notebook page changed - need code here!")
	#----------------------------------------------
	def updateTitle(self, anActivity = None, aPatient = None, aUser = None):
		"""Update title of main window based on template.

		This gives nice tooltips on iconified GnuMed instances.
		User research indicates that in the title bar people want
		the date of birth, not the age, so please stick to this
		convention.

		FIXME: we should go through the global patient cache object
		       to get at the data we need
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

		# set window icon
		icon_bmp_data = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_gui_main)))
		icon = wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)
#==================================================
class AboutFrame (wxFrame, MainFrame):
	"""
	About GnuMed
	"""
	
	__scroll_ctr=0
	__scroll_list=['z', 'e', 'a', 'n', 'r', 'A', ' ', 'o', 'd', 'r', 'a', 'r', 'e', 'G', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', 'r', 'e', 'g', 'r', 'e', 'B', ' ', 'r', 'a', 'm', 'l', 'i', 'H',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 't', 'r', 'e', 'n', 'o', 'B', ' ', 'l',
'e', 'a', 'h', 'c', 'i', 'M', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'd', 'd',
'o', 'D', ' ', 'h', 't', 'e', 'b', 'a', 'z', 'i', 'l', 'E', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', 'r', 'e', 'b', 'u', 'r', 'G', ' ', 't', 'r', 'e', 'b', 'l', 'e', 'g', 'n', 'E', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'd', 'o', 'o', 'w', 'y', 'a', 'H',
' ', 'n', 'a', 'I', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'y', 'r', 'r', 'e', 'T',
' ', 'd', 'r', 'a', 'h', 'c', 'i', 'R', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 
' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', 'l', 'e', 'h', 'c', 'i', 'M', ' ', 'y', 'r', 'r', 'e', 'i', 'h', 'T', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', 'e', 'l', 'l', 'i', 'T', ' ', 's', 'a', 'e', 'r', 'd', 'n', 'A', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']


	def __init__(self, parent, ID, title, pos=wxDefaultPosition, size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
		wxFrame.__init__(self, parent, ID, title, pos, size, style)

		icon = wxEmptyIcon()
		icon.CopyFromBitmap(wxBitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_gui_main))))
		self.SetIcon(icon)

		box = wxBoxSizer(wxVERTICAL)
		box.Add(0,0, 2)
		box.Add(wxStaticText(self, -1, _("Monty the Serpent && the FSF Present")), 0, wxALIGN_CENTRE)
		box.Add(0,0, 3)
		txt=wxStaticText(self, -1, _("GnuMed"))
		txt.SetFont(wxFont(30, wxSWISS, wxNORMAL, wxNORMAL))
		box.Add(txt, 0, wxALIGN_CENTRE)
		box.Add(wxStaticText(self, -1, _("Free eMedicine")), 0, wxALIGN_CENTRE)
		box.Add(0,0, 4)
		box.Add(wxStaticText(self, -1, _("Version X.X.X brought to you by")), 0, wxALIGN_CENTRE)
		box.Add(wxStaticText(self, -1, _("Drs Horst Herb && Karsten Hilbert")), 0, wxALIGN_CENTRE)

		self.changing_txt=wxTextCtrl(self, -1, "", size=(230,20))
		box.Add(self.changing_txt, 0, wxALIGN_CENTRE)
		box.Add(0,0, 1)
		box.Add(wxStaticText(self, -1, _("Please visit http://www.gnumed.org/ for more info")), 0, wxALIGN_CENTRE)
		box.Add(0,0, 1)

		btn = wxButton(self, ID_MENU , _("Close"))
		box.Add(btn,0, wxALIGN_CENTRE)
		box.Add(0,0, 1)
		EVT_BUTTON(btn, ID_MENU, self.OnClose)

		EVT_TIMER(self, -1, self.OnTimer)
		self.timer = wxTimer(self, -1)
		self.timer.Start(40)

		self.SetAutoLayout(true)
 		self.SetSizer(box)
 		self.Layout()

	def OnClose (self, event):
		self.timer.Stop ()
		self.Destroy ()

	def OnTimer(self, evt):
		self.changing_txt.Replace(0,0,self.__scroll_list[self.__scroll_ctr])	# some trickery here
		self.__scroll_ctr=self.__scroll_ctr+1
		if(self.__scroll_ctr>1019):
			self.__scroll_ctr=0

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
		# NOTE: the following only works under Windows according
		# to the docs and bombs under wxPython-2.4 on GTK/Linux
		#frame.Maximize(true)
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
# Revision 1.62  2003-02-01 06:41:03  michaelb
# 'about gnumed' frame added + small change on main window icon
#
# Revision 1.61  2003/01/29 04:26:37  michaelb
# removed import images_gnuMedGP_TabbedLists.py
#
# Revision 1.60  2003/01/14 19:36:04  ncq
# - frame.Maximize() works on Windows ONLY
#
# Revision 1.59  2003/01/14 09:10:19  ncq
# - maybe icons work better now ?
#
# Revision 1.58  2003/01/13 06:30:16  michaelb
# the serpent window-icon was added
#
# Revision 1.57  2003/01/12 17:31:10  ncq
# - catch failing plugins better
#
# Revision 1.56  2003/01/12 01:46:57  ncq
# - coding style cleanup
#
# Revision 1.55  2003/01/11 22:03:30  hinnef
# removed gmConf
#
# Revision 1.54  2003/01/05 10:03:30  ncq
# - code cleanup
# - use new plugin config storage infrastructure
#
# Revision 1.53  2003/01/04 07:43:55  ihaywood
# Popup menus on notebook tabs
#
# Revision 1.52  2002/12/26 15:50:39  ncq
# - title bar fine-tuning
#
# Revision 1.51  2002/11/30 11:09:55  ncq
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
