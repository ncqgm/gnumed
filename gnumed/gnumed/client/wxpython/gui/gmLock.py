"""
Implements a lock console function for those who need it
"""

from wxPython.wx import *
import gmPlugin
import images_gnuMedGP_Toolbar


ID_LOCKMENU = wxNewId ()
ID_LOCKBUTTON = wxNewId ()

class gmLock (gmPlugin.wxBasePlugin):
    def name (self):
        return 'LockConsolePlugin'

    def register (self):
        menu = self.gb['main.toolsmenu']
        menu.Append (ID_LOCKMENU, "Lock", "Lock Console")
        EVT_MENU (self.gb['main.frame'], ID_LOCKMENU, self.OnLockTool)
	self.tb = self.gb['main.toolbar']
	self.tool = wxBitmapButton (self.tb, ID_LOCKBUTTON, bitmap= images_gnuMedGP_Toolbar.getpadlock_closedBitmap(), style=0)
	self.tool.SetToolTip (wxToolTip('Lock Console'))
	self.tb.AddWidgetLeftBottom (self.tool)
	EVT_BUTTON (self.tool, ID_LOCKBUTTON, self.OnLockTool)

    def unregister (self):
        #tb2 = self.gb['toolbar.Patient']
        #tb2.DeleteTool (ID_BMITOOL)
        menu = self.gb['main.toolsmenu']
        menu.Delete (ID_LOCKMENU)
        
    def OnLockTool (self, event):
	    pass