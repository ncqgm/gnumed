#!/usr/bin/python
#############################################################################
# gmGuiMain - The application framework and main window of the
#             all signing all dancing GNUMed reference client.
#             (WORK IN PROGRESS)
# ---------------------------------------------------------------------------
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	10.06.2001 hherb initial implementation, untested
#	01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
#
# @TODO: all testing, most of the implementation
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
# $Id: gmGuiMain.py,v 1.83 2003-02-14 00:05:36 sjtan Exp $
__version__ = "$Revision: 1.83 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
               S. Tan <sjtan@bigpond.com>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

from wxPython.wx import *
from wxPython.html import *

import sys, time, os, cPickle, zlib

import gmDispatcher, gmSignals, gmGuiBroker, gmPG, gmSQLSimpleSearch, gmSelectPerson, gmLog, gmPlugin, gmCfg
#import handler_loader
import images
import images_gnuMedGP_Toolbar                 #bitmaps for use on the toolbar
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmGP_PatientPicture                     #panel to display patients picture
import gmGP_Toolbar                            #panel with two toolbars on top of the screen
#from wxPython.lib.mixins.listctrl import wxColumnSorterMixin

from gmI18N import gmTimeformat, system_locale

_log = gmLog.gmDefLog
email_logger = None
_cfg = gmCfg.gmDefCfgFile

# widget IDs
ID_ABOUT = wxNewId ()
ID_EXIT = wxNewId ()
ID_HELP = wxNewId ()
ID_NOTEBOOK = wxNewId ()
#==================================================

icon_serpent = \
"""x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec"""

#==================================================
class ProgressDialog (wxProgressDialog):
	def __init__(self, nr_plugins):
		wxProgressDialog.__init__(
			self,
			title = _("GnuMed: loading %s plugins") % nr_plugins,
			message = _("loading list of plugins                    "),
			maximum = nr_plugins,
			parent=None,
			style = wxPD_ELAPSED_TIME
			)
		# set window icon
		icon_bmp_data = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(icon_serpent)))
		icon = wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)
#==================================================
class MainFrame(wxFrame):
	"""GNUmed client's main windows frame.

	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""

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
		EVT_NOTEBOOK_PAGE_CHANGED (self.nb, ID_NOTEBOOK, self.OnNotebookPageChanged)

		# add popup menu to notebook
		EVT_RIGHT_UP(self.nb, self.OnNotebookPopup)

		self.vbox.Add (self.nb, 10, wxEXPAND | wxALL, 1)
		# this list relates plugins to the notebook
		# used to be called 'main.notebook.numbers'
		self.guibroker['main.notebook.plugins'] = []
		# load plugins
		self.LoadPlugins(backend)

		#signal any other modules requireing init.
		gmDispatcher.send( gmSignals.application_init())

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
		_log.Log(gmLog.lData, str(type(plugin_list)) + ": " + str(plugin_list))
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
		nbns = self.guibroker['main.notebook.plugins']
		# get the widget of the currently selected window
		nbns[self.nb.GetSelection ()].unregister ()
		# FIXME:"dropping" means talking to configurator so not reloaded
	#----------------------------------------------
	def OnPluginHide (self, evt):
		# this dictionary links notebook page numbers to plugin objects
		nbns = self.guibroker['main.notebook.plugins']
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
			_log.Log(gmLog.lInfo,'running on GTK (probably Linux)')
		elif wxPlatform == '__WXMAC__':
			#Mac OS specific stuff here
			_log.Log(gmLog.lInfo,'running on a Mac')
		else:
			_log.Log(gmLog.lInfo,'running on an unknown platform (%s)' % wxPlatform)
	#----------------------------------------------
	def LoadPlugins(self, backend):
		# get plugin list
		plugin_list = gmPlugin.GetPluginLoadList('gui')
		if plugin_list is None:
			_log.Log(gmLog.lWarn, "no plugins to load")
			return 1
		nr_plugins = len(plugin_list)

		#  set up a progress bar
		progress_bar = ProgressDialog(nr_plugins)

		#  and load them
		last_plugin = ""
		result = ""
		for idx in range(len(plugin_list)):
			curr_plugin = plugin_list[idx]
			#print "\n\n\n\n%s\n\n\n",curr_plugin

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
				_log.Log(gmLog.lInfo,  'got plugin of type %s' % p.__class__.__name__)
				p.register()
				result = _("success")
			except:
				_log.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info())
				result = _("failed")

			last_plugin = curr_plugin

		progress_bar.Destroy()
	#----------------------------------------------
	def OnNotebookPageChanged(self, event):
		"""Called when notebook changes.

		FIXME: we can maybe change title bar information here
		"""
		new_page_id = event.GetSelection()
		old_page_id = event.GetOldSelection()
		_log.Log(gmLog.lData, 'switching notebook pages: %d -> %d' % (old_page_id, new_page_id))

		# get access to selected page
		new_page = self.guibroker['main.notebook.plugins'][new_page_id]

		# show toolbar
		self.tb.ShowBar(new_page.name())
		# hand focus to plugin page
		new_page.ReceiveFocus()
		event.Skip () # required for MSW
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
		patient = "%(title)s %(firstnames)s %(lastnames)s (%(dob)s) #%(ID)d" % (kwds)
		self.updateTitle(aPatient = patient)
	#----------------------------------------------
	def OnAbout(self, event):
		import gmAbout
		gmAbout=gmAbout.AboutFrame(self, -1, _("About GnuMed"), size=wxSize(300, 250), style = wxMAXIMIZE_BOX)
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
		gmDispatcher.send(gmSignals.application_clean_closing())

				
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
		#_log.Log(gmLog.lInfo, 'OnIconify')
	#----------------------------------------------
	def OnMaximize(self, event):
		# FIXME: we should change the amount of title bar information here
		pass
		#_log.Log(gmLog.lInfo,'OnMaximize')
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
		icon_bmp_data = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(icon_serpent)))
		icon = wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)

#==================================================
class gmApp(wxApp):

	__backend = None
	__guibroker = None
	#----------------------------------------------
	def OnInit(self):
		#do platform dependent stuff
		if wxPlatform == '__WXMSW__':
			# windoze specific stuff here
			_log.Log(gmLog.lInfo,'running on Microsoft Windows')
			# need to explicitely init image handlers on windows
			wxInitAllImageHandlers()

		# create a static GUI element dictionary;
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()
		import gmLogin
		self.__backend = gmLogin.Login()
		if self.__backend is None:
			_log.Log(gmLog.lWarn, "Login attempt unsuccesful. Can't run GnuMed without database connection")
			return false
		# set up language in database
		self.__set_db_lang()
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
	#----------------------------------------------
	def __set_db_lang(self):
		if system_locale is None:
			_log.Log(gmLog.lWarn, "system locale is undefined (probably meaning 'C')")
			return 1

		db_lang = '??_??@????'

		# get read-only connection
		roconn = self.__backend.GetConnection(service = 'default')
		# set up 'read-only' cursor
		rocurs = roconn.cursor()

		# get current database locale
		cmd = "select lang from i18n_curr_lang where owner = CURRENT_USER limit 1;"
		try:
			rocurs.execute(cmd)
		except:
			# assuming the admin knows her stuff this means
			# that language settings are not wanted
			_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
			_log.Log(gmLog.lInfo, 'assuming language settings are not wanted/needed')
			_log.LogException("Cannot get database language.", sys.exc_info(), fatal=0)
			rocurs.close()
			self.__backend.ReleaseConnection('default')
			return None
		result = rocurs.fetchone()

		# release read-only connection
		rocurs.close()
		self.__backend.ReleaseConnection('default')

		if result is not None:
			db_lang = result[0]
		_log.Log(gmLog.lData, "current database locale: [%s]" % db_lang)

		# check if system and db language are different
		if db_lang == system_locale:
			_log.Log(gmLog.lData, 'Database locale (%s) up to date.' % db_lang)
			return 1
		# trim '@variant' part
		no_variant = system_locale.split('@', 1)[0]
		if db_lang == no_variant:
			_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at lang_COUNTRY(@variant) level.' % (db_lang, system_locale))
			return 1
		# trim '_LANG@variant' part
		no_country = system_locale.split('_', 1)[0]
		if db_lang == no_country:
			_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at lang(_COUNTRY@variant) level.' % (db_lang, system_locale))
			return 1

		# no match: ask user
		_log.Log(gmLog.lWarn, 'Database locale [%s] does not match system locale [%s]. Asking user what to do.' % (db_lang, system_locale))

		dlg = wxMessageDialog(
			parent = None,
			message = _("The currently selected database language ('%s') does not match\nthe current system language ('%s').\n\nDo you want to set the database language to '%s' ?") % (db_lang, system_locale, system_locale),
			caption = _('checking database language settings'),
			style = wxYES_NO | wxCENTRE | wxICON_QUESTION
		)
		result = dlg.ShowModal()
		dlg.Destroy()

		if result == wxID_NO:
			_log.Log(gmLog.lInfo, 'User did not want to set database locale. Good luck.')
			return 1

		# get read-write connection
		rwconn = self.__backend.GetConnection(service = 'default', readonly = 0)
		# set up 'read-write' cursor
		rwcurs = rwconn.cursor()

		# try setting database language
		cmd = "select set_curr_lang(%s);"
		for lang in [system_locale, no_variant, no_country]:
			try:
				rwcurs.execute(cmd, lang)
			except:
				_log.LogException(">>>%s<<< failed." % (cmd % lang), sys.exc_info(), fatal=0)
				rwconn.rollback()
				continue
			_log.Log(gmLog.lData, "Successfully set database language to [%s]." % lang)
			rwconn.commit()
			rwcurs.close()
			rwconn.close()
			return 1

		rwcurs.close()
		rwconn.close()
		return None
#=================================================
def main():
	"""GNUmed client written in Python.

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
	_log.AddTarget(aLogTarget)
	_log.Log(gmLog.lInfo, 'Starting up as main module.')
	gb = gmGuiBroker.GuiBroker()
	gb['gnumed_dir'] = os.curdir + "/.."
	main()

_log.Log(gmLog.lData, __version__)

#==================================================
# $Log: gmGuiMain.py,v $
# Revision 1.83  2003-02-14 00:05:36  sjtan
#
# generated files more usable.
#
# Revision 1.82  2003/02/13 08:21:18  ihaywood
# bugfix for MSW
#
# Revision 1.81  2003/02/12 23:45:49  sjtan
#
# removing dead code.
#
# Revision 1.80  2003/02/12 23:37:58  sjtan
#
# now using gmDispatcher and gmSignals for initialization and cleanup.
# Comment out the import handler_loader in gmGuiMain will restore back
# to prototype GUI stage.
#
# Revision 1.79  2003/02/11 12:21:19  sjtan
#
# one more dependency formed , at closing , to implement saving of persistence objects.
# this should be temporary, if a periodic save mechanism is implemented
#
# Revision 1.78  2003/02/09 20:02:55  ncq
# - rename main.notebook.numbers to main.notebook.plugins
#
# Revision 1.77  2003/02/09 12:44:43  ncq
# - fixed my typo
#
# Revision 1.76  2003/02/09 09:47:38  sjtan
#
# handler loading placed here.
#
# Revision 1.75  2003/02/09 09:05:30  michaelb
# renamed 'icon_gui_main' to 'icon_serpent', added icon to loading-plugins-progress-dialog box
#
# Revision 1.74  2003/02/07 22:57:59  ncq
# - fixed extra (% cmd)
#
# Revision 1.73  2003/02/07 14:30:33  ncq
# - setting the db language now works
#
# Revision 1.72  2003/02/07 08:57:39  ncq
# - fixed type
#
# Revision 1.71  2003/02/07 08:37:13  ncq
# - fixed some fallout from SJT's work
# - don't die if select lang from i18n_curr_lang returns None
#
# Revision 1.70  2003/02/07 05:13:59  sjtan
#
# took out the myLog temporary so not broken when I'm running to see if hooks work.
#
# Revision 1.69  2003/02/06 14:02:47  ncq
# - some more logging to catch the set_db_lang problem
#
# Revision 1.68  2003/02/06 12:44:06  ncq
# - curr_locale -> system_locale
#
# Revision 1.67  2003/02/05 12:15:01  ncq
# - not auto-sets the database level language if so desired and possible
#
# Revision 1.66  2003/02/02 09:11:19  ihaywood
# gmDemographics will connect, search and emit patient_selected
#
# Revision 1.65  2003/02/01 21:59:42  michaelb
# moved 'About GnuMed' into module; gmGuiMain version no longer displayed in about box
#
# Revision 1.64  2003/02/01 11:57:56  ncq
# - display gmGuiMain version in About box
#
# Revision 1.63  2003/02/01 07:10:50  michaelb
# fixed scrolling problem
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
