# a simple wrapper for the cryptowidget
__version__ = "$Revision: 1.11 $"
__license__ = "GPL"
__author__ =    "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
                 someone before me :-)>"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.wxpython import gmPlugin

class gmPython (gmPlugin.cNotebookPluginOld):
    """
    Plugin to encapsulate the Python shell
    """
    tab_name = _('Python Shell')

    def name (self):
        return gmPython.tab_name

    def MenuInfo (self):
        return ('view', _('&Python'))

    def GetWidget (self, parent):
        #from wx import py
        #from wxPython.lib.PyCrust import shell, version, filling
        win = wxSplitterWindow(parent, -1, size=(600, 300))
        shellWin = py.shell.Shell(win, -1, introText='The Amazing GnuMed Python Shell!\n')
        fillingWin = py.filling.Filling(win, -1, size=(600, 180), rootIsNamespace=1)
        win.SplitHorizontally(shellWin, fillingWin)
        return win


#======================================================
# $Log: gmPython.py,v $
# Revision 1.11  2005-09-26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.10  2004/08/04 17:16:02  ncq
# - wxNotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.9  2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.8  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.7  2004/03/09 00:22:13  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.6  2003/11/07 21:43:13  shilbert
# - PyCrust has been renamed ; use from wx import py
#
