# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin

class gmPython (gmPlugin.wxNotebookPlugin):
    """
    Plugin to encapsulate the Python shell
    """

    def name (self):
        return 'Python Shell'

    def MenuInfo (self):
        return ('view', '&Python')

    def GetWidget (self, parent):
        from wxPython.lib.pyshell import PyShellWindow
        from wxPython.lib.shell import PyShell
        return PyShell(parent, globals())

                            
