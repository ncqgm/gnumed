from pyjamas.EventController import Handler

class GNUmedEvents(object):
    def __init__(self):
        self.login = Handler(self, "Login")
        self.patsearch = Handler(self, "PatientSelected")

events = None

def init_events():
    global events
    events = GNUmedEvents()
