# a plugin for the consultation type
from wxPython.wx import *
import gmPlugin
import gmLog
import gettext
_ = gettext.gettext

ID_TYPE = wxNewId ()

class gmConsultType (gmPlugin.wxBasePlugin):
    """
    Plugin to show a consultation type selector on the toolbar
    """
    def name (self):
        return 'SQLPlugin'

    def register (self):
        tb1 = self.gb['toolbar.Patient']
        tb1.AddSeparator()
        self.types = [_('Home'), _('Surgery'), _('Hospital'), _('Nursing home'), _('Telephone'), _('Other')]
        tb1.Realize ()
        self.select = wxChoice (tb1, ID_TYPE, choices=self.types)
        tb1.AddControl (self.select)
        EVT_CHOICE (self.select, ID_TYPE, self.OnChoice)
        

    def unregister (self):
        pass
    # not sure how to do this
        
    def OnChoice (self, event):
        selection = self.select.GetSelection ()
        gmLog.gmDefLog.Log (gmLog.lInfo, "consultation type is %s" %
                            self.types[selection])
