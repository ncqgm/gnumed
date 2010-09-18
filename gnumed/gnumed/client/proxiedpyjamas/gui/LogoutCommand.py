import GMWevents
import Remote

#======================================================
class cLogoutCommand:

    def onMenuItemLogout(self):
        # TODO: actually send "logout" command to
        # server, resulting in postgresql logout,
        # connection close, or just exit from persistent
        # process would do.
        GMWevents.events.onLoginEvent(self, None, False) # indicate logged out
        Remote.svc.logout(self)

    #--------------------------------------------------
    def onRemoteResponse(self, response, request_info):
        method = request_info.method

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

