# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import gmScheduleAllDoctorsPnl

class gmplNbSchedule(gmPlugin.wxNotebookPlugin):
    """
    Plugin to encapsulate a patient scheduling system
    """

    def name (self):
        return 'Appointments'

    def MenuInfo (self):
        return ('view', '&Appointments')

    def GetWidget (self, parent):
        pnl = gmScheduleAllDoctorsPnl.ScheduleAllDoctorsPnl(parent)
        return pnl



