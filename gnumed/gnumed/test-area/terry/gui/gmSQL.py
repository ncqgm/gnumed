# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import gmSQLWindow
import images_gnuMedGP_Toolbar

class gmSQL (gmPlugin.wxBigPagePlugin):
    """
    Plugin to encapsulate the cryptowidget
    """
    def name (self):
        return 'SQL Plugin'


    def MenuInfo (self):
        return ('view', '&SQL')

    def GetIcon (self):
        return images_gnuMedGP_Toolbar.getToolbar_SQLBitmap()

    def GetWidget (self, parent):
        return gmSQLWindow.SQLWindow (parent, -1)
