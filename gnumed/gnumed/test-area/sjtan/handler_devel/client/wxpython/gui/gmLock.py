"""
Implements a lock console function for those who need it

Dare I say HIPAA ?
"""

from wxPython.wx import *
from wxPython.wx import wxBitmapFromXPMData, wxImageFromBitmap
import cPickle, zlib
import gmPlugin
import images_gnuMedGP_Toolbar


ID_LOCKMENU = wxNewId ()
ID_LOCKBUTTON = wxNewId ()

class gmLock (gmPlugin.wxBasePlugin):
    def name (self):
        return 'LockConsolePlugin'

    def register (self):
        menu = self.gb['main.toolsmenu']
        menu.Append (ID_LOCKMENU, "Lock", "Lock Console")
        EVT_MENU (self.gb['main.frame'], ID_LOCKMENU, self.OnLockTool)
	self.main_toolbar_panel = self.gb['main.toolbar']
	self.tb_lock = wxToolBar(self.main_toolbar_panel,-1,wxDefaultPosition,wxDefaultSize,wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
	self.tool1 = self.tb_lock.AddTool(ID_LOCKBUTTON, getpadlock_closedBitmap(),shortHelpString="Lock gnuMed")
	self.tb_lock.AddControl(wxStaticBitmap(self.tb_lock, -1, getvertical_separator_thinBitmap(), wxDefaultPosition, wxDefaultSize))
	
	#self.tool = wxBitmapButton (self.tb, ID_LOCKBUTTON, bitmap= images_gnuMedGP_Toolbar.getpadlock_closedBitmap(), style=0)
	#self.tool.SetToolTip (wxToolTip('Lock Console'))
	self.main_toolbar_panel.AddWidgetLeftBottom (self.tb_lock)
	EVT_TOOL (self.tb_lock, ID_LOCKBUTTON, self.OnLockTool)

    def unregister (self):
        #tb2 = self.gb['toolbar.Patient']
        #tb2.DeleteTool (ID_BMITOOL)
        menu = self.gb['main.toolsmenu']
        menu.Delete (ID_LOCKMENU)
        
    def OnLockTool (self, event):
	    pass
#----------------------------------------------------------------------
def getpadlock_closedData():
    return cPickle.loads(zlib.decompress(
'x\xda\x85\x90\xb1\n\x03!\x10D\xfb\xfb\n!\x85\xa9\x06,\x12\xad\x15,cq\x8d\
\xedq\xa4\xca\x91\xcd\xffWY5\xcazMFY\x98\xb7\xc3*{=>fY\xb5\xb9+\xbe7e\xf4\
\xb2\xad\x1ajW\xfe\xd8\xf6Wu\x89\xdd\xc5:\x1b\xac\xab^\xb1\x7f\xd0\xfbYM.\
\xcd\xe8b\x88\xadI\xc5{\xe7\x83\xef\xe1Y\x02\x82u\x86\xc8,\xcc\x10\x99\x00jT\
@\x8e\xe2\x0c\xa9\xcc\xa4:\xb7\xc3\xe2\x89Ja\xfa\x83\x0c\x9a\x90\x06\x84P\
\x1a0S?\x02\xa6!\x01G0\xffK\x8a\x99\xe3\x9f\xf2\xf5yK\xd3\xea\xf0\x05\xeaN^\
\xe5' ))

def getpadlock_closedBitmap():
    return wxBitmapFromXPMData(getpadlock_closedData())

def getpadlock_closedImage():
    return wxImageFromBitmap(getpadlock_closedBitmap())

#----------------------------------------------------------------------
def getpadlock_unlockedData():
    return cPickle.loads(zlib.decompress(
'x\xda\x85\x8f=\x0b\xc3 \x10\x86\xf7\xfc\n\xa1\x83\x85\x83\x17\xb3\x04\xe7\
\x06\x1c\x9b!\x8bk\x08\x99\x1az\xfd\xffS\xef\xb4\x1a[\x02}/\x88\xcf\xe3\xf9\
\x91\xeb\xfe\xea\xbb\xd9\xf6\x83\x91O\x06\xdb-\xb3\x85Y\xcdm_\xd6G"\x16\xba\
\x8cN+\xf1\xa4\x1c|\x18]fR\xf6N+\xb1\x11\xbe\xf3sK\x10Ks\xf0\x9fE\r$yvHD\t\
\xbe%"\x03\x9c\xed!\x19\xba\xf2#q"\'\xc9Y\xa7\x84\xd3\x86"AD\xcc\xd0B\x91`\
\x16\'\x01U\x89&Te\xe4R\x8d\xa4\x9aF\xd6\xc6\xf8\xaf\xb39\xb3\xbe\xb3\xbd=\
\xff\x11\xdeR\x1e^\xc8' ))

def getpadlock_unlockedBitmap():
    return wxBitmapFromXPMData(getpadlock_unlockedData())

def getpadlock_unlockedImage():
    return wxImageFromBitmap(getpadlock_unlockedBitmap())

#----------------------------------------------------------------------
def getvertical_separator_thinData():
    return cPickle.loads(zlib.decompress(
'x\xda\xd3\xc8)0\xe4\nV7S04S0V0T\xe7J\x0cVWPHV\xf0\xcb\xcfK\x05s"\x80\x1ce7\
\x0b7g7\x0b0_\x0f\xc47\xb5\x00A\xa8b\xbd\x08\x05\x85\xa1\xc2\xd4\x03\x00\x0c\
\xfe/P' ))

def getvertical_separator_thinBitmap():
    return wxBitmapFromXPMData(getvertical_separator_thinData())

def getvertical_separator_thinImage():
    return wxImageFromBitmap(getvertical_separator_thinBitmap())
#----------------------------------------------------------------------

