#!/usr/bin/python
#############################################################################
# gmGuiMain - The application framework and main window of the
#             all signing all dancing GNUMed reference client.
#             (WORK IN PROGRESS)
# ---------------------------------------------------------------------------
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
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
#<<<<<<< gmGuiMain.py
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/wxpython/Attic/gmGuiMain.py,v $
# $Id: gmGuiMain.py,v 1.10 2003-11-08 18:12:58 sjtan Exp $
__version__ = "$Revision: 1.10 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
               S. Tan <sjtan@bigpond.com>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

from wxPython.wx import *
from wxPython.html import *

import sys, time, os, cPickle, zlib

import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
email_logger = None

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import gmWhoAmI                                                                 
_whoami = gmWhoAmI.cWhoAmI()

import gmPG
encoding = _cfg.get('backend', 'client encoding')
gmPG.set_default_client_encoding(encoding)
if encoding is None:
	print 'WARNING: option <client encoding> not set in config file'
	_log.Log(gmLog.lWarn, 'you need to set the parameter <client encoding> in the config file')
	_log.Log(gmLog.lWarn, 'on Linux you can determine a likely candidate for the encoding by running "locale charmap"')

from gmI18N import gmTimeformat, system_locale, system_locale_level

import gmDispatcher, gmSignals, gmGuiBroker, gmSQLSimpleSearch, gmSelectPerson, gmPlugin

import gmTopPanel
import gmPatient

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
class gmPluginLoadProgressBar (wxProgressDialog):
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
class gmTopLevelFrame(wxFrame):
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

		#initialize the gui broker
		self.guibroker = gmGuiBroker.GuiBroker()
		self.guibroker['EmergencyExit'] = self._clean_exit
		self.guibroker['main.frame'] = self

		backend = gmPG.ConnectionPool()
		db = backend.GetConnection('default')
		curs = db.cursor()
		curs.execute('select CURRENT_USER;')
		(user,) = curs.fetchone()
		curs.close()
		backend.ReleaseConnection('default')
		self.guibroker['currentUser'] = user

		self.SetupStatusBar()
		self.SetStatusText(_("You are logged in as [%s].") % user)
		self.guibroker['main.statustext'] = self.SetStatusText

		# set window title via template
		self.updateTitle(anActivity = _("idle"), aPatient = _("no patient"), aUser = user)
		#  let others have access, too
		self.guibroker['main.SetWindowTitle'] = self.updateTitle

		self.__setup_platform()
		self.__setup_main_menu()
		self.__setup_accelerators()

		# a vertical box sizer for the main window
		self.vbox = wxBoxSizer(wxVERTICAL)
		#self.vbox.SetMinSize(wxSize(320,240))
		self.guibroker['main.vbox'] = self.vbox

		# create the "top row"
		# important patient data is always there
		# - top panel with toolbars
		self.top_panel = gmTopPanel.cMainTopPanel(self, -1)
		self.guibroker['main.toolbar'] = self.top_panel
		# add to main windows sizer
		# problem:
		# - we want this to NOT grow vertically, hence proportion = 0
		# - but then proportion 10 for the notebook does not mean anything
		self.vbox.Add (self.top_panel, 0, wxEXPAND, 1)

		# now set up the main notebook
		self.nb = wxNotebook (self, ID_NOTEBOOK, size = wxSize(320,240), style = wxNB_BOTTOM)
		self.guibroker['main.notebook'] = self.nb
		self.vbox.Add (self.nb, 10, wxEXPAND | wxALL, 1)

		# this list relates plugins to the notebook
		self.guibroker['main.notebook.plugins'] = []	# (used to be called 'main.notebook.numbers')

		self.__load_plugins(backend)
		self.__register_events()

		# size, position and show ourselves
		self.top_panel.ReFit()
		self.SetAutoLayout(true)
		self.SetSizer(self.vbox)
		self.vbox.Fit(self)
		#don't let the window get too small
		# FIXME: should load last used size here
		# setsizehints only allows minimum size, therefore window can't become small enough
		# effectively we need the font size to be configurable according to screen size
		#self.vbox.SetSizeHints(self)

		# try to get last window size from the backend
		defaultSize = (640,480)
		result, set = gmCfg.getFirstMatchingDBSet( 
			machine = _whoami.getMachine(),
			option = 'main.window.size'
		)
		if not set is None and len(result) == 2:
			currentSize = tuple(result)
		else:
			currentSize = defaultSize
			db = gmPG.ConnectionPool()
			conn = db.GetConnection(service = "default")
			dbcfg = gmCfg.cCfgSQL(
				aConn = conn,
				aDBAPI = gmPG.dbapi
			)
			rwconn = db.GetConnection(service = "default", readonly = 0)
			dbcfg.set(
				machine = _whoami.getMachine(),
				user = _whoami.getUser(),
				option = 'main.window.size',
				value = [currentSize[0],currentSize[1]],
				aRWConn = rwconn
			)
			rwconn.close()
			db.ReleaseConnection(service = "default")
		_log.Log(gmLog.lInfo, 'currSize [%s,%s]' % currentSize)

		# FIXME: size should be stored as a special type [int,int]
		self.SetClientSize(wxSize(int(currentSize[0]),int(currentSize[1])))
# Fit() will re-shrink the window
#		self.Fit()
		self.Centre(wxBOTH)
		self.Show(true)
	#----------------------------------------------
	def __setup_platform(self):
		#do the platform dependent stuff
		if wxPlatform == '__WXMSW__':
			#windoze specific stuff here
			_log.Log(gmLog.lInfo,'running on MS Windows')
		elif wxPlatform == '__WXGTK__':
			#GTK (Linux etc.) specific stuff here
			_log.Log(gmLog.lInfo,'running on GTK (probably Linux)')
		elif wxPlatform == '__WXMAC__':
			#Mac OS specific stuff here
			_log.Log(gmLog.lInfo,'running on Mac OS')
		else:
			_log.Log(gmLog.lInfo,'running on an unknown platform (%s)' % wxPlatform)
	#----------------------------------------------
	def __setup_accelerators(self):
		acctbl = wxAcceleratorTable([
			(wxACCEL_ALT | wxACCEL_CTRL, ord('X'), ID_EXIT),
			(wxACCEL_CTRL, ord('H'), ID_HELP)
		])
		self.SetAcceleratorTable(acctbl)
	#----------------------------------------------
	def __setup_main_menu(self):
		"""Create the main menu entries.

		Individual entries are farmed out to the modules.
		"""
		# create main menu
		self.mainmenu = wxMenuBar()
		self.guibroker['main.mainmenu'] = self.mainmenu
		# menu "File"
		self.menu_file = wxMenu()
		self.menu_file.Append(ID_EXIT, _('E&xit\tAlt-X'), _('Close this GnuMed client'))
		EVT_MENU(self, ID_EXIT, self.OnFileExit)
		self.guibroker['main.filemenu'] = self.menu_file
		# FIXME: this isn't really appropriate
		self.mainmenu.Append(self.menu_file, _("&File"));
		# menu "View"
		self.menu_view = wxMenu()
		self.guibroker['main.viewmenu'] = self.menu_view
		self.mainmenu.Append(self.menu_view, _("&View"));

		# menu "Tools"
		self.menu_tools = wxMenu()
		self.guibroker['main.toolsmenu'] = self.menu_tools
		self.mainmenu.Append(self.menu_tools, _("&Tools"));

		# menu "Reference"
		self.menu_reference = wxMenu()
		self.guibroker['main.referencemenu'] = self.menu_reference
		self.mainmenu.Append(self.menu_reference, _("&Reference"));

		# menu "Help"
		self.menu_help = wxMenu()
		self.menu_help.Append(ID_ABOUT, _("About GnuMed"), "")
		EVT_MENU (self, ID_ABOUT, self.OnAbout)
		self.menu_help.AppendSeparator()
		self.guibroker['main.helpmenu'] = self.menu_help
		self.mainmenu.Append(self.menu_help, "&Help");

		# and activate menu structure
		self.SetMenuBar(self.mainmenu)
	#----------------------------------------------
	def __load_plugins(self, backend):
		# get plugin list
		plugin_list = gmPlugin.GetPluginLoadList('gui')
		print plugin_list, "(*********"
		if plugin_list is None:
			_log.Log(gmLog.lWarn, "no plugins to load")
			return 1
		nr_plugins = len(plugin_list)

		#  set up a progress bar
		progress_bar = gmPluginLoadProgressBar(nr_plugins)

		#  and load them
		last_plugin = ""
		result = ""
		for idx in range(len(plugin_list)):
			curr_plugin = plugin_list[idx]

			progress_bar.Update(
				idx,
				_("previous: %s (%s)\ncurrent (%s/%s): %s") % (
					last_plugin,
					result,
					(idx+1),
					nr_plugins,
					curr_plugin)
			)

			try:
				plugin = gmPlugin.InstPlugin ('gui', curr_plugin, guibroker = self.guibroker, dbbroker = backend)
				_log.Log(gmLog.lInfo,  'got plugin of type %s' % plugin.__class__.__name__)
				if plugin:
					plugin.register()
					result = _("success")
				else:
					_log.Log (gmLog.lErr, "plugin [%s] not loaded as no object, see errors above" % curr_plugin)
			except:
				_log.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info())
				result = _("failed")

			last_plugin = curr_plugin

		progress_bar.Destroy()
	#----------------------------------------------
	# event handling
	#----------------------------------------------
	def __register_events(self):
		"""register events we want to react to"""
		# wxPython events
#		EVT_IDLE(self, self.OnIdle)
		EVT_CLOSE(self, self.OnClose)
		EVT_ICONIZE(self, self.OnIconize)
		EVT_MAXIMIZE(self, self.OnMaximize)
		# - notebook page is about to change
		EVT_NOTEBOOK_PAGE_CHANGING (self.nb, ID_NOTEBOOK, self.OnNotebookPageChanging)
		# - notebook page has been changed
		EVT_NOTEBOOK_PAGE_CHANGED (self.nb, ID_NOTEBOOK, self.OnNotebookPageChanged)
		# - popup menu on right click in notebook
		EVT_RIGHT_UP(self.nb, self.OnNotebookPopup)

		# intra-client signals
		gmDispatcher.connect(self.on_patient_selected, gmSignals.patient_selected())
	#----------------------------------------------
	def OnNotebookPageChanging(self, event):
		"""Called before notebook page change is processed.
		"""
		old_page_id = event.GetOldSelection()
		# FIXME: this is the place to tell the old page to
		# update its local on-disk cache or something,
		# in general, call any "validators" for the
		# old page here
		new_page_id = event.GetSelection()
		if new_page_id != old_page_id:
			new_page = self.guibroker['main.notebook.plugins'][new_page_id]
			if not new_page.can_receive_focus():
				event.Veto()
				return
		else:
			_log.Log(gmLog.lData, 'cannot check if page change needs to be veto()ed')
		event.Skip() # required for MSW
	#----------------------------------------------
	def OnNotebookPageChanged(self, event):
		"""Called when notebook changes.

		FIXME: we can maybe change title bar information here
		"""
		new_page_id = event.GetSelection()
		old_page_id = event.GetOldSelection()
		# get access to selected page
		new_page = self.guibroker['main.notebook.plugins'][new_page_id]
		# can we hand focus to new page ?
		if not new_page.can_receive_focus():
			# we can only hope things will work out anyways
			_log.Log(gmLog.lWarn, "new page cannot receive focus but too late for veto (typically happens on Windows)")
		new_page.ReceiveFocus()
		# activate toolbar of new page
		self.top_panel.ShowBar(new_page.internal_name())
		event.Skip() # required for MSW
	#----------------------------------------------
	def on_patient_selected(self, **kwargs):
		pat = gmPatient.gmCurrentPatient()
		#<DEBUG>
		_log.Log(gmLog.lWarn, "patient changed to [%s]" % pat)
		#</DEBUG>
		try:
			epr = pat['clinical record']
			names = pat['active name']
		except:
			_log.LogException("Unable to process signal. Is gmCurrentPatient up to date yet?", sys.exc_info(), verbose=4)
			return None

		# make sure there's an encounter
		status, encounter = epr.attach_to_encounter(forced = 0)
#<<<<<<< gmGuiMain.py
#		patient = "%s %s (%s)" % (names['first'], names['last'], pat['dob'])
#=======
		patient = "%s %s (%s)" % (names['first'], names['last'], demos.getDOB(aFormat = 'DD.MM.YYYY'))
#>>>>>>> 1.120
		# error ?
		if status == -1:
			msg = _(
				'Can neither attach to an existing encounter\n'
				'nor create a new one for patient\n'
				'"%s".'
			) % patient
			self.__show_error(msg, _('recording patient encounter'))
		# ambigous ?
		elif status == 0:
			# FIXME: better widget -> activate/new buttons
			msg = _(
				'There is a recent encounter recorded for\n'
				'"%s".\n'
				'started : %s\n'
				'affirmed: %s\n'
				'type: %s\tstatus: %s\n'
				'description: %s\n\n'
				'Do you want to reactivate this encounter ?\n'
				'Hitting "No" will start a new one.'
			) % (patient, encounter['type'], encounter['started'], encounter['affirmed'], encounter['status'], encounter['comment'])
			result = self.__show_question(msg, _('recording patient encounter'))
			# attach to existing
			if result == wxID_YES:
				epr.attach_to_encounter(anID = encounter['ID'], forced = 1)
			# create new one
			else:
				status, encounter = epr.attach_to_encounter(forced = 1)
				if status == -1:
					msg = _(
						'Cannot create new encounter for patient\n'
						'"%s".'
					) % patient
					self.__show_error(msg, _('recording patient encounter'))
		#elif 1:
			#success

		# update window title
		fname = names['first']
		if len(fname) > 0:
			fname = fname[:1]
#<<<<<<< gmGuiMain.py
#		patient = "%s %s.%s (%s) #%d" % (pat['title'], fname, names['last'], pat['dob'], int(pat['ID']))
#=======
		patient = "%s %s.%s (%s) #%d" % (demos.getTitle(), fname, names['last'], demos.getDOB(aFormat = 'DD.MM.YYYY'), int(pat['ID']))
#>>>>>>> 1.120
		self.updateTitle(aPatient = patient)
	#----------------------------------------------
	def OnAbout(self, event):
		import gmAbout
		gmAbout = gmAbout.AboutFrame(self, -1, _("About GnuMed"), size=wxSize(300, 250), style = wxMAXIMIZE_BOX)
		gmAbout.Centre(wxBOTH)
		gmTopLevelFrame.otherWin = gmAbout
		gmAbout.Show(true)
		del gmAbout
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
				if not (plugin.internal_name() in self.guibroker['modules.gui'].keys()):
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
	def OnFileExit(self, event):
		"""Invoked from Menu->Exit (calls ID_EXIT handler)."""
		# calls EVT_CLOSE handler
		self.Close()
	#----------------------------------------------
	def OnClose(self, event):
		"""EVT_CLOSE handler.

		- framework still functional
		"""
		# call cleanup helper
		self._clean_exit()
	#----------------------------------------------
	def _clean_exit(self):
		"""Cleanup helper.

		- should ALWAYS be called when this program is
		  to be terminated
		- ANY code that should be executed before a
		  regular shutdown should go in here
		- framework still functional
		"""
		# signal imminent demise to plugins
		gmDispatcher.send(gmSignals.application_closing())
		# handle our own stuff
		self.timer.Stop()
		self.mainmenu = None
		self.Destroy()
	#----------------------------------------------
#	def OnIdle(self, event):
#		"""Here we can process any background tasks
#		"""
#		pass
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
		title = "GnuMed [%s@%s] %s: %s" % (self.title_user, _whoami.getMachine(), self.title_activity, self.title_patient)

		# set it
		self.SetTitle(title)

		# set window icon
		icon_bmp_data = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(icon_serpent)))
		icon = wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)
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
	def Lock(self):
		"""Lock GNUmed client against unauthorized access"""
		# FIXME
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
	# internal helpers
	#----------------------------------------------
	def __show_error(self, aMessage = None, aTitle = ''):
		# sanity checks
		tmp = aMessage
		if aMessage is None:
			tmp = _('programmer forgot to specify error message')

		tmp = tmp + _("\n\nPlease consult the error log for further information !")

		dlg = wxMessageDialog(
			NULL,
			tmp,
			aTitle,
			wxOK | wxICON_ERROR
		)
		dlg.ShowModal()
		dlg.Destroy()
		return 1
	#----------------------------------------------
	def __show_question(self, aMessage = None, aTitle = ''):
		# sanity checks
		tmp = aMessage
		if aMessage is None:
			tmp = _('programmer forgot to specify question')
		dlg = wxMessageDialog(
			NULL,
			tmp,
			aTitle,
			wxYES_NO | wxICON_QUESTION
		)
		result = dlg.ShowModal()
		dlg.Destroy()
		return result
#==================================================
class gmApp(wxApp):

	__backend = None
	__guibroker = None
	#----------------------------------------------
	def OnInit(self):
		self.__setup_platform()

		# create a static GUI element dictionary that
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()

		# connect to backend (implicitely runs login dialog)
		import gmLogin
		self.__backend = gmLogin.Login()
		if self.__backend is None:
			_log.Log(gmLog.lWarn, "Login attempt unsuccesful. Can't run GnuMed without database connection")
			return false

		EVT_QUERY_END_SESSION(self, self._on_query_end_session)
		EVT_END_SESSION(self, self._on_end_session)

		# set up language in database
		self.__set_db_lang()

		# create the main window
		frame = gmTopLevelFrame(None, -1, _('GnuMed client'), (640,440))
		# and tell the app to use it
		self.SetTopWindow(frame)
		#frame.Unlock()
		# NOTE: the following only works under Windows according
		# to the docs and bombs under wxPython-2.4 on GTK/Linux
		#frame.Maximize(true)
		frame.CentreOnScreen(wxBOTH)
		frame.Show(true)
		return true
	#----------------------------------------------
	def OnExit(self):
		"""Called:

		- after destroying all application windows and controls
		- before wxWindows internal cleanup
		"""
		pass
	#----------------------------------------------
	def _on_query_end_session(self):
		print "unhandled event detected: QUERY_END_SESSION"
		_log.Log(gmLog.lWarn, 'unhandled event detected: QUERY_END_SESSION')
		_log.Log(gmLog.lInfo, 'we should be saving ourselves from here')
	#----------------------------------------------
	def _on_end_session(self):
		print "unhandled event detected: END_SESSION"
		_log.Log(gmLog.lWarn, 'unhandled event detected: END_SESSION')
	#----------------------------------------------
	# internal helpers
	#----------------------------------------------
	def __setup_platform(self):
		if wxPlatform == '__WXMSW__':
			# windoze specific stuff here
			_log.Log(gmLog.lInfo,'running on Microsoft Windows')
			# need to explicitely init image handlers on windows
			wxInitAllImageHandlers()
	#----------------------------------------------
	def __set_db_lang(self):
		if system_locale is None:
			_log.Log(gmLog.lWarn, "system locale is undefined (probably meaning 'C')")
			return 1

		db_lang = None

		roconn = self.__backend.GetConnection(service = 'default')
		if roconn is None:
			_log.Log(gmLog.lInfo, 'Cannot connect to database to check database locale setting.')
			return None
		rocurs = roconn.cursor()
		# FIXME: gmPG.run_query()
		# get current database locale
		cmd = "select lang from i18n_curr_lang where owner = CURRENT_USER limit 1;"
		try:
			rocurs.execute(cmd)
		except:
			# assuming the admin knows her stuff this means
			# that language settings are not wanted
			_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
			_log.Log(gmLog.lInfo, 'assuming language settings are not wanted/needed')
			_log.LogException("Cannot get database language.", sys.exc_info(), verbose=0)
			rocurs.close()
			self.__backend.ReleaseConnection('default')
			return None
		result = rocurs.fetchone()
		rocurs.close()
		self.__backend.ReleaseConnection('default')

		if result is None:
			msg = _(
				"There is no language selected in the database.\n"
				"Your system language is currently set to [%s].\n\n"
				"Do you want to set the database language to '%s' ?\n\n"
				"Answering <NO> will remember that decision until\n"
				"the system language is changed. You can also reactivate\n"
				"this inquiry by removing the appropriate ignore option\n"
				"from the configuration file."
			)  % (system_locale, system_locale)
			_log.Log(gmLog.lData, "database locale currently not set")
		else:
			db_lang = result[0]
			msg = _(
				"The currently selected database language ('%s') does\n"
				"not match the current system language ('%s').\n\n"
				"Do you want to set the database language to '%s' ?\n\n"
				"Answering <NO> will remember that decision until\n"
				"the system language is changed. You can also reactivate\n"
				"this inquiry by removing the appropriate ignore option\n"
				"from the configuration file."
			) % (db_lang, system_locale, system_locale)
			_log.Log(gmLog.lData, "current database locale: [%s]" % db_lang)
			# check if we can match up system and db language somehow
			if db_lang == system_locale_level['full']:
				_log.Log(gmLog.lData, 'Database locale (%s) up to date.' % db_lang)
				return 1
			if db_lang == system_locale_level['country']:
				_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at country level.' % (db_lang, system_locale))
				return 1
			if db_lang == system_locale_level['language']:
				_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at language level.' % (db_lang, system_locale))
				return 1
			# no match
			_log.Log(gmLog.lWarn, 'database locale [%s] does not match system locale [%s]' % (db_lang, system_locale))

		# returns either None or a locale string
		ignored_sys_lang = _cfg.get('backend', 'ignored mismatching system locale')
		# are we to ignore *this* mismatch ?
		if system_locale == ignored_sys_lang:
			_log.Log(gmLog.lInfo, 'configured to ignore system-to-database locale mismatch')
			return 1
		# no, so ask user
		dlg = wxMessageDialog(
			parent = None,
			message = msg,
			caption = _('checking database language settings'),
			style = wxYES_NO | wxCENTRE | wxICON_QUESTION
		)
		result = dlg.ShowModal()
		dlg.Destroy()

		if result == wxID_NO:
			_log.Log(gmLog.lInfo, 'User did not want to set database locale. Ignoring mismatch next time.')
			comment = [
				"If the system locale matches this value a mismatch",
				"with the database locale will be ignored.",
				"Remove this option if you want to stop ignoring mismatches.",
			]
			_cfg.set('backend', 'ignored mismatching system locale', system_locale, comment)
			_cfg.store()
			return 1

		rwconn = self.__backend.GetConnection(service = 'default', readonly = 0)
		if rwconn is None:
			_log.Log(gmLog.lInfo, 'Cannot connect to database to set database locale.')
			return None
		rwcurs = rwconn.cursor()
		# try setting database language (only possible if translations exist)
		cmd = "select set_curr_lang(%s);"
		for lang in [system_locale_level['full'], system_locale_level['country'], system_locale_level['language']]:
			try:
				rwcurs.execute(cmd, lang)
			except:
				_log.LogException(">>>%s<<< failed." % (cmd % lang), sys.exc_info(), verbose=0)
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
	#----------------------------------------------
	def __show_question(self, aMessage = None, aTitle = ''):
		# sanity checks
		tmp = aMessage
		if aMessage is None:
			tmp = _('programmer forgot to specify question')
		dlg = wxMessageDialog(
			NULL,
			tmp,
			aTitle,
			wxYES_NO | wxICON_QUESTION
		)
		result = dlg.ShowModal()
		dlg.Destroy()
		return result
#=================================================
def main():
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

#==================================================
# $Log: gmGuiMain.py,v $
# Revision 1.10  2003-11-08 18:12:58  sjtan
#
# resurrected gmDemographics: will manage multiple addresses, to update existing identities.
#
# Revision 1.121  2003/10/31 23:23:17  ncq
# - make "attach to encounter ?" dialog more informative
#
# Revision 1.120  2003/10/27 15:53:10  ncq
# - getDOB has changed
#
# Revision 1.119  2003/10/26 17:39:00  ncq
# - cleanup
#
# Revision 1.118  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# syncing with main tree.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.115  2003/10/19 12:17:16  ncq
# - just cleanup
#
# Revision 1.114  2003/10/13 21:00:29  hinnef
# -added main.window.size config parameter (will be set on startup)
#
# Revision 1.113  2003/09/03 17:32:41  hinnef
# make use of gmWhoAmI
#
# Revision 1.112  2003/07/21 21:05:56  ncq
# - actually set database client encoding from config file, warn if missing
#
# Revision 1.111  2003/07/07 08:34:31  ihaywood
# bugfixes on gmdrugs.sql for postgres 7.3
#
# Revision 1.110  2003/06/26 22:28:50  ncq
# - need to define self.nb before using it
# - reordered __init__ for clarity
#
# Revision 1.109  2003/06/26 21:38:28  ncq
# - fatal->verbose
# - ignore system-to-database locale mismatch if user so desires
#
# Revision 1.108  2003/06/25 22:50:30  ncq
# - large cleanup
# - lots of comments re method call order on application closing
# - send application_closing() from _clean_exit()
# - add OnExit() handler, catch/log session management events
# - add helper __show_question()
#
# Revision 1.107  2003/06/24 12:55:40  ncq
# - typo: it's qUestion, not qestion
#
# Revision 1.106  2003/06/23 22:29:59  ncq
# - in on_patient_selected() add code to attach to a
#   previous encounter or create one if necessary
# - show_error/quesion() helper
#
# Revision 1.105  2003/06/19 15:27:53  ncq
# - also process EVT_NOTEBOOK_PAGE_CHANGING
#   - veto() page change if can_receive_focus() is false
#
# Revision 1.104  2003/06/17 22:30:41  ncq
# - some cleanup
#
# Revision 1.103  2003/06/10 09:55:34  ncq
# - don't import handler_loader anymore
#
# Revision 1.102  2003/06/01 14:34:47  sjtan
#
# hopefully complies with temporary model; not using setData now ( but that did work).
# Please leave a working and tested substitute (i.e. select a patient , allergy list
# will change; check allergy panel allows update of allergy list), if still
# not satisfied. I need a working model-view connection ; trying to get at least
# a basically database updating version going .
#
# Revision 1.101  2003/06/01 12:36:40  ncq
# - no way cluttering INFO level log files with arbitrary patient data
#
# Revision 1.100  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.99  2003/05/12 09:13:31  ncq
# - SQL ends with ";", cleanup
#
# Revision 1.98  2003/05/10 18:47:08  hinnef
# - set 'currentUser' in GuiBroker-dict
#
# Revision 1.97  2003/05/03 14:16:33  ncq
# - we don't use OnIdle(), so don't hook it
#
# Revision 1.96  2003/04/28 12:04:09  ncq
# - use plugin.internal_name()
#
# Revision 1.95  2003/04/25 13:03:07  ncq
# - just some silly whitespace fix
#
# Revision 1.94  2003/04/08 21:24:14  ncq
# - renamed gmGP_Toolbar -> gmTopPanel
#
# Revision 1.93  2003/04/04 20:43:47  ncq
# - take advantage of gmCurrentPatient()
#
# Revision 1.92  2003/04/03 13:50:21  ncq
# - catch more early results of connection failures ...
#
# Revision 1.91  2003/04/01 15:55:24  ncq
# - fix setting of db lang, better message if no lang set yet
#
# Revision 1.90  2003/04/01 12:26:04  ncq
# - add menu "Reference"
#
# Revision 1.89  2003/03/30 00:24:00  ncq
# - typos
# - (hopefully) less confusing printk()s at startup
#
# Revision 1.88  2003/03/29 14:12:35  ncq
# - set minimum size to 320x240
#
# Revision 1.87  2003/03/29 13:48:42  ncq
# - cleanup, clarify, improve sizer use
#
# Revision 1.86  2003/03/24 17:15:05  ncq
# - slightly speed up startup by using pre-calculated system_locale_level dict
#
# Revision 1.85  2003/03/23 11:46:14  ncq
# - remove extra debugging statements
#
# Revision 1.84  2003/02/17 16:20:38  ncq
# - streamline imports
# - comment out app_init signal dispatch since it breaks
#
# Revision 1.83  2003/02/14 00:05:36  sjtan
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
# @change log:
#	10.06.2001 hherb initial implementation, untested
#	01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
