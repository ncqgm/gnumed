"""GnuMed widget shadowing.

A module to add shadowing to an arbitrary widget.
"""
##############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/handler_devel/client/wxpython/Attic/gmShadow.py,v $
__version__ = "$Revision: 1.1 $"
__author__  = "H.Berger <Hilmar.Berger@gmx.de>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, R.Terry <rterry@gnumed.net>"

from wxPython.wx import *
import gmGuiBroker
#=========================================================
class Shadow (wxPanel):
	def __init__(self, parent, id):
		"""Create a new shadow.
		"""
		wxPanel.__init__ (self, parent, id)
		self.sh_width = gmGuiBroker.config['main.shadow.width']
		EVT_SIZE (self, self.OnSize)
		EVT_PAINT (self, self.OnPaint)
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
		dc.SetPen (wxTRANSPARENT_PEN)
		#dc.SetBrush (wxWHITE_BRUSH)
		dc.SetBrush (wxBrush (wxColour (240, 240, 240), wxSOLID))
		# draw white bars
		dc.DrawRectangle (0, h-self.sh_width, w, self.sh_width)
		dc.DrawRectangle (w-self.sh_width, 0, self.sh_width, h)
		r, g, b = gmGuiBroker.config['main.shadow.colour']
		dc.SetBrush (wxBrush (wxColour (r, g, b), wxSOLID))
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
# Revision 1.1  2003-02-23 04:08:03  sjtan
#
#
#
# first implementation of past history scripts allergies use case, partial patient details.
#
# Revision 1.8  2003/01/12 11:42:23  ncq
# - nasty "invisible" whitespace bug
#
# Revision 1.7  2003/01/12 01:06:22  ncq
# - CVS keywords
# - code cleanup
#
