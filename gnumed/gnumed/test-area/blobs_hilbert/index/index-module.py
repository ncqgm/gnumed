#!/usr/bin/python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/index/Attic/index-module.py,v $

from wxPython.wx import *
import indexFrame

modules ={'indexFrame': [1, 'Main frame of Application', 'indexFrame.py']}

class BoaApp(wxApp):
	def OnInit(self):
		wxInitAllImageHandlers()
		self.main = indexFrame.create(None)
		#workaround for running in wxProcess
		#self.main.Show();self.main.Hide();self.main.Show()
		self.main.Centre(wxBOTH)
		self.main.Show(true)
		self.SetTopWindow(self.main)
		return true

def main():
	application = BoaApp(0)
	application.MainLoop()

if __name__ == '__main__':
	main()
