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
# @change log:
#	10.06.2001 hherb initial implementation, untested
#	01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
#
# @TODO: all testing, most of the implementation
#
############################################################################
"""GNUMed GUI client
The application framework and main window of the
all signing all dancing GNUMed reference client.
"""

# text translation function for localization purposes
import gettext
_ = gettext.gettext

from wxPython.wx import *
from wxPython.html import *
from gmI18N import *
import time, os
import gmLogFrame, gmGuiBroker, gmPG, gmmanual

# widget IDs
exitID = wxNewId()
helpID = wxNewId()
notebookID = wxNewId()
loginID = wxNewId()



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

		self.log = self.CreateLog()
		#self.About()

		#initialize the gui broker
		self.guibroker = gmGuiBroker.GuiBroker()
		#allow access to a safe exit function for all modules in case of "emergencies"
		self.guibroker['EmergencyExit'] = self.CleanExit

		self.SetupStatusBar()
		# allow all modules to access our status bar
		self.guibroker['main.statustext'] = self.SetStatusText

		backend = gmPG.ConnectionPool()
		db = backend.GetConnection('default')
		user = db.query('select CURRENT_USER').getresult()[0][0];
		self.SetTitle(_("You are logged in as [%s]") % user)

		self.SetupPlatformDependent()
		self.SetupToolBar()
		self.CreateMenu()
		self.SetupAccelerators()
		self.RegisterEvents()

		#a top vertical box sizer for the main window
		self.vbox = wxBoxSizer( wxVERTICAL)
		self.guibroker['main.vbox']=self.vbox

		# the "top row", where all important patient data is always on display
		#self.toprowpanel = gmtoprow.gmTopRow(self, 1)
		self.topbox = wxBoxSizer( wxHORIZONTAL)
		self.guibroker['main.topbox']=self.topbox
		self.vbox.AddSizer(self.topbox, 0, wxEXPAND|wxALL, 1)

		self.nb = self.CreateNotebook(self)
		self.guibroker['main.notebook']=self.nb
		self.vbox.Add(self.nb, 1, wxEXPAND|wxALL, 1)

		self.SetSizer( self.vbox )
		self.SetAutoLayout( true )

		#position the Window on the desktop
		self.Centre(wxBOTH)
		self.Show(true)
		self.vbox.Fit( self )
		self.vbox.SetSizeHints( self )
		#self.Lock()



	def SetupPlatformDependent(self):
		#do the platform dependent stuff
		if wxPlatform == '__WXMSW__':
			#windoze specific stuff here
			pass
		elif wxPlatform == '__WXGTK__':
			#GTK (Linux etc.) specific stuff here
			pass
		elif wxPlatform == '__WXMAC__':
			#Mac OS specific stuff here
			pass



	def RegisterEvents(self):
		#register events we want to react to
		EVT_IDLE(self, self.OnIdle)
		EVT_CLOSE(self, self.OnClose)
		EVT_ICONIZE(self, self.OnIconize)
		EVT_MAXIMIZE(self, self.OnMaximize)



	def About(self):
		" A simple 'about' dialog box"
		wxMessageBox(_("Message from GNUMed:\nPlease write a nice About box!"), _("About GNUMed"))



	def SetupAccelerators(self):
		acctbl = wxAcceleratorTable([(wxACCEL_ALT|wxACCEL_CTRL, ord('X'), exitID), \
		                             (wxACCEL_CTRL, ord('H'), helpID)])
		self.SetAcceleratorTable(acctbl)



	def SetupStatusBar(self):
		self.CreateStatusBar(2, wxST_SIZEGRIP)
		#add time and date display to the right corner of the status bar
		self.timer = wxPyTimer(self.Notify)
		#update every second
		self.timer.Start(1000)
		self.Notify()



	def SetupToolBar(self):
		tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER)



	def Notify(self):
		"Displays date and local time in the second slot of the status bar"

		t = time.localtime(time.time())
		st = time.strftime(gmTimeformat, t)
		self.SetStatusText(st,1)



	def CreateNotebook(self, parent):
		"Create the main window notebook. The notebook is where most user interaction happens"

		#create the notebook widget
		nb = wxNotebook(parent, notebookID, wxDefaultPosition, wxSize(200,440),0)
		#make it accessible from withion all GNUMed modules
		self.guibroker['main.notebook'] = nb
		#allow self-sizing according to page sizes
		nbs = wxNotebookSizer(nb)

		#GNUMeds online manual
		pnl = gmmanual.ManualHtmlPanel(nb, self, self.log)
		nb.AddPage(pnl, _("Manual"))

		import gmSQLWindow
		self.SQLWindow = gmSQLWindow.SQLWindow(nb, -1)
		nb.AddPage(self.SQLWindow, _("SQL"))

		import gmCryptoText
		self.txt= gmCryptoText.gmCryptoText(nb, -1, size=(480,300))
		nb.AddPage(self.txt, _("Test Cryptowidget"))



		self.PythonShellWindow(nb)

		EVT_NOTEBOOK_PAGE_CHANGED(self, notebookID, self.OnPageChanged)

		return nb



	def PythonShellWindow(self, notebook):
		""" The magic Python shell window
		To make full use of it, create an instance of gmgui.gmGuiDict
		as the very first thing. Then, you can access most user interface
		elements through this brokering class
		"""

		from wxPython.lib.pyshell import PyShellWindow
		from wxPython.lib.shell import PyShell
		panel = wxPanel(notebook, -1)
		win = PyShell(notebook, globals(), size=(400,400))
		win.Show(true)
		notebook.AddPage(win, "PythonShell")
		return win


	def CreateLog(self):
		"Create a log widget suitable to display system and error messages"

		#create the log output window
		logframe = gmLogFrame.LogFrame(None, -1, _('GNUMed Debug Log'), size=(600,480))
		wxLog_SetActiveTarget(wxLogTextCtrl(logframe.GetLogWidget()))
		return logframe.GetLogWidget()



	def CreateMenu(self):
		"Create the whole menu bar including all menu entries"

		self.mainmenu = wxMenuBar()
		self.guibroker['main.mainmenu']=self.mainmenu
		self.filemenu = wxMenu()
		self.filemenu.Append(exitID, _('E&xit\tAlt-X'), _('Close this GNUMed client'))
		EVT_MENU(self, exitID, self.OnFileExit)
		self.mainmenu.Append(self.filemenu, _('&File'))
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
		wxLogMessage('OnIconify')



	def OnMaximize(self, event):
		wxLogMessage('OnMaximize')



	def OnPageChanged(self, event):
		wxLogMessage("Notebook page changed - need code here!")


###########################################################################


#==================================================

class gmApp(wxApp):

	__backend = None
	__guibroker = None

	def OnInit(self):
		#login first!
		import gmLogin
		self.__backend = gmLogin.Login()
		if self.__backend == None:
			print _("Login attempt unsuccesful\nCan't run GNUMed without database connetcion")
			return false
		# create a static GUI element dictionary;
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()
		#create the main window
		frame = MainFrame(None, -1, _('GNUMed client'), size=(600,480))
		frame.Maximize(true)
		#frame.Unlock()
		frame.Show(true)
		frame.CentreOnScreen(wxBOTH)
		self.SetTopWindow(frame)
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

if __name__ == '__main__':
	main()
