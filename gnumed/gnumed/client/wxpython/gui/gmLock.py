"""
Implements a lock console function for those who need it
"""

from wxPython.wx import *
import gmPlugin
import images_gnuMedGP_Toolbar


ID_LOCKMENU = wxNewId ()

class gmLock (gmPlugin.wxBasePlugin):
    def name (self):
        return 'LockConsolePlugin'

    def register (self):
        menu = self.gb['main.toolsmenu']
        menu.Append (ID_LOCKMENU, "Lock", "Lock Console")
        EVT_MENU (self.gb['main.frame'], ID_LOCKMENU, self.OnLockTool)
	self.tb = self.gb['main.toolbar']
	self.toolid = self.tb.AddToolRightBottom (images_gnuMedGP_Toolbar.getpadlock_closedBitmap(), 'Lock Console', self.OnLockTool)

    def unregister (self):
        #tb2 = self.gb['toolbar.Patient']
        #tb2.DeleteTool (ID_BMITOOL)
	self.tb.DeleteToolRightBottom (self.toolid)
        menu = self.gb['main.toolsmenu']
        menu.Delete (ID_LOCKMENU)
        
    def OnLockTool (self, event):
	    pass