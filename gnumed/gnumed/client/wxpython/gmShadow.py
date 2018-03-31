"""GNUmed widget shadowing.

A module to add shadowing to an arbitrary widget.
"""
##############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmShadow.py,v $
__version__ = "$Revision: 1.13 $"
__author__  = "H.Berger <Hilmar.Berger@gmx.de>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, R.Terry <rterry@gnumed.net>"

import wx

from Gnumed.pycommon import gmGuiBroker
#=========================================================
class Shadow (wx.Panel):
	def __init__(self, parent, id):
		"""Create a new shadow.
		"""
		wx.Panel.__init__ (self, parent, id)
		self.sh_width = gmGuiBroker.config['main.shadow.width']
		wx.EVT_SIZE (self, self.OnSize)
		wx.EVT_PAINT (self, self.OnPaint)
	#-----------------------------------------------------
	def SetContents (self, widget):
		"""Marry a widget and a shadow.

		Widget MUST have parent=Shadow widget, and pos=(0,0)
		"""
		self.contents = widget
	#-----------------------------------------------------
	def OnSize (self, event):
		w, h = self.GetClientSize ()
		self.contents.SetClientSizeWH (w-self.sh_width, h-self.sh_width)
	#-----------------------------------------------------
	def OnPaint (self, event):
		dc = wxPaintDC (self)
		w, h = self.GetClientSize ()
		dc.SetPen (wx.TRANSPARENT_PEN)
		#dc.SetBrush (wxWHITE_BRUSH)
		dc.SetBrush (wx.Brush (wx.Colour (240, 240, 240), wx.SOLID))
		# draw white bars
		dc.DrawRectangle (0, h-self.sh_width, w, self.sh_width)
		dc.DrawRectangle (w-self.sh_width, 0, self.sh_width, h)
		r, g, b = gmGuiBroker.config['main.shadow.colour']
		dc.SetBrush (wx.Brush (wx.Colour (r, g, b), wx.SOLID))
		# draw grey bars half as thick
		dc.DrawRectangle (
			self.sh_width/2,
			h-self.sh_width,
			w-self.sh_width,
			self.sh_width/2
		)
		dc.DrawRectangle (
			w-self.sh_width,
			self.sh_width/2,
			self.sh_width/2,
			h-self.sh_width-self.sh_width/2
		)
#=======================================================================
