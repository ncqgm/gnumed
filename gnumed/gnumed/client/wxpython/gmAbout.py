# -*- coding: utf8 -*-
#====================================================================
# About GNUmed
#====================================================================
__version__ = "$Revision: 1.35 $"
__author__ = "M.Bonert"
__license__ = "GPL"

import sys


import wx


from Gnumed.pycommon import gmTools

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
		u'Dr Horst Herb',
		u'Karsten Hilbert',
		u'Dr Gerardo Arnaez',
		u'Dr Hilmar Berger',
		u'Michael Bonert',
		u'Dr Elizabeth Dodd',
		u'Dr David Guest',
		u'Ian Haywood',
		u'Dr Tony Lembke',
		u'Dr Richard Terry',
		u'Syan J Tan',
		u'Andreas Tille',
		u'Dr Carlos Moro',
		u'Dr James Busser',
		u'Dr Rogerio Luz',
		u'Dr Sebastian Hilbert',
		u'Dr John Jaarsveld',
		u'Uwe Koch Kronberg',
		u'et alii'
	]

	# initializations
	__scroll_ctr = +230
	__name_ctr = 1
	__delay_ctr = 1

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
	def __init__(self, parent, ID, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, version='???', debug=False):
		wx.Frame.__init__(self, parent, ID, title, pos, size, style)

		self.SetIcon(gmTools.get_icon(wx = wx))

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
		ver_txt=wx.StaticText (
			self,
			-1,
			_('Version %s%s brought to you by') % (
				version,
				gmTools.bool2subst(debug, u' (%s)' % _('debug'), u'')
			)
		)
		ver_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		box.Add(ver_txt, 0, wx.ALIGN_CENTRE)

		admins_txt=wx.StaticText(self, -1, "")
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
== A ===========================================

Marc Angermann, MD
 Germany

 - Rechnungsvorlage
 - bug reports

== B ===========================================

James Busser, MD
 British Columbia

 - test results handling
 - documentation would be nothing without him
 - encouragement, testing, bug reporting
 - testing on MacOSX

== F ===========================================

Joachim Fischer
 GP Fischer + Lintz
 Fachärzte Allgemeinmedizin
 Wolfschlugen

 - Karteieintragsarten passend für Deutschland

== H ===========================================

Sebastian Hilbert, MD
 Germany

 - packaging, PR

Anne te Harvik
 Netherlands

 - Dutch translation

== J ===========================================

John Jaarsveld, MD
 Netherlands

 - lots of help with the visual progress notes
 - Dutch l10n

== K ===========================================

Uwe Koch Kronberg
 Chile

 - Spanish
 - Chilean demographics

== L ===========================================

Nico Latzer
 Germany

 - invoice handling code

Steffi Leibner, Leipzig
 Germany

 - Testen, Fehlerberichte
 - Dokumentenvorlage

Rogerio Luz, Brasil

 - testing, bug reporting
 - SOAP handling discussion
 - providing LaTeX form templates

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

