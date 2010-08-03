import pyjd # dummy in pyjs

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.DockPanel import DockPanel
from pyjamas.ui import HasAlignment
from pyjamas.JSONService import JSONProxy

import jsonobjproxy # just to get it in for pyjs

from LoginPanel import cLoginPanel
from MainPanel import cMainPanel

#======================================================
class gmTopLevelLayer:
    
    def onModuleLoad(self):
        self.TEXT_ERROR = "Server Error"
        self.remote_py = EchoServicePython()
        self.loginpanel = cLoginPanel(self, Spacing=8)
        self.afterloginpanel = cMainPanel(self, Spacing=8)

        self.maindisplay = DockPanel(HorizontalAlignment=HasAlignment.ALIGN_CENTER,
                          VerticalAlignment=HasAlignment.ALIGN_MIDDLE, BorderWidth=1, Padding=8) 

        RootPanel().add(self.maindisplay)

        self.logged_out() # start at logged out

    def logged_out(self):
        self.login_username = None
        self.loginpanel.status.setText("") # reset status display
        if self.maindisplay.center is not None:
            self.maindisplay.remove(self.afterloginpanel)
        self.maindisplay.add(self.loginpanel, DockPanel.CENTER)

    def logged_in(self, username):
        self.login_username = username
        if self.maindisplay.center is not None:
            self.maindisplay.remove(self.loginpanel)
        self.maindisplay.add(self.afterloginpanel, DockPanel.CENTER)

#======================================================
class EchoServicePython(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/JSON",
                ["login",
                "echo", "get_doc_types",
                "get_schema_version",
                "get_documents",
                "doSomething"])

#======================================================
if __name__ == '__main__':
    # for pyjd, set up a web server and load the HTML from there:
    # this convinces the browser engine that the AJAX will be loaded
    # from the same URI base as the URL, it's all a bit messy...
    pyjd.setup("http://127.0.0.1:8080/ProxiedWeb/gui/public/GNUmedWeb.html")
    app = gmTopLevelLayer()
    app.onModuleLoad()
    pyjd.run()
    
