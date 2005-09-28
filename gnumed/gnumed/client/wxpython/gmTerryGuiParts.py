"""GnuMed - Richard Terry style GUI elements

TODO:
- implement user defined rgb colours
- implement flashing text on the rest of the panel!
- add font size/style as option

copyright: author
dependencies: wxPython (>= version 2.3.1)
"""
#===========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmTerryGuiParts.py,v $
__version__ = "$Revision: 1.6 $"
__author__  = 'Dr. Richard Terry'
__license__ = 'GPL (details at http://www.gnu.org)'

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

#===========================================================================
class cAlertCaption(wx.Panel):
	"""Bottom left hand pane alert panel.

	This panel consists constructs a simple heading to be used at the bottom
	of the screen, in the form of capitalised word on user defined foreground
	and background colours. The heading is left justified curently. The
	default colours are black text on intermediate grey so as to not make it
	too intrusive. The alert text will appear in flashing red text
	"""
#   def __init__(self, parent, id, title, bg_red, bg_blue, bg_green,fg_red, fg_blue, fg_green):
#   this to be used once the rgb thingy is fixed
	def __init__(self, parent, id, title):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SetBackgroundColour(wx.Colour(222,222,222))                            #set main panel background color
		sizer  = wx.BoxSizer(wx.HORIZONTAL)
		#SetCaptionBackgroundColor()                                               #set background colour with rgb  TODO
		#-----------------------------------------------
		#create a panel which will hold the caption
		#add the title to it, set the colours
		#stick it on a sizer with a cap above and below
		#----------------------------------------------
		captionpanel = wx.Panel(self,-1,size = (400,10))
		captionpanel.SetBackgroundColour(wx.Colour(197,194,197))                    #intermediate gray
		caption = wx.StaticText(captionpanel,-1, title,style = wx.ALIGN_CENTRE_VERTICAL)   # static text for the caption
		caption.SetForegroundColour(wx.Colour(0,0,0))	                           #black as... 
		#SetCaptionForegroundColor()                                               #set caption text colour rgb TODO
		caption.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))
		sizer.Add(captionpanel,1,wx.EXPAND|wx.ALL,2)
                sizer.Add(0,9,6)
		self.SetSizer(sizer)                                               #set the sizer 
		sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
		self.SetAutoLayout(True)                                           #tell frame to use the sizer
		#self.Show(True) #showing done by manager!                                                    #show the panel   
		
	def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
		self.SetBackgroundColour(wx.Colour(bg_red,bg_blue,bg_green))
		return		  
	def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
		self.caption.SetForegroundColour(wx.Colour(fg_red,fg_blue,fg_green))
		return

#===========================================================================
class cDividerCaption(wx.Panel):
	"""This panel consists of one or more headings on a horizontal panel and is

		used to divide/head sections of the screenel There are user defined foreground
		and background colours. The captions are centred in the available space. The
		default colours are purple panel with white bold text
		words (sounds yuk doesn't it - but I like it and it works well!!!!!
	"""
	#   def __init__(self, parent, id, title, bg_red, bg_blue, bg_green,fg_red, fg_blue, fg_green):
	#   this to be used once the rgb thingy is fixed
	def __init__(self, parent, id, title):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, 0)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.SetBackgroundColour(wx.Colour(197,194,255))                            #set panel background to light purple!
		#SetCaptionBackgroundColor()                                               #set panel background colour  rgb
		caption = wx.StaticText(self,-1, title,style = wx.ALIGN_CENTRE)              #static text control for the caption
		caption.SetForegroundColour(wx.WHITE)	                                   #white foreground text colour
		#SetCaptionForegroundColor()                                              #set caption text colour to rgb
		caption.SetFont(wx.Font(13,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))         #TODO implement font size parameter
		sizer.Add(caption,1,wx.EXPAND)                                      #add caption to the sizer
		self.SetSizer(sizer)                                               #set the sizer
		sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
		self.SetAutoLayout(True)                                           #tell frame to use the sizer
		#self.Show(True)                                                    #show the panel

	def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
		self.SetBackgroundColour(wx.Colour(bg_red,bg_blue,bg_green))

	def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
		self.caption.SetForegroundColour(wx.Colour(fg_red,fg_blue,fg_green))
		return

#===========================================================================
class cHeadingCaption(wx.Panel):
    """This panel consists constructs a simple heading to be used at the top

        of a panel, in the form of capitalised word on user defined foreground
        and background colours. The heading is left justified curently. The
        default colours are purple panel, orange label with yellow capitalised
        words (sounds yuk doesn't it - but I like it and it works well!!!!!
    """
    def __init__ (self, parent, id, text, bgC = wx.Colour (197,194,255), hdrC = wx.Colour (255, 129, 131), txtC = wx.Colour (255, 255, 0)):
        self.text = text
        self.bgC = bgC
        self.hdrC = hdrC
        self.txtC = txtC
        wx.Panel.__init__(self, parent, id)
        wx.EVT_PAINT (self, self.OnPaint)
        wx.EVT_SIZE (self, self.OnSize)
        self.w = 0
        self.h = 0

    def OnPaint (self, event):
        self.redraw (wxPaintDC (self))

    def OnSize (self, event):
        self.w, self.h = self.GetClientSizeTuple ()

    def redraw (self, dc):
        dc.SetBrush (wx.Brush (self.bgC, wx.SOLID))
        dc.SetPen (wx.TRANSPARENT_PEN)
        dc.DrawRectangle (0, 0, self.w, self.h)
        dc.SetTextBackground (self.hdrC)
        dc.SetFont (wx.Font (12, wx.SWISS, wx.NORMAL, wx.BOLD))
        dc.SetTextForeground (self.txtC)
        txtw, txth = dc.GetTextExtent (self.text)
        bufx = txtw / 10 # buffer to left of text
        if bufx + txtw > self.w:
            bufx = 0
        bufy = (self.h - txth)/2
        if bufy < 0:
            bufy = 0
        dc.SetBrush (wx.Brush (self.hdrC, wx.SOLID))
        dc.DrawRectangle (bufx, bufy, txtw, txth)
        dc.DrawText (self.text, bufx, bufy) 

	def SetCaptionBackgroundColor(self, bgC):
		self.bgC = bgC
		self.redraw (wx.ClientDC (self))

	def SetCaptionForegroundColor(self, hdrC):
		self.hdrC = hdrC
		self.redraw (wx.ClientDC (self))

#===========================================================================
if __name__ == "__main__":
		app = wxPyWidgetTester(size = (50, 20))
		app.SetWidget(cAlertCaption, -1,"  Alerts  ")
		app.MainLoop()

#===========================================================================
# $Log: gmTerryGuiParts.py,v $
# Revision 1.6  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.5  2005/09/28 19:47:01  ncq
# - runs until login dialog
#
# Revision 1.4  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.3  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.2  2004/07/18 19:55:29  ncq
# - true/false -> True/False
# - indentation fix
#
# Revision 1.1  2004/07/17 20:48:19  ncq
# - aggregate Richard space GUI parts
#
#
#
# old change log:
#	10.06.2002 rterry initial implementation, untested
