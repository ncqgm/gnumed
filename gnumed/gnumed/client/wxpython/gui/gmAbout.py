#!/usr/bin/python

#====================================================================
# About GNUMed
# licence: GPL
# Changelog:
# 30/01/03: inital version
#====================================================================
__version__ = "$Revision: 1.4 $"
__author__ = "M.Bonert"

from wxPython.wx import *
from wxPython.calendar import *
import math, zlib, cPickle
import random

ID_MENU = wxNewId ()
ID_EXIT = wxNewId ()
#====================================================================
class AboutFrame (wxFrame):
	"""
	About GnuMed
	"""

	# Monty (2)
	__icons ={"""icon_monty_2""":
'x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec' }

	__scroll_ctr=0
	__scroll_list=['y', 'r', 'r', 'e', 'T', ' ', 'd', 'r', 'a', 'h', 'c', 'i', 'R', ' ', 'r', 'D',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
' ', ' ', ' ', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'', '', '', '', '', '', '', '', '', '']


	def __init__ (self, parent):
		wxFrame.__init__(self, parent, -1, _("About GnuMed"), size=wxSize(300, 250))

		icon = wxEmptyIcon()
		icon.CopyFromBitmap(self.getBitmap())
		self.SetIcon(icon)

		box = wxBoxSizer(wxVERTICAL)
		box.Add(0,0, 2)
		box.Add(wxStaticText(self, -1, _("Monty the Serpent && the FSF Present")), 0, wxALIGN_CENTRE)
		box.Add(0,0, 3)

		txt=wxStaticText(self, -1, _("GnuMed"))
		txt.SetFont(wxFont(30, wxSWISS, wxNORMAL, wxNORMAL))
		box.Add(txt, 0, wxALIGN_CENTRE)
		box.Add(wxStaticText(self, -1, _("Free eMedicine")), 0, wxALIGN_CENTRE)

		box.Add(0,0, 4)
		box.Add(wxStaticText(self, -1, _("Version X.X.X brought to you by")), 0, wxALIGN_CENTRE)
		box.Add(wxStaticText(self, -1, _("Drs Horst Herb && Karsten Hilbert")), 0, wxALIGN_CENTRE)


		self.changing_txt=wxTextCtrl(self, -1, "", size=(230,20))
		box.Add(self.changing_txt, 0, wxALIGN_CENTRE)
		box.Add(0,0, 1)
		box.Add(wxStaticText(self, -1, _("Please visit http://www.gnumed.org/ for more info")), 0, wxALIGN_CENTRE)
		box.Add(0,0, 1)

		btn = wxButton(self, ID_MENU , _("Close"))
		box.Add(btn,0, wxALIGN_CENTRE)
		box.Add(0,0, 1)

		EVT_BUTTON(btn, ID_MENU, self.OnClose)

		EVT_TIMER(self, -1, self.OnTimer)
		self.timer = wxTimer(self, -1)
		self.timer.Start(40)


		self.SetAutoLayout(true)
 		self.SetSizer(box)
 		self.Layout()

	def getBitmap (self):
		# used for:
		# (1) defintion the window icon
		return wxBitmapFromXPMData(cPickle.loads(zlib.decompress( self.__icons[_("""icon_monty_2""")] )))

	def OnClose (self, event):
		self.timer.Stop ()
		self.Destroy ()

	def OnTimer(self, evt):
		self.changing_txt.Replace(0,0,self.__scroll_list[self.__scroll_ctr])	# some trickery here
		self.__scroll_ctr=self.__scroll_ctr+1
		if(self.__scroll_ctr>130):
			self.__scroll_ctr=0

#====================================================================
# Main
#====================================================================
if __name__ == '__main__':
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			frame = AboutFrame(None)
			frame.Show(1)
			return 1
	#---------------------
	import gettext
	_ = gettext.gettext
	gettext.textdomain ('gnumed')
	app = TestApp ()
	app.MainLoop ()
else:
	# plugin()ize
	import gmPlugin

	class gmAbout (gmPlugin.wxBasePlugin):
		def name (self):
			return 'About GnuMed'
		#---------------------
		def register (self):
			menu=self.gb['main.helpmenu']
			menu.Append(ID_MENU, _("About..."), _("About..."))
			EVT_MENU (self.gb['main.frame'], ID_MENU, self.OnTool)

		#---------------------
		def unregister (self):
			menu.self.gb['main.helpmenu']
			menu.Delete (ID_MENU)
		#---------------------
		def OnTool (self, event):
			frame = AboutFrame (self.gb['main.frame'])
			frame.Show (1)
