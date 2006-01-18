#======================================================================
# GnuMed patient AU_AppointV01 plugin
# ----------------------------------------------
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.1 $"
__author__ = "S Tan"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmAU_AppointV01
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmAU_AppointV01Plugin(gmPlugin.cNotebookPlugin):
        """Plugin to encapsulate patient AU_AppointV01 window."""

        tab_name = _('AU Appoint')

        def name (self):
                return self.__class__.tab_name

        def GetWidget (self, parent):
                self._widget = gmAU_AppointV01.cAU_AppointV01(parent, -1)
                return self._widget

        def MenuInfo (self):
                return ('vaccination', _('maintain vaccination history'))

        def can_receive_focus(self):
                # need patient
                if not self._verify_patient_avail():
                        return None
                return 1

#======================================================================
# main
