#!/usr/bin/python
from wxPython.wx import *
from string import *
import gettext
#_ = gettext.gettext
_ = lambda x: x


"""
A class, extending wxTextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Ruchard Terry's Visual Basic client
"""
__author__ = "Ian Haywood <ihaywood@gnu.org>"
__version__ = "0.1"


def sort (list):
    """
    convience function, implements mergesort on option list
    """
    index = list[0]
    higher = []
    lower = []
    for i in list[1:]:
        if i[1] >= index[1]:
            higher.append (i)
        else:
            lower.append (i)
    r = []
    if higher:
        r = sort (higher)
    r.append (index)
    if lower:
        r.extend (sort (lower))
    return r

class SmartTextCtrl (wxTextCtrl):
    """
    Widget for smart guessing of user fields, after Richard Terry's
    interface.
    Inherits wxTextCtrl.
    """


    def __getOptions (self):
        """ Private function to return options available with what's
    entered"""
        value = self.GetValue ()
        ret = []
        insert = 1
        for i in self.options:
            if lower (i[2][:len (value)]) == lower (value):
                ret.append (i)
        return ret

    def OnSelected (self, n):
        data = self.list.GetClientData (n)
        self.SetValue (self.list.GetString (n))
        self.popup.Dismiss ()
        self.id_callback (data)

    def OnReturn (self):
        number = self.list.Number ()
        if number == 0:
            wxBell () # no value, can't process
        elif number == 1:
            self.OnSelected (0)
        else: # more than one value
            self.listhasfocus = 1 # give focus to list
            self.list.SetSelection (0) # select first value

    def OnDown (self):
        self.listhasfocus = 1 # give focus to list
        self.list.SetSelection (0) # select first value
    
    def __keypress (self, key):
        """ Internal callback for keypress event """
        if self.listhasfocus:
            selected = self.list.GetSelection ()
            if key.GetKeyCode () == WXK_RETURN:
                self.listhasfocus = 0
                self.OnSelected (selected)
            elif key.GetKeyCode () == WXK_DOWN:
                if selected < self.list.Number ()-1:
                    self.list.SetSelection (selected+1)
            elif key.GetKeyCode () == WXK_UP:
                if selected > 0:
                    self.list.SetSelection (selected-1)
                else:
                    # 'focus' returns to textctrl
                    self.list.SetSelection (0, 0)
                    self.listhasfocus = 0
            else: # lose list focus for other characters
                self.listhasfocus = 0
                key.Skip ()
        else:
            if key.GetKeyCode () == WXK_RETURN:
                self.OnReturn ()
            elif key.GetKeyCode () == WXK_DOWN:
                self.OnDown ()
            else:
                key.Skip ()


    def __text (self, event):
        listvalues  = self.__getOptions ()
        self.list.Clear ()
        if self.GetValue () == '*':
            listvalues = self.options # get all values
        if len (self.GetValue ()) == 0:
            self.popup.Dismiss () # popup vanishes on empty string
        else:
            if len (listvalues) == 0:
                self.list.Append (_("No value found"))
            else:
                listvalues == sort (listvalues)# sort by weighting
                for i in listvalues:
                    self.list.Append (i[2], clientData = i[0])
                # recalculate position
                pos = self.ClientToScreen ((0,0))
                sz = self.GetSize ()
                self.popup.Position (pos, (0, sz.height))
                self.popup.Popup ()

    def __list_lineclicked (self, event):
        self.OnSelected (self.list.GetSelection ())

    def resize (self, event):
        sz = self.GetSize ()
        self.list.SetSize ( (sz.width, sz.height*6))
        # as wide as the textctrl, and 6 times the height
        self.panel.SetSize (self.list.GetSize ())
        self.popup.SetSize (self.panel.GetSize ())

    def __init__ (self, parent, id_callback, id = -1, pos =
    wxDefaultPosition, size = wxDefaultSize):
        """
        id_callback holds a refence to another Python function.
        This function is called when the user selects a value.
        This function takes a single parameter -- being the ID of the
        value so selected""" 
        wxTextCtrl.__init__ (self, parent, id, "", pos, size)
        self.SetBackgroundColour (wxColour (200, 100, 100))
        self.parent = parent
        EVT_TEXT (self, self.GetId (), self.__text) # grab key events
        EVT_KEY_UP (self, self.__keypress)
        EVT_SIZE (self, self.resize)
        self.id_callback = id_callback
        self.popup = wxPopupTransientWindow (parent, -1)
        self.panel = wxPanel (self.popup, -1)
        self.list = wxListBox (self.panel, -1, style=wxLB_SINGLE |
                               wxLB_NEEDED_SB)
        self.listhasfocus = 0 # whether list has focus
        
    """
    Sets the list of available options. options consists of a list of
    lists. Each item of of the form  [ID, weighting, string], where ID
    is the SQL id field, weighting is the user weighting used to order
    the items on the list, and string is what appears in the listbox.
    This is intead to recieve directly the output of an appropriate
    SQL query.
    This cn be called multiple times (presumably in response to values
    in other boxes on the screen)c"""
    def SetValues (self, options):
        self.options = options
        self.__getOptions ()
        if len (self.GetValue ()) > 0:
            # check are entered value is on the new list.
            if len (self.listvalues) == 0:
                self.Clear () # clear text
       


if __name__ == '__main__':
    def clicked (data):
        print "Selected :%s" % data
        
    class TestApp (wxApp):
        def OnInit (self):
            frame = wxFrame (None,-4, "Test App", size=wxSize(900,
    400), style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
            tc = SmartTextCtrl (frame, clicked, pos = (50, 50), size =
        (180, 30))
            tc.resize (None)
            tc.SetValues ([[1, 1, "Bloggs"], [2, 1, "Baker"], [3, 2,
        "Jones"], [4, 1, "Judson"], [5, 1, "Jacobs"]])
            frame.Show (1)
            return 1

    app = TestApp ()
    app.MainLoop ()




