# a simple wrapper for the Manual class
from wxPython.wx import *
import gmPlugin
import gmmanual
import images_gnuMedGP_Toolbar

class gmManual (gmPlugin.wxBigPagePlugin):
    """
    Plugin to encapsulate the manual window
    """
    def name (self):
        return 'GNUMed online manual'

    def MenuInfo (self):
        return ('help', '&Manual')

    def GetIcon (self):
        return images_gnuMedGP_Toolbar.getToolbar_ManualBitmap()

    def GetWidget (self, parent):
        return gmmanual.ManualHtmlPanel (parent, self.gb['main.frame'])

