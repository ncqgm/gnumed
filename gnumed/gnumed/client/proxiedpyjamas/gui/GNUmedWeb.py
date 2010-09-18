import pyjd # dummy in pyjs

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.DockPanel import DockPanel
from pyjamas.ui import HasAlignment

from LoginPanel import cLoginPanel
from MainPanel import cMainPanel

import GMWevents

#======================================================
class gmTopLevelLayer:
    
    def onModuleLoad(self):

        GMWevents.init_events()
        GMWevents.events.addLoginListener(self) # want to receive onLogin

        self.TEXT_ERROR = "Server Error"
        self.loginpanel = cLoginPanel() # fires logged out on UI load
        self.afterloginpanel = cMainPanel()

        self.maindisplay = DockPanel(
                          HorizontalAlignment=HasAlignment.ALIGN_CENTER,
                          VerticalAlignment=HasAlignment.ALIGN_MIDDLE,
                          BorderWidth=1,
                          Padding=8,
                          Width="100%") 

        RootPanel().add(self.maindisplay)

    def onLogin(self, sender, username, logged_in):
        if logged_in:
            self.logged_in(username)
        else:
            self.logged_out()

    def logged_out(self):
        self.login_username = None
        self.loginpanel.setStatus("") # reset status display
        if self.maindisplay.center is not None:
            self.maindisplay.remove(self.afterloginpanel.getPanel())
        self.maindisplay.add(self.loginpanel.getPanel(), DockPanel.CENTER)

    def logged_in(self, username):
        self.login_username = username
        if self.maindisplay.center is not None:
            self.maindisplay.remove(self.loginpanel.getPanel())
        self.maindisplay.add(self.afterloginpanel.getPanel(), DockPanel.CENTER)

#======================================================
if __name__ == '__main__':
    # for pyjd, set up a web server and load the HTML from there:
    # this convinces the browser engine that the AJAX will be loaded
    # from the same URI base as the URL, it's all a bit messy...
    pyjd.setup("http://127.0.0.1:8080/proxiedpyjamas/gui/public/GNUmedWebPyJD.html")
    app = gmTopLevelLayer()
    app.onModuleLoad()
    pyjd.run()
    
