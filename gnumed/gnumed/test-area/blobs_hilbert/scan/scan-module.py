#!/usr/bin/env python
#Boa:PyApp:main

from wxPython.wx import *
import scanFrame

modules ={'scanFrame': [0, '', 'scanFrame.py']}

class BoaApp(wxApp):
    def OnInit(self):
        wxInitAllImageHandlers()
        self.main = scanFrame.create(None)
        #workaround for running in wxProcess
        self.main.Show();self.main.Hide();self.main.Show() 
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
