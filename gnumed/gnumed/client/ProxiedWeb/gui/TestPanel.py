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
from pyjamas.ui import HasAlignment

import Remote

#======================================================
class cTestPanel(VerticalPanel):
    def __init__(self, **kwargs):
        VerticalPanel.__init__(self, **kwargs)

        info = """<h2>JSON-RPC Example</h2>
        #<p>This example demonstrates the calling of server services with
        #   <a href="http://json-rpc.org/">JSON-RPC</a>.
        #</p>
        #<p>Choose a service below, and press a the "call service" button to initiate it. An echo service simply sends the exact same text back that it receives.
        #   </p>"""

        self.status=Label()
        self.dockey = TextBox(Text="12")
        self.TEXT_WAITING = "Waiting for response..."

        self.METHOD_ECHO = "Echo"
        self.METHOD_DOCTYPES = "get doc types"
        self.METHOD_UPPERCASE = "get schema"
        self.METHOD_GETINBOX = "get inbox"
        self.METHOD_GETDOCS = "get documents"
        self.methods = [self.METHOD_ECHO, self.METHOD_DOCTYPES, 
                     self.METHOD_UPPERCASE, self.METHOD_GETINBOX, 
                        self.METHOD_GETDOCS]

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

        self.button_action = Button("Call Service", self)

        buttons = HorizontalPanel()
        buttons.add(self.button_action)
        buttons.setSpacing(8)

        panel = VerticalPanel()
        panel.add(HTML(info))
        panel.add(HTML("Primary key of the patient in the database:"))
        panel.add(self.dockey)
        panel.add(method_panel)
        panel.add(buttons)
        panel.add(self.status)
        self.add(panel)

    #--------------------------------------------------
    def onClick(self, sender):
        self.status.setText(self.TEXT_WAITING)
        method = self.methods[self.method_list.getSelectedIndex()]

        # demonstrate proxy & callMethod()
        if sender == self.button_action:
            if method == self.METHOD_ECHO:
                id = Remote.svc.echo("Hello", self)
            elif method == self.METHOD_DOCTYPES:
                id = Remote.svc.get_doc_types(self)
            elif method == self.METHOD_UPPERCASE:
                id = Remote.svc.get_schema_version(self)
            elif method == self.METHOD_GETINBOX:
                id = Remote.svc.get_provider_inbox_data(self)
            elif method == self.METHOD_GETDOCS:
                key = int(self.dockey.getText()) # TODO: check it!
                id = Remote.svc.get_documents(key, self)

    #--------------------------------------------------
    def onRemoteResponse(self, response, request_info):
        method = request_info.method
        if method == 'get_documents':
            grid = Grid()
            grid.resize(len(response)+1, 8)
            grid.setHTML(0, 0, "Comment")
            grid.setHTML(0, 1, "Episode")
            grid.setHTML(0, 2, "When")
            for (row, item) in enumerate(response):
                grid.setHTML(row+1, 0, item.comment)
                grid.setHTML(row+1, 1, item.episode)
                grid.setHTML(row+1, 2, str(item.clin_when))
            #RootPanel().add(grid)
            self.add(grid)
        else:
            self.status.setText(str(response))

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
            if message == 'Cannot request login parameters.':
                self.status.setText("You need to log in first")
            else:
                self.status.setText("JSONRPC Error %s: %s" %
                                (code, message))

