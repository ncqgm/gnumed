# a simple wrapper for the cryptowidget
__version__ = "$Revision: 1.7 $"
__license__ = "GPL"
__author__ =    "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
                 someone before me :-)>"
from wxPython.wx import *
from Gnumed.wxpython import gmPlugin

class gmPython (gmPlugin.wxNotebookPlugin):
    """
    Plugin to encapsulate the Python shell
    """
    tab_name = _('Python Shell')

    def name (self):
        return gmPython.tab_name

    def MenuInfo (self):
        return ('view', _('&Python'))

    def GetWidget (self, parent):
        from wx import py
        #from wxPython.lib.PyCrust import shell, version, filling
        win = wxSplitterWindow(parent, -1, size=(600, 300))
        shellWin = py.shell.Shell(win, -1, introText='The Amazing GnuMed Python Shell!\n')
        fillingWin = py.filling.Filling(win, -1, size=(600, 180), rootIsNamespace=1)
        win.SplitHorizontally(shellWin, fillingWin)
        return win


#======================================================
# $Log: gmPython.py,v $
# Revision 1.7  2004-03-09 00:22:13  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.6  2003/11/07 21:43:13  shilbert
# - PyCrust has been renamed ; use from wx import py
#
