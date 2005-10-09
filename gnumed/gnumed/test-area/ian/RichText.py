# an experimental simple-HTML rich text widget
# don't try this on wx 2.4


import wx
TEXT=0
COMMAND=1

class RichTextCtrl (wx.TextCtrl):

    def __init__ (self, parent, id, value = '', **kwargs):
        if kwargs.has_key ('style'):
            kwargs['style'] = kwargs['style'] | wx.TE_RICH2
        else:
            kwargs['style'] = wx.TE_RICH2
        if kwargs.has_key ('value'):
            value = kwargs['value']
            del kwargs['value']
        if kwargs.has_key('keywords'):
            self.keywords = kwargs['keywords']
            del kwargs['keywords']
        wx.TextCtrl.__init__ (self, parent, id, **kwargs)
        if value:
            self.SetValue (value)

    def makecolour (self, c):
        if c[0] == '#':
            return wx.Colour (red = int (c[1:3], 16), green = int (c[3:5], 16), blue = int (c[5:7], 16))
        else:
            return wx.NamedColour (c)

    def as_triplet (self, c):
        return (c.Red (), c.Green (), c.Blue ())

    def AppendText (self, value):
        self.func = wx.TextCtrl.AppendText
        self.__add_text (value)
        
    def SetValue (self, value):
        self.func = wx.TextCtrl.AppendText
        self.__add_text (value)

    def Replace (self, from_, to, value):
        self.func = RichTextCtrl._replace
        self.from_ = from_
        self.to = to
        self.__add_text (value)


    def _replace (value):
        wx.TextCtrl.Replace (self.from_, self.to, value)
        self.from_ = self.to
        
    def __add_text (self, value):
        value = unicode (value)
        t = []
        buf = ''
        for i in value:
            if i == '<':
                buf = buf.replace ('&amp;', '&')
                buf = buf.replace ('&lt;','<')
                buf = buf.replace ('&gt;','>')
                buf = buf.replace ('&quot;', "'")
                buf = buf.replace ('&nbsp;',' ')
                t.append ((TEXT, buf))
                buf = ''
            elif i == '>':
                buf = buf.replace ('"', '')
                t.append ((COMMAND, buf.lower ()))
                buf = ''
            else:
                buf += i
        font = self.GetFont ()
        style = self.GetDefaultStyle ()
        fontstack = []
        for mode, content in t:
            if mode == TEXT:
                self.func (self, content)
            else:
                if content == 'b':
                    font.SetWeight (wx.FONTWEIGHT_BOLD)
                    style.SetFont (font)
                    self.SetDefaultStyle (style)
                elif content == '/b':
                    font.SetWeight (wx.FONTWEIGHT_NORMAL)
                    style.SetFont (font)
                    self.SetDefaultStyle (style)
                elif content == 'i':
                    font.SetStyle (wx.FONTSTYLE_ITALIC)
                    style.SetFont (font)
                    self.SetDefaultStyle (style)
                elif content == '/i':
                    font.SetStyle (wx.FONTSTYLE_NORMAL)
                    style.SetFont (font)
                    self.SetDefaultStyle (style)
                elif content == 'p' or content == '/p':
                    self.func (self, '\n')
                elif content == 'center' or content == 'centre':
                    style.SetAlignment (wx.TEXT_ALIGNMENT_CENTER)
                    self.SetDefaultStyle (style)
                elif content == '/center' or content == '/centre':
                    style.SetAlignment (wx.TEXT_ALIGNMENT_DEFAULT)
                    self.SetDefaultStyle (style)
                elif content[:4] == 'font':
                    fontstack.append ((self.GetFont ().GetPointSize (), self.GetFont ().GetFamily (), self.as_triplet (self.GetDefaultStyle ().GetTextColour ()), self.as_triplet (self.GetDefaultStyle ().GetBackgroundColour ())))
                    for i in content[4:].split ():
                        i = i.split ('=')
                        if i[0] == 'size':
                            font.SetPointSize (int(i[1]))
                            style.SetFont (font)
                        elif i[0] == 'color':
                            style.SetTextColour (self.makecolour(i[1]))
                        elif i[0] == 'bgcolor':
                            style.SetBackgroundColour(self.makecolour (i[1]))
                        elif i[0] == 'face':
                            size = font.GetPointSize ()
                            if i[1] == 'sans-serif' or i[1] == 'arial':
                                font = wx.Font (size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                            elif i[1] == 'serif' or i[1] == 'roman':
                                font = wx.Font (size, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                            elif i[1] == 'monospace' or i[1] == 'typewriter' or i[1] == 'courier':
                                font = wx.Font (size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                            elif i[1] == 'cursive':
                                font = wx.Font (size, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                            elif i[1] == 'fantasy':
                                font = wx.Font (size, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                            elif i[1] == 'modern':
                                font = wx.Font (size, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                            style.SetFont (font)
                    self.SetDefaultStyle (style)
                elif content == '/font':
                    size, face, color, bgcolor = fontstack[-1]
                    font = wx.Font (size, face,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                    style.SetFont (font)
                    style.SetTextColour (wx.Colour (*color))
                    style.SetBackgroundColour (wx.Colour (*bgcolor))
                    self.SetDefaultStyle (style)
                    del fontstack[-1]
                 
                          
if __name__ == '__main__':
    	class TestApp (wx.App):
		def OnInit (self):

			frame = wx.Frame (
				None,
				-1,
				"phrase wheel test for GNUmed",
				size=wx.Size(300, 350),
				style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE
			)

                        RichTextCtrl (frame, -1,
"<font size=14><font face=monospace><p>Some text<p><font face=roman>Some text<p><font face=sans-serif>Some text<p><font face=cursive>Some text<p><font face=modern>Some text</font>", size = wx.Size (299, 249), style=wx.TE_MULTILINE) 

			frame.Show (1)
			return 1
	#--------------------------------------------------------
	app = TestApp ()
	app.MainLoop ()

