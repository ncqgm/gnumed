#!/usr/bin/env python

"""GnuMed onscreen Snellen Chart emulator.

FIXME: store screen size
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmSnellen.py,v $
# $Id: gmSnellen.py,v 1.14 2005-09-24 09:17:29 ncq Exp $
__version__ = "$Revision: 1.14 $"
__author__ = "Ian Haywood, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import math, random

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N
#from Gnumed.wxpython import gmPlugin

ID_SNELLENMENU = wx.wxNewId()
ID_SNELLENBUTTON = wx.wxNewId()

#============================================================================
class cSnellenChart(wx.wxFrame):

	def convert (self, X,Y):
		"""Converts a pair of co-ordinates from block co-ords to real.

		X, Y	-- define top-left corner of current character
		"""
		if self.mirror:
			X = 5-X
		return wx.wxPoint(
			(X * self.blockX) + self.startX,
			(Y * self.blockY) + self.startY
		)

	def rect (self, x1, y1, x2, y2):
		"""
		Draw a rectangle
		"""
		x1, y1 = self.convert (x1, y1)
		x2, y2 = self.convert (x2, y2)
		width = x2 - x1
		if width < 0:
			width = -width
			x = x2
		else:
			x = x1
		height = y2 - y1
		if height < 0:
			height = -height
			y = y2
		else:
			y = y1
		self.dc.DrawRectangle (x, y, width, height)

	def straight (self, x1, y1, x2, y2, width = 1):
		"""
		Draws straight descending letter-stroke, (x1, y1) is top-left,
		(x2, y2) is bottom left point
		"""
		
		list = [self.convert (x1, y1), self.convert (x1+width, y1),
		self.convert (x2+width, y2), self.convert (x2, y2)]
		self.dc.DrawPolygon (list)

	def reverse (self):
		"""
		Swap fore- and background pens
		"""
		background = self.dc.GetBackground ()
		foreground = self.dc.GetBrush ()
		self.dc.SetBrush (background)
		self.dc.SetBackground (foreground)
		

	def arc (self, x, y, arm, start, end):
		"""
		Draws an arc-stroke, 1 unit wide, subtending (x, y), the outer
		distance is arm, between start and end angle
		"""
		topx, topy = self.convert (x-arm, y-arm)
		botx, boty = self.convert (x+arm, y+arm)
		width = botx - topx
		if width < 0:
			width = -width
			t = botx
			botx = topx
			topx = t
		height = boty - topy
		self.dc.DrawEllipticArc(topx, topy, width, height, start, end)
		# now do wedge as background, to give arc pen-stroke
		arm -= 1
		self.reverse ()
		topx, topy = self.convert (x-arm, y-arm)
		botx, boty = self.convert (x+arm, y+arm)
		width = botx - topx
		if width < 0:
			width = -width
			t = botx
			botx = topx
			topx = t
		height = boty- topy
		self.dc.DrawEllipticArc(topx, topy, width, height, start, end)
		self.reverse ()

	def O (self):
		"""
		Draws the letter O
		"""
		self.arc (2.5, 2.5, 2.5, 0, 360)

	def Q (self):
		self.O ()
		self.straight (2.6, 3, 4, 5)

	def C (self):
		if self.mirror:
			self.arc (2.5, 2.5, 2.5, 140, -140)
		else:
			self.arc (2.5, 2.5, 2.5, 40, 320)

	def G (self):
		if self.mirror:
			self.arc (2.5, 2.5, 2.5, 140, -150)
		else:
			self.arc (2.5, 2.5, 2.5, 40, 330)
		self.rect (2.5, 2.7, 5, 3.7)
		self.rect (4, 2.7, 5, 5)

	def W (self):
		self.straight (0, 0, 1, 5)
		self.straight (2, 0, 1, 5)
		self.straight (2, 0, 3, 5)
		self.straight (4, 0, 3, 5)

	def V (self):
		self.straight (0, 0, 2, 5)
		self.straight (4, 0, 2, 5)

	def T (self):
		self.rect (0, 0, 5, 1)
		self.rect (2, 1, 3, 5)

	def I (self):
		self.rect (2, 0, 3, 5)

	def A (self):
		self.straight (2, 0, 0, 5)
		self.straight (2, 0, 4, 5)
		self.rect (1.4, 2.5, 3.6, 3.5)

	def F (self):
		self.rect (0, 0, 1, 5)
		self.rect (1, 0, 5, 1)
		self.rect (1, 2, 5, 3)

	def E (self):
		self.rect (0, 0, 1, 5)
		self.rect (0, 0, 5, 1)
		self.rect (0, 2, 5, 3)
		self.rect (0, 4, 5, 5)

	def BackE (self):
		self.rect (4, 0, 5, 5)
		self.rect (0, 0, 5, 1)
		self.rect (0, 2, 5, 3)
		self.rect (0, 4, 5, 5)

	def UpE (self):
		self.rect (0, 4, 5, 5)
		self.rect (0, 0, 1, 5)
		self.rect (2, 0, 3, 5)
		self.rect (4, 0, 5, 5)

	def DownE (self):
		self.rect (0, 0, 5, 1)
		self.rect (0, 0, 1, 5)
		self.rect (2, 0, 3, 5)
		self.rect (4, 0, 5, 5)

	def H (self):
		self.rect (0, 0, 1, 5)
		self.rect (4, 0, 5, 5)
		self.rect (1, 2, 4, 3)

	def K (self):
		self.rect (0, 0, 1, 5)
		self.straight (3.5, 0, 0.5, 2.5, width = 1.5)
		self.straight (0.5, 2.5, 3.5, 5, width = 1.5)

	def L (self):
		self.rect (0, 0, 1, 5)
		self.rect (1, 4, 5, 5)

	def Z (self):
		self.rect (0, 0, 5, 1)
		self.rect (0, 4, 5, 5)
		self.straight (3.5, 1, 0, 4, width = 1.5)

	def X (self):
		self.straight (4, 0, 0, 5)
		self.straight (0, 0, 4, 5)

	def NM (self):
		"""
		Sidebars common to N and M
		"""
		self.rect (0, 0, 1, 5)
		self.rect (4, 0, 5, 5)

	def N (self):
		self.NM ()
		self.straight (0, 0, 4, 5)

	def BackN (self):
		self.NM ()
		self.straight (4, 0, 0, 5)

	def M (self):
		self.NM ()
		self.straight (0, 0, 2, 5)
		self.straight (4, 0, 2, 5)

	def gamma (self):
		self.rect (0, 0, 5, 1)
		self.rect (0, 0, 1, 5)

	def delta (self):
		self.straight (2, 0, 0, 5)
		self.straight (2, 0, 4, 5)
		self.rect (0.5, 4, 4.5, 5)

	def pi (self):
		self.rect (0, 0, 5, 1)
		self.rect (0, 0, 1, 5)
		self.rect (4, 0, 5, 5)

	def cross (self):
		self.rect (2, 0, 3, 5)
		self.rect (0, 2, 5, 3)

	def box (self):
		self.rect (0, 0, 5, 1)
		self.rect (0, 4, 5, 5)
		self.rect (0, 1, 1, 4)
		self.rect (4, 1, 5, 4)

	def star (self):
		"""
		Star of 5 points
		"""
		n = 5 # can change here
		list = []
		for i in xrange (0, n):
			theta = (i+0.00001)/n*2*math.pi # points on a circle inside the 5x5 grid
			x = 2.5 + 2.5*math.sin (theta)
			y = 2.5 - 2.5*math.cos (theta)
			list.append (self.convert (x, y)) # add point to list
			theta = (i+0.5)/n*2*math.pi
			x = 2.5 + math.sin (theta)
			y = 2.5 - math.cos (theta)
			list.append (self.convert (x, y)) 
		self.dc.DrawPolygon (list, fill_style = wx.wxWINDING_RULE)

	latin = [A, C,
			 C, E, F, G,
			 H, I, K, L, M,
			 N, O, Q, T, V,
			 W, X, Z]

	fourE = [E, UpE, DownE, BackE]

	greek = [A, gamma, delta, E,
			 Z, H, I, K, M,
			 N, O, pi, T, X]

	cyrillic = [A, delta, E, BackN,
			   K, M, H, O, pi,
			   T, C, X]

	symbol = [O, cross, star, box]

	alphabets = {_("Latin"):latin, _("Greek"):greek,
				 _("Cyrillic"):cyrillic, _("Four Es"):fourE,
				 _("Symbol"):symbol}

	def __init__(self, width, height, alpha = symbol, mirr = 0, parent = None):
		"""
		Initialise. width and height define the physical size of the
		CRT in cm.
		"""
		wx.wxFrame.__init__ (self, parent, -1, _("Snellen Chart"))
		wx.EVT_CLOSE (self, self.OnClose)
		# width/Y is screen size (X/Y in cm)
		# distance is distance in metres between CRT and the "average" patient
		self.width = width
		self.height = height
		self.distances = [3, 5, 6, 7.5, 9, 12, 15, 18, 24, 30, 48, 60]
		self.mirror = mirr
		self.alphabet = alpha
		wx.EVT_KEY_DOWN (self, self.OnKeyUp)
		wx.EVT_LEFT_UP (self, self.OnLeftDown)
		wx.EVT_RIGHT_UP (self, self.OnRightDown)
		wx.EVT_LEFT_DCLICK (self, self.OnDClick)
		wx.EVT_PAINT (self, self.OnPaint)
		self.ShowFullScreen (1)
		self.screen_x, self.screen_y = self.GetClientSizeTuple ()
		gmLog.gmDefLog.Log (gmLog.lInfo, 'I think the screen size is %d x %d' % (self.screen_x, self.screen_y))
		self.set_distance (2)
		screensizes = {_("14 inch"):(28, 21), _("16 inch"):(30, 23)}

	def set_distance (self, n):
		"""
		Sets standard viewing distance, against which patient is
		compared. n is an index to the list self.distances
		"""
		self.distance = n
		# Snellen characters are the smallest readable characters by
		# an average person at the stated distance. They are defined
		# exactly as being in a box which subtends 5' of an arc on the
		# patient's eye, each stroke subtending 1' of arc
		one_minute = (math.pi/180)/60
		blocksize = self.distances[n]*100*math.atan(one_minute) # in cm
		# convert to pixels
		self.blockX = int (blocksize/self.width*self.screen_x)
		self.blockY = int (blocksize/self.height*self.screen_y)
		# how many characters can we fit now?
		chars = int (self.screen_x / (self.blockX*5)) - 1
		if chars < 1:
			chars = 1
		if chars > 7:
			chars = 7
		if chars < len (self.alphabet):
			self.choices = []
			while len (self.choices) < chars:
				c = random.choice (self.alphabet)
				if not c in self.choices:
					self.choices.append (c)
		else:
			self.choices = [random.choice (self.alphabet) for i in
							range (1, chars)]
		self.spacing = int ((self.screen_x -
		(chars*self.blockX*5))/(chars+1))
		if self.spacing < 0:
			self.spacing = 0
		self.startY = int ((self.screen_y-(self.blockY*5))/2)

	def draw (self):
		"""
		displays characters in the centre of the screen from the
		selected alphabet
		"""

		# clear the screen
		self.reverse ()
		self.dc.DrawRectangle (0,0, self.screen_x, self.screen_y)
		self.reverse ()
		# draw size
		self.dc.DrawText (str(self.distances[self.distance]), 20, 20)
		self.startX = self.spacing
		for i in self.choices:
			i (self)
			self.startX += self.blockX*5
			self.startX += self.spacing


	def setup_DC (self):
		self.dc.SetFont (wx.wxFont (36, wx.wxROMAN, wx.wxNORMAL, wx.wxNORMAL))
		self.dc.SetBrush (wx.wxBLACK_BRUSH)
		self.dc.SetBackground (wx.wxWHITE_BRUSH)
		self.dc.SetPen (wx.wxTRANSPARENT_PEN)


	def OnPaint (self, event):
		self.dc = wx.wxPaintDC (self)
		self.setup_DC ()
		self.draw ()
		self.dc = None 

	def OnKeyUp (self, key):
		if key.GetKeyCode () == wx.WXK_UP and self.distance < len (self.distances)-1:
			self.set_distance (self.distance+1)
		if key.GetKeyCode () == wx.WXK_DOWN and self.distance > 0:
			self.set_distance (self.distance-1)
		if key.GetKeyCode () == wx.WXK_ESCAPE:
			self.Destroy ()

	def OnLeftDown (self, key):
		if self.distance > 0:
			self.set_distance (self.distance-1)
		self.Refresh ()

	def OnRightDown (self, key):
		if self.distance < len(self.distances)-1:
			self.set_distance (self.distance+1)
		self.Refresh()

	def OnDClick (self, key):
		self.Destroy()
		
	def OnClose (self, event):
		self.Destroy()

#============================================================================
class cSnellenCfgDlg (wx.wxDialog):
	"""
	Dialogue class to get Snellen chart settings.
	"""
	def __init__ (self):
		wx.wxDialog.__init__(
			self,
			None,
			-1,
			_("Snellen Chart Setup"),
			wx.wxDefaultPosition,
			wx.wxSize(350, 200)
		)
		vbox = wx.wxBoxSizer (wx.wxVERTICAL)
		hbox1 = wx.wxBoxSizer (wx.wxHORIZONTAL)
		hbox1.Add (wx.wxStaticText(self, -1, _("Screen Height (cm): ")), 0, wx.wxALL, 15)
		self.height_ctrl = wx.wxSpinCtrl (self, -1, value = "25", min = 10, max = 100)
		hbox1.Add (self.height_ctrl, 1, wx.wxTOP, 15)
		vbox.Add (hbox1, 1, wx.wxEXPAND)
		hbox2 = wx.wxBoxSizer (wx.wxHORIZONTAL)
		hbox2.Add (wx.wxStaticText(self, -1, _("Screen Width (cm): ")), 0, wx.wxALL, 15)
		self.width_ctrl = wx.wxSpinCtrl (self, -1, value = "30", min = 10, max = 100)
		hbox2.Add (self.width_ctrl, 1, wx.wxTOP, 15)
		vbox.Add (hbox2, 1, wx.wxEXPAND)
		hbox3 = wx.wxBoxSizer (wx.wxHORIZONTAL)
		hbox3.Add (wx.wxStaticText(self, -1, _("Alphabet: ")), 0, wx.wxALL, 15)
		self.alpha_ctrl = wx.wxChoice (self, -1, choices=cSnellenChart.alphabets.keys ())
		hbox3.Add (self.alpha_ctrl, 1, wx.wxTOP, 15)
		vbox.Add (hbox3, 1, wx.wxEXPAND)
		self.mirror_ctrl = wx.wxCheckBox (self, -1, label = _("Mirror"))
		vbox.Add (self.mirror_ctrl, 0, wx.wxALL, 15)
		vbox.Add (wx.wxStaticText (self, -1,
_("""Control Snellen chart using mouse:
left-click increases text
right-click decreases text
double-click ends""")), 0, wx.wxALL, 15)
		hbox5 = wx.wxBoxSizer (wx.wxHORIZONTAL)
		ok = wx.wxButton(self, wx.wxID_OK, _(" OK "), size=wx.wxDefaultSize)
		cancel = wx.wxButton (self, wx.wxID_CANCEL, _(" Cancel "),
						   size=wx.wxDefaultSize)
		hbox5.Add (ok, 1, wx.wxTOP, 15)
		hbox5.Add (cancel, 1, wx.wxTOP, 15)
		vbox.Add (hbox5, 1, wx.wxEXPAND)
		self.SetSizer (vbox)
		self.SetAutoLayout (1)
		vbox.Fit (self)

		wx.EVT_BUTTON (ok, wx.wxID_OK, self.OnOK)
		wx.EVT_BUTTON (cancel, wx.wxID_CANCEL, self.OnCancel)
		wx.EVT_CLOSE (self, self.OnClose )
		self.Show(1)
#		self.parent = parent

	def OnClose (self, event):
		self.Destroy ()

	def OnCancel (self, event):
		self.Destroy ()

	def OnOK (self, event):
		if self.Validate() and self.TransferDataFromWindow():
			selected_alpha_string = self.alpha_ctrl.GetStringSelection()
			if selected_alpha_string is None or len (selected_alpha_string) < 2:
				alpha = cSnellenChart.latin
			else:
				alpha = cSnellenChart.alphabets[selected_alpha_string]
			height = self.height_ctrl.GetValue ()
			width = self.width_ctrl.GetValue ()
			mirr = self.mirror_ctrl.GetValue()

#			self.Destroy()
			return (width, height, alpha, mirr)

#============================================================================
# FIXME needn't be a plugin, rewrite to not be one
#class gmSnellen (gmPlugin.wxBasePlugin):
#	tab_name = _('Snellen Chart')

#	def name (self):
#		return gmSnellen.tab_name

#	def register (self):
#		menu = self.gb['main.toolsmenu']
#		menu.Append (ID_SNELLENMENU, "Snellen", "Snellen Chart")
#		wx.EVT_MENU (self.gb['main.frame'], ID_SNELLENMENU, self.OnSnellenTool)

#	def unregister (self):
#		menu = self.gb['main.toolsmenu']
#		menu.Delete (ID_SNELLENMENU)
		
#	def OnSnellenTool (self, event):
#		frame = cSnellenCfgDlg (self.gb['main.frame'])
#		frame.Show (1)
	
#============================================================================
# main
#----------------------------------------------------------------------------
if __name__ == '__main__':
	class TestApp (wx.wxApp):
		def OnInit (self):
			cfg = cSnellenCfgDlg()
			print cfg
			print "now doing frame"
			frame = cSnellenChart (
				width = cfg[0],
				height = cfg[1],
				alpha = cfg[2],
				mirr = cfg[3],
				parent = None
			)
			print "now showing frame"
#			frame.Show (1)

			frame.CentreOnScreen(wx.wxBOTH)
			self.SetTopWindow(frame)
			frame.Show(True)
			return 1

	def main ():
		app = TestApp ()
		app.MainLoop ()

	main()
#============================================================================
# $Log: gmSnellen.py,v $
# Revision 1.14  2005-09-24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.13  2004/07/28 15:43:12  ncq
# - tabify, start rework for permanent (?) inclusion in top panel
#
