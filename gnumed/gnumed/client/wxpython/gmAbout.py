# -*- coding: utf-8 -*-
"""GNUmed About classes.

This module contains classes for building the About Dialog
(Scrolling text class and the actual About dialog class), as
well as the list of contributors  for the Contributors dialog.
"""
#================================================================
__author__ = "M.Bonert, K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"


# stdlib
import os
import sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _		# do we already have _() ?
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

from Gnumed.pycommon import gmTools

from Gnumed.wxpython import gmGuiHelpers

#====================================================================
class ScrollTxtWin (wx.Window):
	"""
	Scrolling Text!
	"""
	# control parameters
	__scroll_speed=.3 	# pixels/milliseconds (?)
	__delay=1000		# milliseconds
	name_list = [
		'Dr Horst Herb',
		'Karsten Hilbert',
		'Dr Gerardo Arnaez',
		'Dr Hilmar Berger',
		'Michael Bonert',
		'Dr Elizabeth Dodd',
		'Dr David Guest',
		'Ian Haywood',
		'Dr Tony Lembke',
		'Dr Richard Terry',
		'Syan J Tan',
		'Andreas Tille',
		'Dr Carlos Moro',
		'Dr James Busser',
		'Dr Rogerio Luz',
		'Dr Sebastian Hilbert',
		'Dr John Jaarsveld',
		'Uwe Koch Kronberg',
		'Dr Jerzy Luszawski',
		'María Scappini',
		'Marc Angermann',
		'et alii'
	]

	# initializations
	__scroll_ctr = +230
	__name_ctr = 1
	__delay_ctr = 1

	def __init__ (self, parent):
		wx.Window.__init__(self, parent, -1, size=(250,23), style=wx.SUNKEN_BORDER)
		if not gmGuiHelpers.is_probably_dark_theme():
			self.SetBackgroundColour(wx.Colour(255, 255, 255))  # original white
		else:
			pass  # another color for dark theme
		self.__delay_ctr_reset=self.__delay*self.__scroll_speed

		self.moving_txt=wx.StaticText(self, -1, "", size=(250,23), style=wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE)
		self.moving_txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.moving_txt.SetLabel(self.name_list[0])

		#wx.EVT_TIMER(self, -1, self.OnTimer)
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.timer = wx.Timer(self, -1)
		#self.timer.Start(self.__scroll_speed)
		self.timer.Start(milliseconds = int(1./self.__scroll_speed))

	def OnTimer(self, evt):
		if(self.__scroll_ctr<-2 and self.__delay_ctr<self.__delay_ctr_reset):
			# pause at centre
			self.__delay_ctr=self.__delay_ctr+1
		else:
			self.__scroll_ctr=self.__scroll_ctr-1
			self.moving_txt.Move(self.__scroll_ctr, 0)
		if(self.__scroll_ctr<-230):
			# reset counters
			self.__scroll_ctr=+230
			self.__delay_ctr=1

			# get next name in dict.
			self.moving_txt.SetLabel(self.name_list[self.__name_ctr])
			self.__name_ctr=self.__name_ctr+1
			if(self.__name_ctr>len(self.name_list)-1):
				self.__name_ctr=0

#====================================================================
from Gnumed.wxGladeWidgets import wxgAboutFrame

class cAboutFrame (wxgAboutFrame.wxgAboutFrame):
	"""
	About GNUmed
	"""
	def __init__ (
		self,
		parent,
		ID,
		title,
		pos=wx.DefaultPosition,
		size=wx.DefaultSize,
		style=wx.DEFAULT_FRAME_STYLE,
		version_client:str=None,
		version_db:str=None,
		debug:bool=False,
		license:str='GPL v2 or later',
		license_url:str='https://www.gnu.org/licenses/old-licenses/gpl-2.0.html'
	):
		# wx.Frame.__init__(self, parent, ID, title, pos, size, style)
		wxgAboutFrame.wxgAboutFrame.__init__(self, parent, ID, title, pos = pos, size = size, style = style)
		self.SetIcon(gmTools.get_icon(wx = wx))
		logo_fname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bitmaps', 'gnumedlogo.png'))
		self.logo.SetBitmap(wx.Bitmap(logo_fname, wx.BITMAP_TYPE_ANY))
		self.label_version_client.SetLabel (
			_('Client version: %s%s') % (
				version_client,
				gmTools.bool2subst(debug, ' (%s)' % _('debug'), '')
			)
		)
		self.label_version_db.SetLabel (
			_('Database version: %s%s') % (
				version_db,
				gmTools.bool2subst(debug, ' (%s)' % _('debug'), '')
			)
		)
		self.hyperlink_license.LabelText = license
		self.hyperlink_license.URL = license_url
		self.button_close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.win = ScrollTxtWin(self.panel_scroll_container)
		self.panel_scroll_container.GetSizer().Add(self.win, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		self.panel_scroll_container.Layout()
		self.Layout()

	def OnClose (self, event):
		self.win.timer.Stop()
		self.Destroy()


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
) % """
== A ===========================================

Marc ANGERMANN, MD
 Germany

 - Rechnungsvorlage
 - bug reports
 - Debian packaging

== B ===========================================

James BUSSER, MD
 British Columbia

 - test results handling
 - documentation would be nothing without him
 - encouragement, testing, bug reporting
 - testing on MacOSX

Vaibhav BANAIT, MD, DNB, DM
 India

 - bug reports
 - feature suggestions
 - testing

== F ===========================================

Joachim FISCHER
 GP Fischer + Lintz
 Fachärzte Allgemeinmedizin
 Wolfschlugen

 - Karteieintragsarten passend für Deutschland

== H ===========================================

Sebastian HILBERT, MD
 Germany

 - packaging, PR

Anne te HARVIK
 Netherlands

 - Dutch translation

== J ===========================================

John JAARSVELD, MD
 Netherlands

 - lots of help with the visual progress notes
 - Dutch l10n

== K ===========================================

Uwe Koch KRONBERG
 Chile

 - Spanish
 - Chilean demographics

== L ===========================================

Nico LATZER
 Germany

 - invoice handling code

Steffi LEIBNER, Leipzig
 Germany

 - Testen, Fehlerberichte
 - Dokumentenvorlage

Jerzy LUSZAWSKI
 Poland

 - list sorting
 - plugins
 - printing

Rogerio LUZ, Brasil

 - testing, bug reporting
 - SOAP handling discussion
 - providing LaTeX form templates

== N ===========================================

Clemens NIETFELD, Oldenburg

 - Information zur Anbindung von DocConcept

== P ===========================================

Martin PREUSS, Hamburg

 - Chipkartenansteuerung

== R ===========================================

Thomas REUS, Düsseldorf

 - Testen, Fehlerberichte
 - Dokumentenvorlage

== T ===========================================

Andreas TILLE, Wernigerode

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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed', prefer_local_catalog = True)

	from Gnumed.wxpython import gmGuiTest

	#------------------------------------------------------
	def test_about_frame():
		main_frame = gmGuiTest.setup_widget_test_env(patient = None)
		frame_about = cAboutFrame (
			parent = None,
			ID = wx.ID_ANY,
			title = 'Test About GNUmed',
			version_client = 'testing',
			version_db = 'testing',
			debug = True
		)
		frame_about.Centre(wx.BOTH)
		main_frame.otherWin = frame_about
		frame_about.Show(True)
		wx.GetApp().MainLoop()

	#------------------------------------------------------
	test_about_frame()
