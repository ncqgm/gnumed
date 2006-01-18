
import wx
from  pyPgSQL import PgSQL as dbapi
from  Gnumed.wxGladeWidgets.wxgAU_AdminLoginV01 import cAU_AdminLoginDialogV01 as Base

class cAU_AdminLoginDialogV01(Base):
    def __init__(self, *args, **kwds):
    	Base.__init__(self, *args, **kwds)

    def admin_login_ok(self, event): # wxGlade: cAU_AdminLoginDialogV01.<event_handler>
        #print "Event handler `admin_login_ok' not implemented!"
	self.DSN = ":".join( [ str(x.GetValue()).strip() for x in [ self.text_ctrl_3, self.text_ctrl_4, self.text_ctrl_5, self.text_ctrl_1, self.text_ctrl_2 ] ] )
	self.EndModal( wx.ID_OK)
        event.Skip()

    def get_connection(self):
    	c = dbapi.connect(self.DSN)
	return c

# end of class cAU_AdminLoginDialogV01


