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
        from wxPython.lib.PyCrust import shell, version, filling
        win = wxSplitterWindow(parent, -1, size=(600, 300))
        shellWin = shell.Shell(win, -1, introText='The Amazing GnuMed Python Shell!\n')
        fillingWin = filling.Filling(win, -1, size=(600, 180), rootIsNamespace=1)
        win.SplitHorizontally(shellWin, fillingWin)
        return win


