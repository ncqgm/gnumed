from wxPython.wx import *
from wxPython.stc import *
import string

STYLE_ERROR=1
STYLE_TEXT=2
STYLE_EMBED=4

class PickList (wxListBox):

    def __init__ (self, parent, pos, size, callback):
        wxListBox.__init__ (self, parent, -1, pos, size, style=wxLB_SINGLE | wxLB_NEEDED_SB)
        self.callback = callback
        self.SetSelection (1)
        EVT_LISTBOX (self, self.GetId (), self.Enter)


    def SetItems (self, items):
        """
        Sets the items, Items is a dict with label, data, weight items
        """
        items.sort (lambda a,b: cmp (b['weight'], a['weight']))
        self.Clear ()
        self.Set ([i['label'] for i in items])
        n= 0
        for i in items:
            self.SetClientData (n, i['data'])
        self.alive = 1

    def Up (self):
        n = self.GetSelection ()
        if n > 0:
            self.SetSelection (n-1)

    def Down (self):
        n = self.GetSelection ()
        if n < self.GetCount ()-1:
            self.SetSelection (n+1)

    def Enter (self, event=None):
        n = self.GetSelection ()
        self.callback (self.GetString (n), self.GetClientData (n))

    def Destroy (self):
        self.alive = 0
        wxListBox.Destroy (self)
        
class ResizingWindow (wxScrolledWindow):
    """
    A vertically-scrolled window which allows subwindows to change their size,
    and adjusts accordingly
    """
    
    def __init__ (self, parent, id, pos = wxDefaultPosition, size = wxDefaultSize):
        wxScrolledWindow.__init__ (self, parent, id, pos = pos, size = size, style =wxVSCROLL)
        self.lines = [[]]
        self.SetScrollRate (0, 20) # suppresses X scrolling by setting X rate to zero
        self.prev = None
        self.next = None
        self.__matcher = None
        self.list = None
        self.popup = None

    def AddWidget (self, widget, label=None):
        """
        Adds a widget, optionally with label
        
        @type label: string
        @param label: text of the label
        @type widgets: wxWindow descendant
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

    def PickList (self, callback, x, y):
        """
        Returns a pick list, destroying a pre-existing pick list for this widget

        the alive member is true until the object is Destroy ()'ed

        @param callback: called when a item is selected,
        @type callback: callable
        @param x: the X-position where the list should appear
        @type x: int
        @param x: the Y-position where the list should appear
        @type y: int

        @return: PickList
        """
        if self.list and self.list.alive:
            self.list.Destroy ()
        w, h = self.GetSizeTuple ()
        ch = self.GetCharHeight ()
        lh = ch*9
        if lh+ch > h:
            lh = h
            y = 0
        elif y+lh+ch > h:
            y = h-lh
        else:
            y += ch
        lw = int (lh / 1.4)
        if lw > w:
            lw = w
            x = 0
        elif x+lw > w:
            x = w-lw
        self.list = PickList (self, wxPoint (x, y), wxSize (lw, lh), callback)
        return self.list


    def DestroyPopup (self):
        if self.popup:
            self.popup.Destroy ()
            self.popup = None

    def PlacePopup (self, window):
        """
        Accepts any window whose parent is this window, and
        sizes and positions at appropriately
        """
        x, y = self.GetSizeTuple ()
        x = x/4
        width = x*3
        y = y/3
        height = y*2
        window.SetDimensions (x, y, width, height)
        self.popup = window

    def PlaceFixedPopup (self, window):
        """
        Places a  popup window, preserves the window's size
        """
        x,y = self.GetSizeTuple ()
        w,h = window.GetSizeTuple ()
        window.MoveXY (x-w, y-h)
        self.popup = None

class ResizingSTC (wxStyledTextCtrl):
    """
    A StyledTextCrl that monitors the size of its internal text and
    resizes the parent accordingly.
    
    MUST ONLY be used inside ResizingWindow!
    """
    
    def __init__ (self, parent, id, pos=wxDefaultPosition, size= wxDefaultSize, style=0, name="StyledTextCtrl"):
        wxStyledTextCtrl.__init__ (self, parent, id, pos, size, style, name)
        self.parent = parent
        self_id = self.GetId ()
        self.SetWrapMode (wxSTC_WRAP_WORD)
        self.StyleSetSpec (STYLE_ERROR, "fore:#7F11010,bold")
        self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
        self.StyleSetChangeable (STYLE_EMBED, 0)
        self.StyleSetHotSpot (STYLE_EMBED, 1)
        self.SetEOLMode (wxSTC_EOL_LF)
        self.SetModEventMask (wxSTC_MOD_INSERTTEXT | wxSTC_MOD_DELETETEXT | wxSTC_PERFORMED_USER)
        EVT_STC_MODIFIED (self, self_id, self.__OnChange)
        EVT_KEY_DOWN (self, self.__OnKeyDown)
        EVT_KEY_UP (self, self.__OnKeyUp)
        self.__no_list = 0
        self.__embed = {}
        self.list = 0
        self.no_list = 0
        self.__matcher = None

    def SetText (self, text):
        self.__no_list = 1
        wxStyledTextCtrl.SetText (self, text)
        self.__no_list = 0
        
    def __OnChange (self, event):
        event.Skip ()
        self.parent.DestroyPopup ()
        length = self.GetLength ()
        height = self.PointFromPosition (length).y - self.PointFromPosition (0).y + self.TextHeight (0)
        x, y = self.GetSizeTuple ()
        if y != height:
            self.SetDimensions (-1, -1, -1, height)
            self.parent.ReSize ()
        if self.__matcher and not self.__no_list and event.GetModificationType () & (wxSTC_MOD_INSERTTEXT | wxSTC_MOD_DELETETEXT):
            pos = self.GetCurrentPos ()
            text = self.GetText ()
            self.end = text.find (';', pos, length) 
            self.start = text.rfind (';', 0, pos)
            if self.start == -1:
                self.start = 0
            else:
                self.start += 1
            if self.end == -1:
                self.end = length
            text = text[self.start:self.end].strip ()
            if text and not self.no_list:
                flag, l = self.__matcher.getMatches (text)
                if flag:
                    if not (self.list and self.list.alive):
                        x, y = self.GetPositionTuple ()
                        p = self.PointFromPosition (pos)
                        self.list = self.parent.PickList (self.__userlist, x+p.x, y+p.y)
                    self.list.SetItems (l)
                elif self.list and self.list.alive:
                        self.list.Destroy ()
            else:
                if self.list and self.list.alive:
                    self.list.Destroy ()


    def __userlist (self, text, data=None):
        self.list.Destroy ()
        if callable (data):
            data (text, self.parent, self)
        else:
            self.Embed (text, data)

    def Embed (self, text, data=None):
        self.no_list = 1
        self.SetTargetEnd (self.end)
        self.SetTargetStart (self.start)
        self.ReplaceTarget (text + ';')
        self.StartStyling (self.start, 0xFF)
        self.SetStyling (len (text)+1, STYLE_EMBED)
        if data:
            self.__embed[text] = data
        self.SetCurrentPos (self.start + len (text) + 1)
        self.SetTargetEnd (0)
        self.SetTargetStart (0)
        self.no_list = 0

    def __OnKeyDown (self, event):
        if self.list and not self.list.alive:
            self.list = None #someone else has destroyed our list!
        pos = self.GetCurrentPos ()
        if event.KeyCode () == WXK_TAB:
            if event.m_shiftDown:
                if self.prev:
                    self.prev.SetFocus ()
            else:
                if self.next:
                    self.next.SetFocus ()
        elif event.KeyCode () == ord (';'):
            if self.GetLength () == 0:
                wxBell ()
            elif self.GetCharAt (pos and pos-1) == ord (';'):
                wxBell ()
            else:
                event.Skip ()
        elif event.KeyCode () == WXK_DELETE:
            if self.GetStyleAt (pos) == STYLE_EMBED:
                self.DelPhrase (pos)
            else:
                event.Skip ()
        elif event.KeyCode () == WXK_BACK:
            if self.GetStyleAt (pos and pos-1) == STYLE_EMBED:
                self.DelPhrase (pos and pos-1)
            else:
                event.Skip ()
        elif event.KeyCode () == WXK_RETURN and not event.m_shiftDown:
            if self.list and self.list.alive:
                self.list.Enter ()
            elif pos == self.GetLength ():
                if self.GetCharAt (pos and pos-1) == ord (';'):
                    if self.next:
                        self.next.SetFocus ()
                else:
                    self.AddText (';')
            elif self.GetLength () == 0 and self.next ():
                self.next.SetFocus ()
            else:
                event.Skip ()
        elif self.list and self.list.alive and event.KeyCode () == WXK_UP:
            self.list.Up ()
        elif self.list and self.list.alive and event.KeyCode () == WXK_DOWN:
            self.list.Down ()
        else:
            event.Skip ()

    def DelPhrase (self, pos):
        end = pos+1
        while end < self.GetLength () and self.GetCharAt (end) != ord(';'):
            end += 1
        start = pos
        while start > 0 and self.GetCharAt (start and start-1) != ord (';'):
            start -= 1
        self.SetTargetStart (start)
        self.SetTargetEnd (end)
        self.ReplaceTarget ('')
        

    def __OnKeyUp (self, event):
        if not self.list:
            cur = self.PointFromPosition (self.GetCurrentPos ())
            self.parent.EnsureVisible (self, cur.x, cur.y)

    def SetFocus (self):
        wxStyledTextCtrl.SetFocus (self)
        cur = self.PointFromPosition (self.GetCurrentPos ())
        self.parent.EnsureVisible (self, cur.x, cur.y)

    def AttachMatcher (self, matcher):
        """
        Attaches a gmMatchProvider to the STC,this will be used to drive auto-completion
        """
        self.__matcher = matcher

if __name__ == '__main__':

    from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

    class RecallWindow (wxWindow):
        def __init__ (self, parent, id):
            wxWindow.__init__ (self, parent, id)
            self.type = wxTextCtrl (self, -1)
            self.date = wxTextCtrl (self, -1)
            self.notes = wxTextCtrl (self, -1)
            szr = wxFlexGridSizer (3, 2)
            szr.Add (wxStaticText (self, -1, 'Type'), 1)
            szr.Add (self.type, 1)
            szr.Add (wxStaticText (self, -1, 'Date'), 1)
            szr.Add (self.date, 1)
            szr.Add (wxStaticText (self, -1, 'Notes'), 1)
            szr.Add (self.notes, 1)
            szr.AddGrowableCol (1)
            #szr.AddGrowableRow (2)
            self.SetSizer (szr)
            szr.Fit (self)

    def Recall (text, parent, caller):
        recall = RecallWindow (parent, -1)
        parent.PlacePopup (recall)
        recall.Layout ()
        recall.Show ()

    AOElist = [{'label':'otitis media', 'data':1, 'weight':1}, {'label':'otitis externa', 'data':2, 'weight':1},
                {'label':'cellulitis', 'data':3, 'weight':1}, {'label':'gingvitis', 'data':4, 'weight':1},
                {'label':'ganglion', 'data':5, 'weight':1}]

    Subjlist = [{'label':'earache', 'data':1, 'weight':1}, {'label':'earache', 'data':1, 'weight':1},
               {'label':'ear discharge', 'data':2, 'weight':1}, {'label':'eardrum bulging', 'data':3, 'weight':1},
               {'label':'sore arm', 'data':4, 'weight':1}, {'label':'sore tooth', 'data':5, 'weight':1}]

    Planlist = [{'label':'pencillin V', 'data':1, 'weight':1}, {'label':'penicillin X', 'data':2, 'weight':1},
                {'label':'penicillinamine', 'data':3, 'weight':1}, {'label':'penthrane', 'data':4, 'weight':1},
                {'label':'penthidine', 'data':5, 'weight':1},
                {'label':'recall', 'data':Recall, 'weight':1}]

    
    class testFrame(wxFrame):
        def __init__(self, title):
            # begin wxGlade: MyFrame.__init__
            wxFrame.__init__(self, None, wxNewId (), title)
            self.text_ctrl_1 = ResizingWindow (self, -1, size = wxSize (300, 150))
            self.S = ResizingSTC (self.text_ctrl_1, -1)
            self.S.AttachMatcher (cMatchProvider_FixedList (Subjlist))
            self.O = ResizingSTC (self.text_ctrl_1, -1)
            self.A = ResizingSTC (self.text_ctrl_1, -1)
            self.A.AttachMatcher (cMatchProvider_FixedList (AOElist))
            self.P = ResizingSTC (self.text_ctrl_1, -1)
            self.P.AttachMatcher (cMatchProvider_FixedList (Planlist))
            self.S.prev = None
            self.S.next = self.O
            self.O.prev = self.S
            self.O.next = self.A
            self.A.prev = self.O
            self.A.next = self.P
            self.P.prev = self.A
            self.P.next = None
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
