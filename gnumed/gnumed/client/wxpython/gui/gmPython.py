# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin

class gmPython (gmPlugin.wxNotebookPlugin):
    """
    Plugin to encapsulate the Python shell
    """
    tab_name = _('Python Shell')

    def name (self):
        return gmPython. tab_name

    def MenuInfo (self):
        return ('view', _('&Python'))

    def GetWidget (self, parent):
        from wxPython.lib.PyCrust import shell, version, filling
        win = wxSplitterWindow(parent, -1, size=(600, 300))
        shellWin = shell.Shell(win, -1, introText='The Amazing GnuMed Python Shell!\n')
        fillingWin = filling.Filling(win, -1, size=(600, 180), rootIsNamespace=1)
        win.SplitHorizontally(shellWin, fillingWin)
        return win


