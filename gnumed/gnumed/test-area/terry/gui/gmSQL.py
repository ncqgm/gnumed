# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import gmSQLWindow
import images_gnuMedGP_Toolbar

ID_SQL = wxNewId ()
ID_SQLMENU = wxNewId ()

class gmSQL (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the cryptowidget
    """
    def name (self):
        return 'SQLPlugin'

    def register (self):
         self.mwm = self.gb['main.manager']
         self.mwm.RegisterLeftSide ('SQL', gmSQLWindow.SQLWindow (self.mwm, -1))
         tb2 = self.gb['main.bottom_toolbar']
         tb2.AddSeparator()
         tool1 = tb2.AddTool(ID_SQL,
                             images_gnuMedGP_Toolbar.getToolbar_SQLBitmap(),
                             shortHelpString="Test SQL terminal")
         EVT_TOOL (tb2, ID_SQL, self.OnSQLTool)
         menu = self.gb['main.viewmenu']
         menu.Append (ID_SQLMENU, "&SQL", "SQL Window")
         EVT_MENU (self.gb['main.frame'], ID_SQLMENU, self.OnSQLTool)
        
    def OnSQLTool (self, event):
        self.mwm.Display ('SQL')
