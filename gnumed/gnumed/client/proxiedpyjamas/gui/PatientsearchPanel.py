import pyjd # dummy in pyjs

from pyjamas.ui.TextBox import TextBox
from pyjamas.ui import HasAlignment
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.Image import Image
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button

from WebguiHelpers import cSimplePopup
from PatientSelectDialog import cPatientSelector


import Remote
import GMWevents

#======================================================
class cPatientsearchPanel(HorizontalPanel):
    def __init__(self, **kwargs):
        GMWevents.events.addPatientSelectedListener(self)
        HorizontalPanel.__init__(self, **kwargs)

        self.patientphoto = Image("images/empty-face-in-bust.png")
        self.searchbox = TextBox(Text="<search patient here>")
        self.search_button = Button("Search", self)
        self.lblcave= Label()
        self.lblcave.setText("cave")
        self.allergybox = TextBox(Text = "allergies")
        self.add(self.patientphoto)
        self.add(self.searchbox)
        self.add(self.search_button)
        self.add(self.lblcave)
        self.add(self.allergybox)
        
    #--------------------------------------------------
    def onClick(self, sender):

        # demonstrate proxy & callMethod()
        if sender == self.search_button:
            search_term = self.searchbox.getText()
            id = Remote.svc.search_patient(self, search_term)

    #--------------------------------------------------
    def onRemoteResponse(self, response, request_info):
        method = request_info.method
        if method == 'search_patient':
            if isinstance(response, list):
                GMWevents.events.onPatientSelectedEvent(self, None) 
                selector = cPatientSelector(response)
                return

            # notify listeners of patient details
            GMWevents.events.onPatientSelectedEvent(self, response)

    #--------------------------------------------------
    def onPatientSelected(self, sender, patient):
        if patient is None:
            return
        self.searchbox.setText(patient.description)

    #--------------------------------------------------
    def onRemoteError(self, code, errobj, request_info):
        # onRemoteError gets the HTTP error code or 0 and
        # errobj is an jsonrpc 2.0 error dict:
        #     {
        #       'code': jsonrpc-error-code (integer) ,
        #       'message': jsonrpc-error-message (string) ,
        #       'data' : extra-error-data
        #     }
        message = errobj['message']
        if code != 0:
            #self.status.setText("HTTP error %d: %s" % 
            #                    (code, message))
            msg = "HTTP error %d: %s" % (code, message)
            self.popup = cSimplePopup(msg)
        else:
            code = errobj['code']
            #if message['message'] == 'Cannot request login parameters.':
            #    self.status.setText("You need to log in first")
            #else:
            #    self.status.setText("JSONRPC Error %s: %s" %
            #                    (code, message))
            msg = ("JSONRPC Error %s: %s" % (code, message))
            self.popup = cSimplePopup(msg)

