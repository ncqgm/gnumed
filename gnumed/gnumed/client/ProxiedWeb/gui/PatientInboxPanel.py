from pyjamas.builder.Builder import Builder, HTTPUILoader
from pyjamas.ui.SimplePanel import SimplePanel
from InboxGrid import fill_grid_messages
import GMWevents
import Remote

#======================================================
class cPatientInboxPanel(SimplePanel): 
    """ Patient Inbox Messages.

        derives from SimplePanel so that it can be added immediately to
        cPatientsummaryPanel and then, when HTTPUILoader picks up the XML
        file (asynchronously), the PatientInbox instance can be added then.
    """
    def __init__(self, **kwargs):
        SimplePanel.__init__(self, **kwargs)
        self.pp = None
        self.active_patient_messages = []
        self.active_patient_id = None
        self.TEXT_WAITING = "Waiting for response..."
        HTTPUILoader(self).load("gnumedweb.xml") # calls onUILoaded when done

    #--------------------------------------------------
    def onUILoaded(self, text):
        self.b = Builder(text)
        self.pp = self.b.createInstance("PatientInbox", self)
        GMWevents.events.addPatientSelectedListener(self)
        GMWevents.events.addLoginListener(self)
        self.add(self.pp)

    #--------------------------------------------------
    def getPanel(self):
        return self.pp

    #--------------------------------------------------
    def fill_grid(self):
        fill_grid_messages(self.pp.grid, self.active_patient_messages)
                
    #--------------------------------------------------
    def onPatientSelected(self, sender, patient_info):
        if self.logged_in and patient_info is not None:
            self.active_patient_id = patient_info.pk_identity
            self.active_patient_messages = None
            Remote.svc.get_patient_messages(self.active_patient_id, self)
        else:
            self.active_patient_id = None
            self.active_patient_messages = []
        print "patient id", self.active_patient_id
        self.fill_grid()

    #--------------------------------------------------
    def onLogin(self, sender, username, logged_in):
        self.logged_in = logged_in

    #--------------------------------------------------
    def onRemoteResponse(self, response, request_info):
        method = request_info.method

        if method == 'get_provider_inbox_data':
            self.messages = response
            self.fill_grid()
        elif method == 'get_patient_messages':
            self.active_patient_messages = response
            self.fill_grid()

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
            self.setStatus("HTTP error %d: %s" % 
                                (code, message))
        else:
            code = errobj['code']
            if message['message'] == 'Cannot request login parameters.':
                self.setStatus("You need to log in first")
            else:
                self.setStatus("JSONRPC Error %s: %s" %
                                (code, message))

