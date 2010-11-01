from pyjamas.builder.Builder import Builder, HTTPUILoader
import GMWevents
import Remote

#======================================================
class cLoginPanel: 
    def __init__(self):
        self.lp = None
        self.TEXT_WAITING = "Waiting for response..."
        HTTPUILoader(self).load("gnumedweb.xml") # calls onUILoaded when done

    def onUILoaded(self, text):
        self.b = Builder(text)
        self.lp = self.b.createInstance("LoginPanel", self)
        GMWevents.events.onLoginEvent(self, None, False) # indicate logged out

    def setStatus(self, txt):
        if self.lp is not None:
            self.lp.status.setText(txt)

    def getPanel(self):
        return self.lp

    #--------------------------------------------------
    def onLoginClicked(self, sender):
        self.setStatus(self.TEXT_WAITING)

        self.lp.button_login.setEnabled(False) # disable whilst checking
        self.try_user = self.lp.CaptionPanel1.Grid1.username.getText()
        passwd = self.lp.CaptionPanel1.Grid1.password.getText() 
        self.lp.CaptionPanel1.Grid1.password.setText("") # reset to blank
        Remote.svc.login(self.try_user, passwd, self)

    #--------------------------------------------------
    def onRemoteResponse(self, response, request_info):
        method = request_info.method

        if method == 'login':
            self.lp.button_login.setEnabled(True) # re-enable after response
            if response:
                # XXX response should really contain the username
                self.setStatus("Login successful: %s" %str(response))
                user = self.try_user
                GMWevents.events.onLoginEvent(self, user, True) 
                self.setStatus("Connected as: %s" % user)
            else:
                self.setStatus("Login failed: %s" %str(response))

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
        self.lp.button_login.setEnabled(True) # re-enable after response
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

