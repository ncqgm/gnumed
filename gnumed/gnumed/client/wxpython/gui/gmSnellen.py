#!/usr/bin/env python

"""GnuMed onscreen Snellen Chart emulator.

FIXME: store screen size
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmSnellen.py,v $
# $Id: gmSnellen.py,v 1.21 2007-10-18 18:05:01 ncq Exp $
__version__ = "$Revision: 1.21 $"
__author__ = "Ian Haywood, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import math, random, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../../')
	_ = lambda x:x
from Gnumed.pycommon import gmLog, gmI18N
#from Gnumed.wxpython import gmPlugin

ID_SNELLENMENU = wx.NewId()
ID_SNELLENBUTTON = wx.NewId()

#============================================================================
class cSnellenChart(wx.Frame):

	def convert (self, X,Y):
		"""Converts a pair of co-ordinates from block co-ords to real.

		X, Y	-- define top-left corner of current character
		"""
		if self.mirror:
			X = 5-X
		return wx.Point(
			int ((X * self.blockX) + self.startX),
			int ((Y * self.blockY) + self.startY)
		)

	def O (self):
		"""
		Draws the letter O
		"""
		self._draw_arc (2.5, 2.5, 2.5, 0, 360)

	def Q (self):
		self.O()
		self._draw_line (2.6, 3, 4, 5)

	def C (self):
		if self.mirror:
			self._draw_arc (2.5, 2.5, 2.5, 140, -140)
		else:
			self._draw_arc (2.5, 2.5, 2.5, 40, 320)

	def G (self):
		if self.mirror:
			self._draw_arc (2.5, 2.5, 2.5, 140, -150)
		else:
			self._draw_arc (2.5, 2.5, 2.5, 40, 330)
		self._draw_rect (2.5, 2.7, 5, 3.7)
		self._draw_rect (4, 2.7, 5, 5)

	def W (self):
		self._draw_line (0, 0, 1, 5)
		self._draw_line (2, 0, 1, 5)
		self._draw_line (2, 0, 3, 5)
		self._draw_line (4, 0, 3, 5)

	def V (self):
		self._draw_line (0, 0, 2, 5)
		self._draw_line (4, 0, 2, 5)

	def T (self):
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (2, 1, 3, 5)

	def I (self):
		self._draw_rect (2, 0, 3, 5)

	def A (self):
		self._draw_line (2, 0, 0, 5)
		self._draw_line (2, 0, 4, 5)
		self._draw_rect (1.4, 2.5, 3.6, 3.5)

	def F (self):
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (1, 0, 5, 1)
		self._draw_rect (1, 2, 5, 3)

	def E (self):
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 2, 5, 3)
		self._draw_rect (0, 4, 5, 5)

	def BackE (self):
		self._draw_rect (4, 0, 5, 5)
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 2, 5, 3)
		self._draw_rect (0, 4, 5, 5)

	def UpE (self):
		self._draw_rect (0, 4, 5, 5)
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (2, 0, 3, 5)
		self._draw_rect (4, 0, 5, 5)

	def DownE (self):
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (2, 0, 3, 5)
		self._draw_rect (4, 0, 5, 5)

	def H (self):
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (4, 0, 5, 5)
		self._draw_rect (1, 2, 4, 3)

	def K (self):
		self._draw_rect (0, 0, 1, 5)
		self._draw_line (3.5, 0, 0.5, 2.5, width = 1.5)
		self._draw_line (0.5, 2.5, 3.5, 5, width = 1.5)

	def L (self):
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (1, 4, 5, 5)

	def Z (self):
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 4, 5, 5)
		self._draw_line (3.5, 1, 0, 4, width = 1.5)

	def X (self):
		self._draw_line (4, 0, 0, 5)
		self._draw_line (0, 0, 4, 5)

	def NM (self):
		"""Sidebars common to N and M
		"""
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (4, 0, 5, 5)

	def N (self):
		self.NM ()
		self._draw_line (0, 0, 4, 5)

	def BackN (self):
		self.NM ()
		self._draw_line (4, 0, 0, 5)

	def M (self):
		self.NM ()
		self._draw_line (0, 0, 2, 5)
		self._draw_line (4, 0, 2, 5)

	def gamma (self):
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 0, 1, 5)

	def delta (self):
		self._draw_line (2, 0, 0, 5)
		self._draw_line (2, 0, 4, 5)
		self._draw_rect (0.5, 4, 4.5, 5)

	def pi (self):
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 0, 1, 5)
		self._draw_rect (4, 0, 5, 5)

	def cross (self):
		self._draw_rect (2, 0, 3, 5)
		self._draw_rect (0, 2, 5, 3)

	def box (self):
		self._draw_rect (0, 0, 5, 1)
		self._draw_rect (0, 4, 5, 5)
		self._draw_rect (0, 1, 1, 4)
		self._draw_rect (4, 1, 5, 4)

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
		self.dc.DrawPolygon (list, fill_style = wx.WINDING_RULE)

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

	alphabets = {
		_("Latin"): latin,
		_("Greek"): greek,
		_("Cyrillic"): cyrillic,
		_("Four Es"): fourE,
		_("Symbol"): symbol
	}

	def __init__(self, width, height, alpha = symbol, mirr = 0, parent = None):
		"""
		Initialise. width and height define the physical size of the
		CRT in cm.
		"""
		wx.Frame.__init__ (self, parent, -1, _("Snellen Chart"))

		# width/Y is screen size (X/Y in cm)
		#wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
#		screensizes = {_("14 inch"):(28, 21), _("16 inch"):(30, 23)}
		self.screen_width_cm = width
		self.screen_height_cm = height

		self.screen_width_pixel = 0
		self.screen_height_pixel = 0

		self.standard_patient_chart_distances = [3, 5, 6, 7.5, 9, 12, 15, 18, 24, 30, 48, 60] # in metres
		self.mirror = mirr
		self.alphabet = alpha

		wx.EVT_CLOSE (self, self.OnClose)
		wx.EVT_KEY_DOWN (self, self.OnKeyUp)
		wx.EVT_LEFT_UP (self, self.OnLeftDown)
		wx.EVT_RIGHT_UP (self, self.OnRightDown)
		wx.EVT_LEFT_DCLICK (self, self.OnDClick)
		wx.EVT_PAINT (self, self.OnPaint)
#		wx.EVT_WINDOW_CREATE (self, self.OnCreate)

		self.ShowFullScreen(1)
	#---------------------------------
	# event handlers
	#---------------------------------
#	def OnCreate(self, event):
#		self.ShowFullScreen(1)
	#---------------------------------
	def OnPaint (self, event):
		self.dc = wx.PaintDC(self)
		if self.screen_width_pixel == 0:
			self.screen_width_pixel, self.screen_height_pixel = self.GetClientSizeTuple()
			self.set_distance(2)
#			gmLog.gmDefLog.Log (gmLog.lInfo, 'I think the screen size is %d x %d' % (self.screen_width_pixel, self.screen_height_pixel))

#		self.setup_DC()
		self.dc.SetFont(wx.Font (36, wx.ROMAN, wx.NORMAL, wx.NORMAL))
		self.dc.SetBrush(wx.BLACK_BRUSH)
		self.dc.SetBackground(wx.WHITE_BRUSH)
		self.dc.SetPen(wx.TRANSPARENT_PEN)

#		self.draw ()
		# clear the screen
		self._swap_fg_bg_col()
		self.dc.DrawRectangle(0, 0, self.screen_width_pixel, self.screen_height_pixel)
		self._swap_fg_bg_col ()
		# draw size
		self.dc.DrawText (str(self.standard_patient_chart_distances[self.distance]), 20, 20)
		self.startX = self.spacing
		for i in self.choices:
			i (self)
			self.startX += self.blockX*5
			self.startX += self.spacing

		self.dc = None

	def OnKeyUp (self, key):
		if key.GetKeyCode() == wx.K_UP and self.distance < len (self.standard_patient_chart_distances)-1:
			self.set_distance (self.distance+1)
		if key.GetKeyCode() == wx.K_DOWN and self.distance > 0:
			self.set_distance (self.distance-1)
		if key.GetKeyCode() == wx.K_ESCAPE:
			self.Destroy ()

	def OnLeftDown (self, key):
		if self.distance > 0:
			self.set_distance (self.distance-1)
		self.Refresh ()

	def OnRightDown (self, key):
		if self.distance < len(self.standard_patient_chart_distances)-1:
			self.set_distance (self.distance+1)
		self.Refresh()

	def OnDClick (self, key):
		self.Destroy()
		
	def OnClose (self, event):
		self.Destroy()

	def DestroyWhenApp (self):
		import sys
		sys.exit (0)

	#---------------------------------
	# internal API
	#---------------------------------
	def _swap_fg_bg_col(self):
		"""Swap fore- and background pens."""
		background = self.dc.GetBackground()
		foreground = self.dc.GetBrush()
		self.dc.SetBrush(background)
		self.dc.SetBackground(foreground)
	#---------------------------------
	def _draw_rect(self, x1, y1, x2, y2):
		"""Draw a rectangle."""
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

		self.dc.DrawRectangle(x, y, width, height)
	#---------------------------------
	def _draw_arc (self, x, y, arm, start, end):
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
		self._swap_fg_bg_col()
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
		self._swap_fg_bg_col()
	#---------------------------------
	def _draw_line(self, x1, y1, x2, y2, width = 1):
		"""Draws straight descending letter-stroke.

		(x1, y1) is top-left,
		(x2, y2) is bottom left point
		"""
		coords = [
			self.convert (x1, y1),
			self.convert (x1+width, y1),
			self.convert (x2+width, y2),
			self.convert (x2, y2)
		]
		self.dc.DrawPolygon(coords)
	#---------------------------------
	#---------------------------------
	def set_distance (self, n):
		"""
		Sets standard viewing distance, against which patient is
		compared. n is an index to the list self.standard_patient_chart_distances
		"""
		self.distance = n
		# Snellen characters are the smallest readable characters by
		# an average person at the stated distance. They are defined
		# exactly as being in a box which subtends 5' of an arc on the
		# patient's eye, each stroke subtending 1' of arc
		one_minute = (math.pi / 180) / 60
		blocksize = (self.standard_patient_chart_distances[n] * 100) * math.atan(one_minute) # in cm
		# convert to pixels
		self.blockX = int (blocksize / self.screen_width_cm * self.screen_width_pixel)
		self.blockY = int (blocksize / self.screen_height_cm * self.screen_height_pixel)
		# how many characters can we fit now?
		chars = int (self.screen_width_pixel / (self.blockX*5)) - 1
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
			self.choices = [ random.choice(self.alphabet) for i in range(1, chars) ]
		self.spacing = int ((self.screen_width_pixel -
		(chars*self.blockX*5))/(chars+1))
		if self.spacing < 0:
			self.spacing = 0
		self.startY = int ((self.screen_height_pixel-(self.blockY*5))/2)

#	def draw (self):
#		"""
#		displays characters in the centre of the screen from the
#		selected alphabet
#		"""
#		# clear the screen
#		self._swap_fg_bg_col()
#		self.dc.DrawRectangle (0,0, self.screen_width_pixel, self.screen_height_pixel)
#		self._swap_fg_bg_col ()
#		# draw size
#		self.dc.DrawText (str(self.standard_patient_chart_distances[self.distance]), 20, 20)
#		self.startX = self.spacing
#		for i in self.choices:
#			i (self)
#			self.startX += self.blockX*5
#			self.startX += self.spacing

#	def setup_DC (self):
#		self.dc.SetFont (wx.Font (36, wx.ROMAN, wx.NORMAL, wx.NORMAL))
#		self.dc.SetBrush (wx.BLACK_BRUSH)
#		self.dc.SetBackground (wx.WHITE_BRUSH)
#		self.dc.SetPen (wx.TRANSPARENT_PEN)

#============================================================================
class cSnellenCfgDlg (wx.Dialog):
	"""
	Dialogue class to get Snellen chart settings.
	"""
	def __init__ (self):
		wx.Dialog.__init__(
			self,
			None,
			-1,
			_("Snellen Chart Setup"),
			wx.DefaultPosition,
			wx.Size(350, 200)
		)

#		print wx.DisplaySize()
#		print wx.DisplaySizeMM()

		vbox = wx.BoxSizer (wx.VERTICAL)
		hbox1 = wx.BoxSizer (wx.HORIZONTAL)
		hbox1.Add (wx.StaticText(self, -1, _("Screen Height (cm): ")), 0, wx.ALL, 15)
		self.height_ctrl = wx.SpinCtrl (self, -1, value = "25", min = 10, max = 100)
		hbox1.Add (self.height_ctrl, 1, wx.TOP, 15)
		vbox.Add (hbox1, 1, wx.EXPAND)
		hbox2 = wx.BoxSizer (wx.HORIZONTAL)
		hbox2.Add (wx.StaticText(self, -1, _("Screen Width (cm): ")), 0, wx.ALL, 15)
		self.width_ctrl = wx.SpinCtrl (self, -1, value = "30", min = 10, max = 100)
		hbox2.Add (self.width_ctrl, 1, wx.TOP, 15)
		vbox.Add (hbox2, 1, wx.EXPAND)
		hbox3 = wx.BoxSizer (wx.HORIZONTAL)
		hbox3.Add (wx.StaticText(self, -1, _("Alphabet: ")), 0, wx.ALL, 15)
		self.alpha_ctrl = wx.Choice (self, -1, choices = cSnellenChart.alphabets.keys ())
		hbox3.Add (self.alpha_ctrl, 1, wx.TOP, 15)
		vbox.Add (hbox3, 1, wx.EXPAND)
		self.mirror_ctrl = wx.CheckBox (self, -1, label = _("Mirror"))
		vbox.Add (self.mirror_ctrl, 0, wx.ALL, 15)
		vbox.Add (wx.StaticText (self, -1,
_("""Control Snellen chart using mouse:
left-click increases text
right-click decreases text
double-click ends""")), 0, wx.ALL, 15)
		hbox5 = wx.BoxSizer (wx.HORIZONTAL)
		ok = wx.Button(self, wx.ID_OK, _(" OK "), size=wx.DefaultSize)
		cancel = wx.Button (self, wx.ID_CANCEL, _(" Cancel "),
						   size=wx.DefaultSize)
		hbox5.Add (ok, 1, wx.TOP, 15)
		hbox5.Add (cancel, 1, wx.TOP, 15)
		vbox.Add (hbox5, 1, wx.EXPAND)
		self.SetSizer (vbox)
		self.SetAutoLayout (1)
		vbox.Fit (self)

		wx.EVT_BUTTON (ok, wx.ID_OK, self.OnOK)
		wx.EVT_BUTTON (cancel, wx.ID_CANCEL, self.OnCancel)
		wx.EVT_CLOSE (self, self.OnClose )
		self.Show(1)
#		self.parent = parent

	def OnClose (self, event):
		self.EndModal (1)

	def OnCancel (self, event):
		self.EndModal (1)

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
			self.vals = (width, height, alpha, mirr)
			self.EndModal(0)
			

#============================================================================
# FIXME needn't be a plugin, rewrite to not be one
#class gmSnellen (gmPlugin.wx.BasePlugin):
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

	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	class TestApp (wx.App):
		def OnInit (self):
			cfg = cSnellenCfgDlg()
			if cfg.ShowModal () == 0:
				frame = cSnellenChart (
					width = cfg.vals[0],
					height = cfg.vals[1],
					alpha = cfg.vals[2],
					mirr = cfg.vals[3],
					parent = None
					)
				frame.CentreOnScreen(wx.BOTH)
				self.SetTopWindow(frame)
				frame.Destroy = frame.DestroyWhenApp
				frame.Show(True)
			return 1

	def main ():
		app = TestApp ()
		app.MainLoop ()

	main()
#============================================================================
# $Log: gmSnellen.py,v $
# Revision 1.21  2007-10-18 18:05:01  ncq
# - rearrange, clean up and make runnable
#
# Revision 1.20  2007/10/12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.19  2007/01/20 22:53:32  ncq
# - .KeyCode -> .GetKeyCode()
#
# Revision 1.18  2007/01/18 22:09:18  ncq
# - wx2.8ification
#
# Revision 1.17  2005/10/23 11:31:45  ihaywood
# Snellen now works again (with Andreas' packages, on wx2.4)
#
# Revision 1.16  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.15  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.14  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.13  2004/07/28 15:43:12  ncq
# - tabify, start rework for permanent (?) inclusion in top panel
#
