# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import images_gnuMedGP_Toolbar

ID_PYTHON = wxNewId ()
ID_PYTHONMENU = wxNewId ()

class gmPython (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the cryptowidget
    """
    def name (self):
        return 'PythonPlugin'

    def register (self):
         self.mwm = self.gb['main.manager']
         from wxPython.lib.pyshell import PyShellWindow
         from wxPython.lib.shell import PyShell
         win = PyShell(self.mwm, globals())
         self.mwm.RegisterLeftSide ('python', win)
         tb2 = self.gb['main.bottom_toolbar']
         tb2.AddSeparator()
         tool1 = tb2.AddTool(ID_PYTHON,
                             images_gnuMedGP_Toolbar.getToolbar_PythonBitmap(),
                             shortHelpString="Python terminal")
         EVT_TOOL (tb2, ID_PYTHON, self.OnPythonTool)
         menu = self.gb['main.viewmenu']
         menu.Append (ID_PYTHONMENU, "&Python", "Python shell")
         EVT_MENU (self.gb['main.frame'], ID_PYTHONMENU, self.OnPythonTool)
        
    def OnPythonTool (self, event):
        self.mwm.Display ('python')
