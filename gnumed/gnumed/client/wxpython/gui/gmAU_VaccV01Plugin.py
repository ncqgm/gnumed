#======================================================================
# GnuMed patient AU_VaccV01 plugin
# ----------------------------------------------
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.2 $"
__author__ = "S Tan"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmAU_VaccV01

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmAU_VaccV01Plugin(gmPlugin.cNotebookPlugin):
        """Plugin to encapsulate patient AU_VaccV01 window."""

        tab_name = _('AU Vacc')

        def name (self):
                return gmAU_VaccV01Plugin.tab_name

        def GetWidget (self, parent):
                self._widget = gmAU_VaccV01.cAU_VaccV01Panel(parent, -1)
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
