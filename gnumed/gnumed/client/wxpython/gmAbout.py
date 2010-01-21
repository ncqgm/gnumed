# -*- coding: utf8 -*-
#====================================================================
# About GNUmed
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmAbout.py,v $
# $Id: gmAbout.py,v 1.32 2009-01-15 11:35:06 ncq Exp $
__version__ = "$Revision: 1.32 $"
__author__ = "M.Bonert"
__license__ = "GPL"

import zlib, cPickle, sys


import wx


try:
	_('dummy-no-need-to-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

ID_MENU = wx.NewId()
ID_EXIT = wx.NewId()
#====================================================================
class ScrollTxtWin (wx.Window):
	"""
	Scrolling Text!
	"""

	# control parameters
	__scroll_speed=.3 	# pixels/milliseconds (?)
	__delay=500		# milliseconds
	name_list = [
		u'Dr Gerardo Arnaez',
		u'Dr Hilmar Berger',
		u'Michael Bonert',
		u'Dr Elizabeth Dodd',
		u'Engelbert Gruber',
		u'Dr David Guest',
		u'Ian Haywood',
		u'Dr Tony Lembke',
		u'Thierry Michel',
		u'Dr Richard Terry',
		u'Syan J Tan',
		u'Andreas Tille',
		u'Dr Carlos Moro'
	]

	# initializations
	__scroll_ctr=+230
	__name_ctr=1
	__delay_ctr=1

	def __init__ (self, parent):
		wx.Window.__init__(self, parent, -1, size=(230,20), style=wx.SUNKEN_BORDER)
		self.SetBackgroundColour(wx.Colour(255, 255, 255))
		self.__delay_ctr_reset=self.__delay*self.__scroll_speed

		self.moving_txt=wx.StaticText(self, -1, "", size=(230,20), style=wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE)
		self.moving_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.moving_txt.SetLabel(self.name_list[0])

		wx.EVT_TIMER(self, -1, self.OnTimer)
		self.timer = wx.Timer(self, -1)
		#self.timer.Start(self.__scroll_speed)
		self.timer.Start(milliseconds = 1./self.__scroll_speed)

	def OnTimer(self, evt):
		if(self.__scroll_ctr<-2 and self.__delay_ctr<self.__delay_ctr_reset):
			# pause at centre
			self.__delay_ctr=self.__delay_ctr+1
		else:
			self.__scroll_ctr=self.__scroll_ctr-1
			self.moving_txt.MoveXY(self.__scroll_ctr, 0)
		if(self.__scroll_ctr<-230):
			# reset counters
			self.__scroll_ctr=+230
			self.__delay_ctr=1

			# get next name in dict.
			self.moving_txt.SetLabel(self.name_list[self.__name_ctr])
			self.__name_ctr=self.__name_ctr+1
			if(self.__name_ctr>len(self.name_list)-1):
				self.__name_ctr=0

class AboutFrame (wx.Frame):
	"""
	About GNUmed
	"""

	icon_serpent='x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec'

	def __init__(self, parent, ID, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, version='???'):
		wx.Frame.__init__(self, parent, ID, title, pos, size, style)

		icon = wx.EmptyIcon()
		icon.CopyFromBitmap(wx.BitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_serpent))))
		self.SetIcon(icon)

		box = wx.BoxSizer(wx.VERTICAL)
		if wx.Platform == '__WXMAC__':
			box.Add((0,0), 2)
		else:
			box.Add((0,0), 2)
		intro_txt=wx.StaticText(self, -1, _("Monty the Serpent && the FSF Present"))
		intro_txt.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.NORMAL,False,''))
		box.Add(intro_txt, 0, wx.ALIGN_CENTRE)
		if wx.Platform == '__WXMAC__':
			box.Add((0,0), 3)
		else:
			box.Add((0,0), 3)
		gm_txt=wx.StaticText(self, -1, "GNUmed")
		gm_txt.SetFont(wx.Font(30, wx.SWISS, wx.NORMAL, wx.NORMAL))
		box.Add(gm_txt, 0, wx.ALIGN_CENTRE)

		motto_txt=wx.StaticText(self, -1, _("Free eMedicine"))
		motto_txt.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.NORMAL,False,''))
		box.Add(motto_txt, 0, wx.ALIGN_CENTRE)
		if wx.Platform == '__WXMAC__':
			box.Add((0,0), 4)
		else:
			box.Add((0,0), 4)
		ver_txt=wx.StaticText(self, -1, _("Version %s brought to you by") % version)
		ver_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		box.Add(ver_txt, 0, wx.ALIGN_CENTRE)

		admins_txt=wx.StaticText(self, -1, _("Drs Horst Herb && Karsten Hilbert"))
		admins_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		box.Add(admins_txt, 0, wx.ALIGN_CENTRE)

		self.win=ScrollTxtWin(self)
		box.Add(self.win, 0, wx.ALIGN_CENTRE)
		if wx.Platform == '__WXMAC__':
			box.Add((0,0), 1)
		else:
			box.Add((0,0), 1)
		info_txt=wx.StaticText(self, -1, _("Please visit http://www.gnumed.org"))
		info_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		box.Add(info_txt, 0, wx.ALIGN_CENTRE)
		if wx.Platform == '__WXMAC__':
			box.Add((0,0), 1)
		else:
			box.Add((0,0), 1)
		btn = wx.Button(self, ID_MENU , _("Close"))
		box.Add(btn,0, wx.ALIGN_CENTRE)
		if wx.Platform == '__WXMAC__':
			box.Add((0,0), 1)
		else:
			box.Add((0,0), 1)
		wx.EVT_BUTTON(btn, ID_MENU, self.OnClose)

		self.SetAutoLayout(True)
 		self.SetSizer(box)
 		self.Layout()

	def OnClose (self, event):
		self.win.timer.Stop ()
		self.Destroy ()
#====================================================================
class cContributorsDlg(wx.Dialog):
	# people who don't want to be listed here:
	# ...
	contributors = _(
'The following people kindly contributed to GNUmed.\n'
'Please write to <gnumed-devel@gnu.org> to have your\n'
'contribution duly recognized in this list or to have\n'
'your name removed from it for, say, privacy reasons.\n\n'
'Note that this list is sorted alphabetically by last\n'
'name, first name. If the only identifier is an email\n'
'address it is sorted under the first character of\n'
'the user name.\n'
'%s'
) % u"""
== B ===========================================

James Busser, MD, GP
 British Columbia

 - test results handling
 - documentation would be nothing without him
 - encouragment
 - testing on MacOSX

== F ===========================================

Joachim Fischer
 GP Fischer + Lintz
 Fachärzte Allgemeinmedizin
 Wolfschlugen

 - Karteieintragsarten passend für Deutschland

== H ===========================================

Sebastian Hilbert, MD

 - packaging, PR

== L ===========================================

Steffi Leibner, Leipzig

 - Testen, Fehlerberichte
 - Dokumentenvorlage

== N ===========================================

Clemens Nietfeld, Oldenburg

 - Information zur Anbindung von DocConcept

== P ===========================================

Martin Preuss, Hamburg

 - Chipkartenansteuerung

== R ===========================================

Thomas Reus, Düsseldorf

 - Testen, Fehlerberichte
 - Dokumentenvorlage

== T ===========================================

Andreas Tille, Wernigerode

 - Debian packages
 - encouragement, wisdom

"""
	#----------------------------------------------
	def __init__(self, *args, **kwargs):
		wx.Dialog.__init__(self, *args, **kwargs)
		contributor_listing = wx.TextCtrl (
			self,
			-1,
			cContributorsDlg.contributors,
			style = wx.TE_MULTILINE | wx.TE_READONLY,
			size = wx.Size(500, 300)
		)
#		contributor_listing.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
		# arrange widgets
		szr_outer = wx.BoxSizer(wx.VERTICAL)
		szr_outer.Add(contributor_listing, 1, wx.EXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizerAndFit(szr_outer)
		szr_outer.SetSizeHints(self)
		self.Layout()
#====================================================================
# Main
#====================================================================
if __name__ == '__main__':
	# set up dummy app
	class TestApp (wx.App):
		def OnInit (self):
			frame = AboutFrame(None, -1, u"About GNUmed", size=wx.Size(300, 250))
			frame.Show(1)
			return 1
	#---------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		app = TestApp()
		app.MainLoop()

#------------------------------------------------------------
# $Log: gmAbout.py,v $
# Revision 1.32  2009-01-15 11:35:06  ncq
# - cleanup
#
# Revision 1.31  2008/09/09 20:18:06  ncq
# - cleanup
#
# Revision 1.30  2008/07/28 20:41:58  ncq
# - support version in about box
#
# Revision 1.29  2007/09/20 19:34:04  ncq
# - cleanup
#
# Revision 1.28  2007/09/10 12:35:08  ncq
# - make accessible to epydoc
#
# Revision 1.27  2007/08/29 14:37:00  ncq
# - add Clemens Nietfeld
#
# Revision 1.26  2007/08/20 14:22:24  ncq
# - add more helpful people
#
# Revision 1.25  2006/10/23 15:48:07  ncq
# - fix unicode/latin1 string issue
#
# Revision 1.24  2005/12/27 18:46:20  ncq
# - define _()
#
# Revision 1.23  2005/12/24 10:27:42  shilbert
# - gui fixes
#
# Revision 1.22  2005/11/27 14:29:27  shilbert
# - more wx24 --> wx26 cleanup
#
# Revision 1.21  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.20  2005/09/28 15:57:47  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.19  2005/09/27 20:44:58  ncq
# - wx.wx* -> wx.*
#
# Revision 1.18  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.17  2005/07/24 11:35:59  ncq
# - use robustified gmTimer.Start() interface
#
# Revision 1.16  2005/07/18 20:45:25  ncq
# - make contributors dialog slightly larger
#
# Revision 1.15  2005/07/11 16:16:21  ncq
# - display contributor dialog in a proper size
#
# Revision 1.14  2005/07/11 09:04:27  ncq
# - add contributors dialog
#
# Revision 1.13  2005/07/02 18:19:01  ncq
# - one more GnuMed -> GNUmed
#
# Revision 1.12  2005/06/30 10:05:47  cfmoro
# String corrections
#
# Revision 1.11  2005/06/21 04:57:12  rterry
# fix this to run under wxPython26
# -e.g incorrect sizer attributes
#
# Revision 1.10  2005/05/30 09:20:51  ncq
# - add Carlos Moro
#
# Revision 1.9  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.8  2004/06/30 15:56:14  shilbert
# - more wxMAC fixes -they don't stop surfacing :-)
#
# Revision 1.7  2003/11/17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.6  2003/05/17 18:18:19  michaelb
# added $Log statement
#
# 30/01/03: inital version
