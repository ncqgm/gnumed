#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/ian/SOAP2.py,v $
# $Id: SOAP2.py,v 1.8 2004-11-09 13:13:18 ihaywood Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "Ian Haywood"
__license__ = 'GPL'

from wxPython.wx import *
from wxPython.stc import *
import string, types

STYLE_ERROR=1
STYLE_TEXT=2
STYLE_EMBED=4

class PickList (wxListBox):

    def __init__ (self, parent, pos, size, callback):
        wxListBox.__init__ (self, parent, -1, pos, size, style=wxLB_SINGLE | wxLB_NEEDED_SB)
        self.callback = callback
        EVT_LISTBOX (self, self.GetId (), self.OnList)
        self.alive = 1 # 0=dead, 1=alive, 2=must die


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
        self.SetSelection (0)

    def Up (self):
        n = self.GetSelection ()
        if n > 0:
            self.SetSelection (n-1)

    def Down (self):
        n = self.GetSelection ()
        if n < self.GetCount ()-1:
            self.SetSelection (n+1)

    def Enter (self):
        n = self.GetSelection ()
        if n >= 0:
            text = self.GetString (n)
            data = self.GetClientData (n)
            self.callback (text, data)
        self.alive = 2
        self.Destroy () # this is only safe when in the event handler of another widget

    def OnList (self, event):
        event.Skip ()
        if self.alive != 2:
            n = self.GetSelection ()
            if n >= 0:
                text = self.GetString (n)
                data = self.GetClientData (n)
                self.callback (text, data)
            self.alive = 2
        else:
            wxCallAfter (self.Destroy) # in theory we shouldn't have to do this,
                                       # but when we don't, wx segfaults.
        
    def Destroy (self):
        self.alive = 0
        wxListBox.Destroy (self)
        
class ResizingWindow (wxScrolledWindow):
    """
    A vertically-scrolled window which allows subwindows to change their size,
    and adjusts accordingly
    """
    
    def __init__ (self, parent, id, pos = wxDefaultPosition, size = wxDefaultSize, complete = None):
        wxScrolledWindow.__init__ (self, parent, id, pos = pos, size = size, style =wxVSCROLL)
        self.lines = [[]]
        self.SetScrollRate (0, 20) # suppresses X scrolling by setting X rate to zero
        self.prev = None
        self.next = None
        self.__matcher = None
        self.list = None
        self.popup = None
        self.complete = complete
        self.szr = None
        self.DoLayout ()
        self.szr = wxFlexGridSizer (len (self.lines), 2)
        self.SetSizer (self.szr)
        for line in self.lines:
            if line:
                if line[0][1]:
                    self.szr.Add (line[0][1], 1) # first label goes in column 1
                else:
                    self.szr.Add (20, 20)
                h_szr = wxBoxSizer (wxHORIZONTAL)
                h_szr.Add (line[0][2], 1, wxGROW) # the rest gets packed into column 2
                for w in line[1:]:
                    if w[1]:
                        h_szr.Add (w[1], 0)
                    h_szr.Add (w[2], 1, wxGROW)
                self.szr.Add (h_szr, 1, wxGROW)
        self.szr.AddGrowableCol (1)
        self.szr.Add (10, 10)
        self.FitInside ()

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

    def DoLayout (self):
        """
        Overridden by descendants, this function uses AddWidget and Newline to form
        the outline of the widget
        """
        pass

    def ReSize (self, widget, new_height):
        """
        Called when a child widget has a new height, redoes the layout
        """
        if self.szr:
            self.szr.SetItemMinSize (widget, -1, new_height)
            self.szr.FitInside (self)

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

    def GetSummary (self):
        """
        Gets a terse summary string for the data in the widget
        """
        return ""


    def Set (self, item):
        """
        Accepts a cClinItem, sets the widget to reflect its contents
        """
        pass

    def Save (self, item):
        """
        Accepts a cClinItem, sets *it* to reflect the widget's contents
        """
        pass

class ResizingSTC (wxStyledTextCtrl):
    """
    A StyledTextCrl that monitors the size of its internal text and
    resizes the parent accordingly.
    
    MUST ONLY be used inside ResizingWindow!
    """


    def ReplaceText (self, start, end, text, style=-1, space=0):
        """
        Oddly, the otherwise very rich wxSTC API does not provide an
        easy way to replace text, so we provide it here.

        @param start: the position in the text to start from
        @param length: the length of the string to replace
        @param text: the new string
        @param style: the style for the replaced string
        """
        self.SetTargetStart (start)
        self.SetTargetEnd (end)
        self.ReplaceTarget (text)
        if style > -1:
            self.StartStyling (start, 0xFF)
            self.SetStyling (len (text), style)
    
    def __init__ (self, parent, id, pos=wxDefaultPosition, size= wxDefaultSize, style=0):
        if not isinstance(parent, ResizingWindow):
             raise ValueError, 'parent of %s MUST be a ResizingWindow' % self.__class__.__name__
        wxStyledTextCtrl.__init__ (self, parent, id, pos, size, style)
        self.parent = parent
        self_id = self.GetId ()
        self.SetWrapMode (wxSTC_WRAP_WORD)
        self.StyleSetSpec (STYLE_ERROR, "fore:#7F11010,bold")
        self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
        self.StyleSetChangeable (STYLE_EMBED, 0)
#        self.StyleSetHotSpot (STYLE_EMBED, 1)
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
        if self.no_list:
            return
        length = self.GetLength ()
        height = self.PointFromPosition (length).y - self.PointFromPosition (0).y + self.TextHeight (0)
        x, y = self.GetSizeTuple ()
        if y != height:
            self.parent.ReSize (self, height)
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
            if text:
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
        if isinstance (data, types.ClassType) and issubclass (data, ResizingWindow):
            PopupFrame (text, data, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ()))).Show ()
        elif callable (data):
            data (text, self.parent, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ())))
        else:
            self.Embed (text, data)

    def Embed (self, text, data=None):
        self.no_list = 1
        self.ReplaceText (self.start, self.end, text+';', STYLE_EMBED, 1)
        self.GotoPos (self.start+len (text)+1)
        self.SetFocus ()
        if data:
            self.__embed[text] = data
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
                elif self.parent.complete:
                    self.parent.complete ()
        elif self.parent.complete and event.KeyCode () == WXK_F12:
            self.parent.complete ()
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
                    elif self.parent.complete:
                        self.parent.complete ()
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

class PopupFrame (wxFrame):
    def __init__ (self, text, widget_class, originator=None, pos=wxDefaultPosition):
        wxFrame.__init__(self, None, wxNewId (), widget_class.__name__, pos = pos, style=wxSIMPLE_BORDER)
        self.win = widget_class (self, -1, pos = pos, size = wxSize (300, 150), complete = self.OnOK)
        self.text = text
        self.originator = originator
        self.ok = wxButton (self, -1, _("OK"), style=wxBU_EXACTFIT)
        self.cancel = wxButton (self, -1, _("Cancel"), style=wxBU_EXACTFIT)
        EVT_BUTTON (self.ok, self.ok.GetId (), self.OnOK)
        EVT_BUTTON (self.cancel, self.cancel.GetId (), self.OnClose)
        self.__do_layout()

    def __do_layout(self):
        sizer_1 = wxBoxSizer(wxVERTICAL)
        sizer_1.Add(self.win, 1, wxEXPAND, 0)
        sizer_2 = wxBoxSizer (wxHORIZONTAL)
        sizer_2.Add(self.ok, 0, 0)
        sizer_2.Add(self.cancel, 0, 0)
        sizer_1.Add(sizer_2, 0, wxEXPAND)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()

    def OnClose (self, event):
        self.Close ()

    def OnOK (self, event=None):
        if self.originator:
            self.originator.Embed ("%s: %s" % (self.text, self.win.GetSummary ()))
        self.Close ()

if __name__ == '__main__':

    from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList
    from Gnumed.pycommon import gmI18N

    class RecallWindow (ResizingWindow):
        def DoLayout (self):
            self.type = ResizingSTC (self, -1)
            self.date = ResizingSTC (self, -1)
            self.notes = ResizingSTC (self, -1)
            self.type.prev = None
            self.type.next = self.date
            self.date.prev = self.type
            self.date.next = self.notes
            self.notes.prev = self.date
            self.notes.next = None
            self.AddWidget (self.type, "Type")
            self.Newline ()
            self.AddWidget (self.date, "Date")
            self.Newline ()
            self.AddWidget (self.notes, "Notes")

        def GetSummary (self):
            return "%s on %s [%s]" % (self.type.GetText (), self.date.GetText (), self.notes.GetText ())

    class SOAPWindow (ResizingWindow):
        def DoLayout (self):
            Planlist = [{'label':'pencillin V', 'data':1, 'weight':1}, {'label':'penicillin X', 'data':2, 'weight':1},
                {'label':'penicillinamine', 'data':3, 'weight':1}, {'label':'penthrane', 'data':4, 'weight':1},
                {'label':'penthidine', 'data':5, 'weight':1},
                {'label':'recall', 'data':RecallWindow, 'weight':1}]
            AOElist = [{'label':'otitis media', 'data':1, 'weight':1}, {'label':'otitis externa', 'data':2, 'weight':1},
                {'label':'cellulitis', 'data':3, 'weight':1}, {'label':'gingvitis', 'data':4, 'weight':1},
                {'label':'ganglion', 'data':5, 'weight':1}]
            Subjlist = [{'label':'earache', 'data':1, 'weight':1}, {'label':'earache', 'data':1, 'weight':1},
               {'label':'ear discharge', 'data':2, 'weight':1}, {'label':'eardrum bulging', 'data':3, 'weight':1},
               {'label':'sore arm', 'data':4, 'weight':1}, {'label':'sore tooth', 'data':5, 'weight':1}]
            self.S = ResizingSTC (self, -1)
            self.S.AttachMatcher (cMatchProvider_FixedList (Subjlist))
            self.O = ResizingSTC (self, -1)
            self.A = ResizingSTC (self, -1)
            self.A.AttachMatcher (cMatchProvider_FixedList (AOElist))
            self.P = ResizingSTC (self, -1)
            self.P.AttachMatcher (cMatchProvider_FixedList (Planlist))
            self.S.prev = None
            self.S.next = self.O
            self.O.prev = self.S
            self.O.next = self.A
            self.A.prev = self.O
            self.A.next = self.P
            self.P.prev = self.A
            self.P.next = None
            self.AddWidget (self.S, "Subjective")
            self.Newline ()
            self.AddWidget (self.O, "Objective")
            self.Newline ()
            self.AddWidget (self.A, "Assessment")
            self.Newline ()
            self.AddWidget (self.P, "Plan")
            self.SetValues ({"Subjective":"sore ear", "Plan":"Amoxycillin"})

    class SOAPPanel (wxPanel):
        def __init__ (self, parent, id):
            wxPanel.__init__ (self, parent, id)
            sizer = wxBoxSizer (wxVERTICAL)
            self.soap = SOAPWindow (self, -1)
            self.save = wxButton (self, -1, _(" Save "))
            self.delete = wxButton (self, -1, _(" Delete "))
            self.new = wxButton (self, -1, _(" New "))
            self.list = wxListBox (self, -1, style=wxLB_SINGLE | wxLB_NEEDED_SB)
            EVT_BUTTON (self.save, self.save.GetId (), self.OnSave)
            EVT_BUTTON (self.delete, self.delete.GetId (), self.OnDelete)
            EVT_BUTTON (self.new, self.new.GetId (), self.OnNew)
            EVT_LISTBOX (self.list, self.list.GetId (), self.OnList) 
            self.__do_layout()

        def __do_layout (self):
            sizer_1 = wxBoxSizer(wxVERTICAL)
            sizer_1.Add(self.soap, 3, wxEXPAND, 0)
            sizer_2 = wxBoxSizer (wxHORIZONTAL)
            sizer_2.Add(self.save, 0, 0)
            sizer_2.Add(self.delete, 0, 0)
            sizer_2.Add(self.new, 0, 0)
            sizer_1.Add(sizer_2, 0, wxEXPAND)
            sizer_1.Add(self.list, 3, wxEXPAND, 0)
            self.SetAutoLayout(1)
            self.SetSizer(sizer_1)
            sizer_1.Fit(self)
            sizer_1.SetSizeHints(self)
            self.Layout()

        def OnDelete (self, event):
            self.soap.Clear ()
            sel = self.list.GetSelection ()
            if sel >= 0:
                self.list.Delete (sel)

        def OnNew (self, event):
            sel = self.list.GetSelection ()
            if sel >= 0:
                self.OnSave (None)
            self.soap.Clear ()
            self.list.SetSelection (sel, 0)

        def OnSave (self, event):
            data = self.soap.GetValues ()
            title = data['Assessment'] or data['Subjective'] or data['Plan'] or data['Objective']
            self.soap.Clear ()
            sel = self.list.GetSelection ()
            if sel < 0:
                self.list.Append (title, data)
            else:
                self.list.SetClientData (sel, data)
                self.list.SetString (sel, title)

        def OnList (self, event):
            self.soap.SetValues (event.GetClientData ())

    class testFrame (wxFrame):
        def __init__ (self, title):
            wxFrame.__init__ (self, None, wxNewId (), "test SOAP", size = wxSize (350, 200)) # this frame will have big fat borders
            EVT_CLOSE (self, self.OnClose)
            sizer = wxBoxSizer (wxVERTICAL)
            panel = SOAPPanel (self, -1)
            sizer.Add (panel, 1, wxGROW)
            self.SetSizer (sizer)
            self.SetAutoLayout(1)
            sizer.Fit (self)
            self.Layout ()

        def OnClose (self, event):
            self.Destroy ()


    class testApp (wxApp):
        def OnInit (self):
            self.frame = testFrame ("testFrame")
            self.frame.Show ()
            return 1

    app = testApp (0)
    app.MainLoop ()

#================================================================
# $Log: SOAP2.py,v $
# Revision 1.8  2004-11-09 13:13:18  ihaywood
# Licence added
#
# Segfaults fixed.
# Demonstration listbox for multiple SOAP entries, I had intended to drop
# this into the gnumed client, will check what Carlos is doing
#
# Still have vanishing cursor problem when returning  from a popup, can't
# seem to get it back even after explicit SetFocus ()
#
# Revision 1.7  2004/11/09 11:20:59  ncq
# - just silly cleanup
#
# Revision 1.6  2004/11/09 11:19:47  ncq
# - if we know that parent of ResizingSTC must be
#   ResizingWindow we can test for it
# - added some CVS keywords
# - this should not be a physical replacement for the edit
#   area, just a logical one where people want to use it !
#   IOW we will keep gmEditArea around as it IS a good design !
#
#----------------------------------------------------------------
# revision 1.5
# date: 2004/11/09 02:05:20;  author: ihaywood;  state: Exp;  lines: +106 -100
# crashes less often now, the one stickler is clicking on the
# auto-completion list causes a segfault.
#
# This is becoming a candidate replacement for cEditArea
#
# revision 1.4
# date: 2004/11/08 09:36:28;  author: ihaywood;  state: Exp;  lines: +86 -77
# fixed the crashing bu proper use of wxSize.SetItemMinSize (when all else
# fails, read the docs ;-)
#
# revision 1.3
# date: 2004/11/08 07:07:29;  author: ihaywood;  state: Exp;  lines: +108 -22
# more fun with semicolons
# popups too: having a lot of trouble with this, many segfaults.
#
# revision 1.2
# date: 2004/11/02 11:55:59;  author: ihaywood;  state: Exp;  lines: +198 -19
# more feaures, including completion box (unfortunately we can't use the
# one included with StyledTextCtrl)
#
# revision 1.1
# date: 2004/10/24 13:01:15;  author: ihaywood;  state: Exp;
# prototypical SOAP editor, secondary to Sebastian's comments:
#	- Now shrinks as well as grows boxes
#	- TAB moves to next box, Shift-TAB goes back
