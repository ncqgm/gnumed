# a simple wrapper for the Manual class
from wxPython.wx import *
import gmPlugin
import gmmanual
import images_gnuMedGP_Toolbar

ID_MANUAL = wxNewId ()
ID_MANUALMENU = wxNewId ()

class gmManual (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the manual window
    """
    def name (self):
        return 'ManualPlugin'

    def register (self):
         self.mwm = self.gb['main.manager']
         self.mwm.RegisterLeftSide ('manual', gmmanual.ManualHtmlPanel
                                    (self.mwm, self.gb['main.frame']))
         tb2 = self.gb['main.bottom_toolbar']
         tb2.AddSeparator()
         tool1 = tb2.AddTool(ID_MANUAL,
                             images_gnuMedGP_Toolbar.getToolbar_ManualBitmap(),
                             shortHelpString="Online Manual")
         EVT_TOOL (tb2, ID_MANUAL, self.OnManualTool)
         menu = self.gb['main.helpmenu']
         menu.Append (ID_MANUALMENU, "&Manual", "Online manual")
         EVT_MENU (self.gb['main.frame'], ID_MANUALMENU, self.OnManualTool)
        
    def OnManualTool (self, event):
        self.mwm.Display ('manual')
