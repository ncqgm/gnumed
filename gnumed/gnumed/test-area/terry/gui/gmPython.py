# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import images_gnuMedGP_Toolbar

class gmPython (gmPlugin.wxBigPagePlugin):
    """
    Plugin to encapsulate the Python shell
    """

    def name (self):
        return 'Python Shell'

    def MenuInfo (self):
        return ('view', '&Python')

    def GetIcon (self):
        return images_gnuMedGP_Toolbar.getToolbar_PythonBitmap()

    def GetWidget (self, parent):
        from wxPython.lib.pyshell import PyShellWindow
        from wxPython.lib.shell import PyShell
        return PyShell(parent, globals())

                            
