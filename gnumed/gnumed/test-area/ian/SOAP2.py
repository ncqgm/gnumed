from wxPython.wx import *
from wxPython.stc import *

STYLE_HEADER=1
STYLE_TEXT=2
STYLE_EMBED=4
STYLE_KEYWORD=3

class ResizingWindow (wxScrolledWindow):
    """
    A vertically-scrolled window which allows subwindows to change their size,
    and adjusts accordingly
    """
    
    def __init__ (self, parent, id, size = wxDefaultSize):
        wxScrolledWindow.__init__ (self, parent, id, size = size, style =wxVSCROLL)
        self.lines = [[]]
        self.SetScrollRate (0, 20) # suppresses X scrolling by setting X rate to zero
        self.prev = None
        self.next = None

    def AddWidget (self, widget, label=None):
        """
        Adds a widget, optionally with label
        
        @type label: string
        @param label: text of the label
        @type widgets: wxWindow descendent
        """
        if label:
            textbox = wxStaticText (self, -1, label, style=wxALIGN_RIGHT)
        else:
            textbox = None
        self.lines[-1].append ((label, textbox, widget))

    def Newline (self):
        """
        Starts a newline on the widget
        """
        self.lines.append ([])

    def ReSize (self):
        """
        Resizes the window, called by a subwindow when it changes size
        """
        szr = wxFlexGridSizer (len (self.lines), 2)
        for line in self.lines:
            if line:
                if line[0][1]:
                    szr.Add (line[0][1], 1) # first label goes in column 1
                else:
                    szr.Add (20, 20)
                h_szr = wxBoxSizer (wxHORIZONTAL)
                h_szr.Add (line[0][2], 1, wxGROW) # the rest gets packed into column 2
                for w in line[1:]:
                    if w[1]:
                        h_szr.Add (w[1], 0)
                    h_szr.Add (w[2], 1, wxGROW)
            szr.Add (h_szr, 1, wxGROW)
        szr.AddGrowableCol (1)
        szr.Add (10, 10)
        self.SetSizer (szr)
        self.FitInside ()

    def EnsureVisible (self, widget, cur_x = 0, cur_y = 0):
        """
        Ensures widget is visible
        
        @param widget: a child widget
        @type cur_x: integer
        @param cur_x: the X co-ordinate of the cursor inside widget, if applicable
        @type cur_y: integer
        @param cur_y: the Y co-ordinate of the cursor inside widget
        """
        x, y = widget.GetPositionTuple ()
        x += cur_x
        y += cur_y
        x, y = self.CalcUnscrolledPosition (x, y) # converts real to virtual co-ordinates
        xUnit, yUnit = self.GetScrollPixelsPerUnit ()
        y = y / yUnit
        self.Scroll (-1, y) # currently, don't bother with X

    def SetValues (self, values):
        """
        Runs SetValue () on all the fields

        @type values: dictionary
        @param values: keys are the labels, values are passed to SetValue ()
        """
        for line in self.lines:
            for w in line:
                if values.has_key (w[0]):
                    if isinstance (w[2], wxStyledTextCtrl):
                        w[2].SetText (values[w[0]])
                    elif isinstance (w[2], (wxChoice, wxRadioBox)):
                        w[2].SetSelection (values[w[0]])
                    else:
                        w[2].SetValue (values[w[0]])

    def GetValues (self):
        """
        Returns a dictionary of the results of GetValue ()
        called on all widgets, keyed by label
        Unlabelled widgets don't get called
        """
        ret = {}
        for line in self.lines:
            for w in line:
                if w[0]:
                    if isinstance (w[2], wxStyledTextCtrl):
                        ret[w[0]] = w[2].GetText ()
                    elif isinstance (w[2], (wxChoice, wxRadioBox)):
                        ret[w[0]] = w[2].GetSelection ()
                    else:
                        ret[w[0]] = w[2].GetValue ()
        return ret

    def Clear (self):
        """
        Clears all widgets where this makes sense
        """
        for line in self.lines:
            for w in line:
                if isinstance (w[2], wxStyledTextCtrl):
                    w[2].ClearAll ()
                elif isinstance (w[2], wxTextCtrl):
                    w[2].Clear ()
                elif isinstance (w[2], (wxToggleButton, wxCheckBox, wxRadioButton, wxGauge)):
                    w[2].SetValue (0)
                elif isinstance (w[2], (wxChoice, wxComboBox, wxRadioBox)):
                    w[2].SetSelection (0)
                elif isinstance (w[2], wxSpinCtrl):
                    w[2].SetValue (w[2].GetMin ())
                
                    

class ResizingSTC (wxStyledTextCtrl):
    """
    A StyledTextCrl that monitors the size of its internal text and
    resizes the parent accordingly
    Public API is identical to parent
    MUST ONLY be used inside ResizingWindow!
    """
    
    def __init__ (self, parent, id, pos=wxDefaultPosition, size= wxDefaultSize, style=0, name="StyledTextCtrl"):
        wxStyledTextCtrl.__init__ (self, parent, id, pos, size, style, name)
        self.parent = parent
        self_id = self.GetId ()
        self.SetWrapMode (wxSTC_WRAP_WORD)
        self.StyleSetSpec (STYLE_HEADER, "fore:#7F11010,bold,face:Times,size:12")
        self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
        self.StyleSetSpec (STYLE_KEYWORD, "fore:#3030A0")
        self.SetEOLMode (wxSTC_EOL_LF)
        self.SetModEventMask (wxSTC_MOD_INSERTTEXT | wxSTC_MOD_DELETETEXT | wxSTC_PERFORMED_USER | wxSTC_PERFORMED_UNDO | wxSTC_PERFORMED_REDO)
        EVT_STC_CHANGE (self, self_id, self.OnChange)
        EVT_KEY_DOWN (self, self.OnKeyDown)
        EVT_KEY_UP (self, self.OnKeyUp)

    def OnChange (self, event):
        event.Skip ()
        height = self.PointFromPosition (self.GetLength ()).y - self.PointFromPosition (0).y + self.TextHeight (0)
        x, y = self.GetSizeTuple ()
        if y != height:
            self.SetDimensions (-1, -1, -1, height)
            self.parent.ReSize ()

    def OnKeyDown (self, event):
        if event.KeyCode () == WXK_TAB:
            if event.m_shiftDown:
                if self.prev:
                    self.prev.SetFocus ()
            else:
                if self.next:
                    self.next.SetFocus ()
        else:
            event.Skip ()

    def OnKeyUp (self, event):
        cur = self.PointFromPosition (self.GetCurrentPos ())
        self.parent.EnsureVisible (self, cur.x, cur.y)

    def SetFocus (self):
        wxStyledTextCtrl.SetFocus (self)
        cur = self.PointFromPosition (self.GetCurrentPos ())
        self.parent.EnsureVisible (self, cur.x, cur.y)

if __name__ == '__main__':
    
    class testFrame(wxFrame):
        def __init__(self, title):
            # begin wxGlade: MyFrame.__init__
            wxFrame.__init__(self, None, wxNewId (), title)
            self.text_ctrl_1 = ResizingWindow (self, -1, size = wxSize (300, 120))
            self.S = ResizingSTC (self.text_ctrl_1, -1)
            self.O = ResizingSTC (self.text_ctrl_1, -1)
            self.A = ResizingSTC (self.text_ctrl_1, -1)
            self.P = ResizingSTC (self.text_ctrl_1, -1)
            self.S.next = self.O
            self.O.prev = self.S
            self.O.next = self.A
            self.A.prev = self.O
            self.A.next = self.P
            self.P.prev = self.A
            self.text_ctrl_1.AddWidget (self.S, "Subjective")
            self.text_ctrl_1.Newline ()
            self.text_ctrl_1.AddWidget (self.O, "Objective")
            self.text_ctrl_1.Newline ()
            self.text_ctrl_1.AddWidget (self.A, "Assessment")
            self.text_ctrl_1.Newline ()
            self.text_ctrl_1.AddWidget (self.P, "Plan")
            self.text_ctrl_1.SetValues ({"Subjective":"sore ear", "Plan":"Amoxycillin"})
            self.text_ctrl_1.ReSize ()
            EVT_CLOSE (self, self.OnClose)
            self.__do_layout()
            # end wxGlade

        def __do_layout(self):
            # begin wxGlade: MyFrame.__do_layout
            sizer_1 = wxBoxSizer(wxVERTICAL)
            sizer_1.Add(self.text_ctrl_1, 1, wxEXPAND, 0)
            self.SetAutoLayout(1)
            self.SetSizer(sizer_1)
            sizer_1.Fit(self)
            sizer_1.SetSizeHints(self)
            self.Layout()
            # end wxGlade

        def OnClose (self, event):
            print self.text_ctrl_1.GetValues ()
            self.Destroy ()

    # end of class MyFrame


    class testApp (wxApp):
        def OnInit (self):
            self.frame = testFrame ("Test SOAP")
            self.frame.Show ()
            return 1

    app = testApp (0)
    app.MainLoop ()
