"""GnuMed single box SOAP notes plugin.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmSingleBoxSoapPlugin.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import gettext
_ = gettext.gettext
from Gnumed.pycommon import gmLog
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython.gmSingleBoxSOAP import gmSingleBoxSOAPPanel

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

from wxPython.wx import *
#================================================================
class gmSingleBoxSoapPlugin(gmPlugin.wxNotebookPlugin):
    tab_name = _("David's SOAP")

    def name (self):
        return gmSingleBoxSoapPlugin.tab_name

    def GetWidget (self, parent):
        self._widget = gmSingleBoxSOAPPanel(parent, -1)
        return self._widget

    def MenuInfo (self):
        return ('tools', _("David's single box SOAP entry"))

    def can_receive_focus(self):
        # need patient
        if not self._verify_patient_avail():
            return None
        return 1
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
    # catch all remaining exceptions
    try:
        application = wxPyWidgetTester(size=(640,480))
        application.SetWidget(cStandalonePanel,-1)
        application.MainLoop()
    except StandardError:
        _log.LogException("unhandled exception caught !", sys.exc_info(), verbose=1)
        # but re-raise them
        raise

#================================================================
# $Log: gmSingleBoxSoapPlugin.py,v $
# Revision 1.8  2004-06-20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.7  2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.6  2004/03/08 23:34:27  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.5  2003/11/17 10:56:41  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.4  2003/07/03 15:25:41  ncq
# - removed unneccary iports
#
# Revision 1.3  2003/06/29 15:21:22  ncq
# - add can_receive_focus() on patient not selected
#
# Revision 1.2  2003/06/26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.1  2003/06/19 16:48:57  ncq
# - this is what David wanted
#
