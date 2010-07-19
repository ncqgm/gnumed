import pyjd # dummy in pyjs

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.Grid import Grid
from pyjamas.JSONService import JSONProxy

import jsonobjproxy # just to get it in for pyjs

class JSONRPCExample:
    def onModuleLoad(self):
        self.TEXT_WAITING = "Waiting for response..."
        self.TEXT_ERROR = "Server Error"
        self.METHOD_ECHO = "Echo"
        self.METHOD_DOCTYPES = "get doc types"
        self.METHOD_UPPERCASE = "get schema"
        self.METHOD_LOWERCASE = "doSomething"
        self.METHOD_GETDOCS = "get documents"
        self.methods = [self.METHOD_ECHO, self.METHOD_DOCTYPES, 
                        self.METHOD_UPPERCASE, self.METHOD_LOWERCASE, 
                        self.METHOD_GETDOCS]

        self.remote_py = EchoServicePython()

        self.status=Label()
        self.username = TextBox(Text="any-doc")
        self.password = TextBox()
        self.dockey = TextBox(Text="12")
        
        self.method_list = ListBox()
        self.method_list.setName("hello")
        self.method_list.setVisibleItemCount(1)
        for method in self.methods:
            self.method_list.addItem(method)
        self.method_list.setSelectedIndex(0)

        method_panel = HorizontalPanel()
        method_panel.add(HTML("Remote string method to call: "))
        method_panel.add(self.method_list)
        method_panel.setSpacing(8)

        self.button_login = Button("Login", self)
        self.button_action = Button("Call Service", self)

        buttons = HorizontalPanel()
        buttons.add(self.button_login)
        buttons.add(self.button_action)
        buttons.setSpacing(8)
        
        info = """<h2>JSON-RPC Example</h2>
        <p>This example demonstrates the calling of server services with
           <a href="http://json-rpc.org/">JSON-RPC</a>.
        </p>
        <p>Choose a service below, and press a the "call service" button to initiate it. An echo service simply sends the exact same text back that it receives.
           </p>"""
        
        panel = VerticalPanel()
        panel.add(HTML(info))
        panel.add(self.username)
        panel.add(self.password)
        panel.add(HTML("Document Key:"))
        panel.add(self.dockey)
        panel.add(method_panel)
        panel.add(buttons)
        panel.add(self.status)
        
        RootPanel().add(panel)

    def onClick(self, sender):
        self.status.setText(self.TEXT_WAITING)
        method = self.methods[self.method_list.getSelectedIndex()]

        # demonstrate proxy & callMethod()
        if sender == self.button_login:
            user = self.username.getText()
            passwd = self.password.getText()
            id = self.remote_py.login(user, passwd, self)
        else:
            if method == self.METHOD_ECHO:
                id = self.remote_py.echo("Hello", self)
            elif method == self.METHOD_DOCTYPES:
                id = self.remote_py.get_doc_types(self)
            elif method == self.METHOD_UPPERCASE:
                id = self.remote_py.get_schema_version(self)
            elif method == self.METHOD_LOWERCASE:
                id = self.remote_py.doSomething(self)
            elif method == self.METHOD_GETDOCS:
                key = int(self.dockey.getText()) # TODO: check it!
                id = self.remote_py.get_documents(key, self)

    def onRemoteResponse(self, response, request_info):
        if request_info.method == 'get_documents':
            grid = Grid()
            grid.resize(len(response)+1, 8)
            grid.setHTML(0, 0, "Comment")
            grid.setHTML(0, 1, "Episode")
            grid.setHTML(0, 2, "When")
            for (row, item) in enumerate(response):
                grid.setHTML(row+1, 0, item.comment)
                grid.setHTML(row+1, 1, item.episode)
                grid.setHTML(row+1, 2, str(item.clin_when))
            RootPanel().add(grid)
        else:
            self.status.setText(str(response))

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

class EchoServicePython(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/JSON",
                ["login",
                "echo", "get_doc_types",
                "get_schema_version",
                "get_documents",
                "doSomething"])

if __name__ == '__main__':
    # for pyjd, set up a web server and load the HTML from there:
    # this convinces the browser engine that the AJAX will be loaded
    # from the same URI base as the URL, it's all a bit messy...
    pyjd.setup("http://127.0.0.1:8080/ProxiedWeb/jsonrpc/public/JSONRPCExample.html")
    app = JSONRPCExample()
    app.onModuleLoad()
    pyjd.run()

