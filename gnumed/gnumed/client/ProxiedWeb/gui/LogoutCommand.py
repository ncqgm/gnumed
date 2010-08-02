#======================================================
class cLogoutCommand:
    def __init__(self, app):
        self.app = app

    def execute(self):
        # TODO: actually send "logout" command to
        # server, resulting in postgresql logout,
        # connection close, or just exit from persistent
        # process would do.
        self.app.logged_out()

