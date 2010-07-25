from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.PasswordTextBox import PasswordTextBox
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.Image import Image
from pyjamas.ui.HTML import HTML
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.CaptionPanel import CaptionPanel

#======================================================
class cLoginPanel(VerticalPanel): 
    def __init__(self, app, **kwargs):
        self.app = app
        VerticalPanel.__init__(self, **kwargs)

        self.status=Label()
        self.TEXT_WAITING = "Waiting for response..."
        
        self.lblusername = Label()
        self.lblusername.setText("username")
        self.username = TextBox(Text="any-doc")
        self.lblpassword = Label()
        self.lblpassword.setText("password")
        self.password = PasswordTextBox(Text="")
        self.button_login = Button("Login", self)
        self.gnumedlogo = Image("images/gnumedlogo.png")

        usernamepanel = HorizontalPanel()
        usernamepanel.add(self.lblusername)
        usernamepanel.add(self.username)

        passwdpanel = HorizontalPanel()
        passwdpanel.add(self.lblpassword)
        passwdpanel.add(self.password)

        credentialpanel = VerticalPanel()
        credentialpanel.add(usernamepanel)
        credentialpanel.add(passwdpanel)

        captionpanel = CaptionPanel("GNUmed Default 0.7.7", credentialpanel)

        panel = VerticalPanel()
        panel.add(self.gnumedlogo)
        panel.add(captionpanel)
        panel.add(self.button_login)
        panel.add(self.status)
        self.add(panel)

    #--------------------------------------------------
    def onClick(self, sender):
        self.status.setText(self.TEXT_WAITING)

        if sender == self.button_login:
            self.button_login.setEnabled(False) # disable whilst checking
            self.try_user = self.username.getText()
            passwd = self.password.getText() 
            self.password.setText("") # reset to blank
            self.app.remote_py.login(self.try_user, passwd, self)

    #--------------------------------------------------
    def onRemoteResponse(self, response, request_info):
        method = request_info.method

        if method == 'login':
            self.button_login.setEnabled(True) # re-enable after response
            if response:
                # XXX response should really contain the username
                self.status.setText("Login successful: %s" %str(response))
                user = self.try_user
                self.app.logged_in(user)
                self.status.setText("Connected as: %s" % user)
            else:
                self.status.setText("Login failed: %s" %str(response))

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
            self.status.setText("HTTP error %d: %s" % 
                                (code, message))
        else:
            code = errobj['code']
            if message['message'] == 'Cannot request login parameters.':
                self.status.setText("You need to log in first")
            else:
                self.status.setText("JSONRPC Error %s: %s" %
                                (code, message))

