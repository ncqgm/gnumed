"""GnuMed widget shadowing.

A module to add shadowing to an arbitrary widget.
"""
##############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmShadow.py,v $
__version__ = "$Revision: 1.13 $"
__author__  = "H.Berger <Hilmar.Berger@gmx.de>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, R.Terry <rterry@gnumed.net>"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

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
		w, h = self.GetClientSizeTuple ()
		self.contents.SetClientSizeWH (w-self.sh_width, h-self.sh_width)
	#-----------------------------------------------------
	def OnPaint (self, event):
		dc = wxPaintDC (self)
		w, h = self.GetClientSizeTuple ()
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
# $Log: gmShadow.py,v $
# Revision 1.13  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.12  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.11  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.10  2004/03/04 19:47:07  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.9  2003/11/17 10:56:39  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.8  2003/01/12 11:42:23  ncq
# - nasty "invisible" whitespace bug
#
# Revision 1.7  2003/01/12 01:06:22  ncq
# - CVS keywords
# - code cleanup
#
