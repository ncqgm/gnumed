#======================================================================
# GnuMed patient AU_DrugV01 plugin
# ----------------------------------------------
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.1 $"
__author__ = "S Tan"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmAU_DrugV01
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmAU_DrugV01Plugin(gmPlugin.cNotebookPlugin):
        """Plugin to encapsulate patient AU_DrugV01 window."""

        tab_name = _('AU Drug')

        def name (self):
                return gmAU_DrugV01Plugin.tab_name

        def GetWidget (self, parent):
                self._widget = gmAU_DrugV01.cAU_DrugV01Panel(parent, -1)
                return self._widget

        def MenuInfo (self):
                return ('drug and prescription manager', _('maintain medication and allergy history; prescribe'))

        def can_receive_focus(self):
                # need patient
                if not self._verify_patient_avail():
                        return None
                return 1

#======================================================================
# main
