# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import gmSelectPerson

_description = """This panel allows to select the active patient.
The user can enter any number of letters of the surname only or
of the first name and the surname (in that order). Depending on the 
'case sensitive' switch on the search panel, the search will be
performed case sensitive or not, and all matching patients will be
displayed in a list control.
From there, a patient can be selected by double click or selection
via keyboard (arrows move the cursor, space selects, CR activates
the selection).
Once a patient selection has been activated, the signal 
gmSignals.patient_selected() will be sent to the dispatcher.
Keyword arguments passed to the dispatcher contain not only the 
patient's ID, but also all fields of the view v_basic_person,
accessible via the field names"""

class gmplNbPatientSelector(gmPlugin.wxNotebookPlugin):
    """
    Plugin to encapsulate a patient selection panel
    """

    def name (self):
        return 'Patient Selector'

    def description(self):
        return _description

    def MenuInfo (self):
        return ('file', '&Select Patient')

    def GetWidget (self, parent):
        try:
            pnl = gmSelectPerson.DlgSelectPerson(parent)
        except:
            print "Failed to load patient selection panel"
	    return None
        return pnl



