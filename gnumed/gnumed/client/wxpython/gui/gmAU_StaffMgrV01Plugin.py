#======================================================================
# GnuMed patient AU_StaffMgrV01 plugin
# ----------------------------------------------
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.1 $"
__author__ = "S Tan"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmAU_StaffMgrPanelV01
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmAU_StaffMgrV01Plugin(gmPlugin.cNotebookPlugin):
        """Plugin to encapsulate patient AU_StaffMgrV01 window."""

        tab_name = _('AU Staff Manager')

        def name (self):
                return self.__class__.tab_name

        def GetWidget (self, parent):
                self._widget = gmAU_StaffMgrPanelV01.cAU_StaffMgrPanelV01(parent, -1)
                return self._widget

        def MenuInfo (self):
                return ('manage users', _('manage users'))

        def can_receive_focus(self):
                # need patient
                if not self._verify_patient_avail():
                        return None
                return 1

#======================================================================
# main
