#!/usr/bin/env python
##     Text control for SOAP notes
##     Copyright (C) 2004 Ian Haywood

##     This program is free software; you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation; either version 2 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.

##     You should have received a copy of the GNU General Public License
##     along with this program; if not, write to the Free Software
##     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""
This widget allows the display of SOAP notes, or similar,
with
highlighted headings which are portected from user editing.
A pluggable autocompletion mechanism will be provided
"""
    
import string, re
from wxPython.wx import *
from wxPython.stc import *
if __name__ == "__main__":
    import sys
    sys.path.append ("../..")
from Gnumed.pycommon import gmLog

STYLE_HEADER=1
STYLE_TEXT=2
STYLE_KEYWORD=3

class SOAPTextCtrl (wxStyledTextCtrl):
    def __init__ (self, parent, id, headers = ['Subjective', 'Objective', 'Assessment', 'Plan'], matchers = {}):
        """
        @type parent: wxWindow
        @param parent: the parent widget
        @type id: number
        @paramid: the window ID
        @type headers: list of strings
        @param headers: the headers to displayed in the widget, in order
        @type matchers: dictionary of cMatchProvider
        @param matchers: the plugged match providers, by activationg keyword,
                         which may or may not be the same as rhe headers 
        """
        wxStyledTextCtrl.__init__ (self, parent, id, size = wxSize (400, 400))
        id = self.GetId ()
        self.SetWrapMode (wxSTC_WRAP_WORD)
        self.StyleSetSpec (STYLE_HEADER, "fore:#7F11010,bold,face:Times,size:12")
        self.StyleSetSpec (STYLE_KEYWORD, "fore:#4040B0")    
        self.SetEOLMode (wxSTC_EOL_LF)
        self.SetMarginWidth (1, 0)
        self.AutoCompStops ("()<>,.;:'\"[]{}\\|/? !@#$%^&*")
        self.autocompstr = ''
        self.headers = headers
        self.matchers = matchers
        self.__matcher = None
        self.AutoCompSetSeparator (10)
        self.__write_headings ()
        EVT_KEY_DOWN (self, self.__keypressed)
        EVT_LEFT_DOWN (self, self.__mouse_down)
        EVT_STC_USERLISTSELECTION (self, id, self.__userlist)

    def ClearAll (self):
        """
        Clears the widget and writes the headers again
        """
        wxStyledTextCtrl.ClearAll (self)
        self.SetEOLMode (wxSTC_EOL_LF)
        self.__write_headings ()

    def set_data (self, data):
        """
        Clears the contents of the widget,
        and sets the values of the various sections

        @type data: dictionary of strings
        @param data: the text to insert, keyed by header name
        """
        wxStyledTextCtrl.ClearAll (self)
        self.SetEOLMode (wxSTC_EOL_LF)
        self.__write_headings (data)

    def __write_headings (self, data={}):
        pos = 0
        for heading in self.headers:
            text = "%s: %s\n" % (heading, data.setdefault(heading, ''))
            self.AddText (text)
            self.StartStyling (pos, 0xFF)
            self.SetStyling (len (heading)+1, STYLE_HEADER)
            pos += len (text)
            
        self.GotoPos (len (self.headers[0]))


    def get_data (self):
        """
        Parses the contents and obtains the text by number

        @rtype: dictionary of strings
        @return : dictionary keyed by header name
        """
        r = re.compile (string.join (self.headers, ':(.*)') + ':(.*)', re.S)
        mo = r.match (self.GetText ())
        if not mo:
            gmLog.gmDefLog.Log (gmLog.lErr, "the SOAP structure has been corrupted")
            return None
        else:
            ret = {}
            i = 1
            for hdr in self.headers:
                ret[hdr] = mo.group (i)
                i += 1
            return ret
        
    def __keypressed (self, event):
        pos = self.GetCurrentPos ()
        if self.AutoCompActive ():
            event.Skip ()
        else:
            if event.KeyCode () in [WXK_RETURN, WXK_RIGHT, WXK_DELETE]:
                if self.GetCharAt (pos) == 10: # we are at the end of a line
                    pos += 1
                    if self.GetStyleAt (pos) == STYLE_HEADER: # the next line is a header
                        doclen = self.GetLength ()
                        while pos < doclen and self.GetCharAt (pos) != 10:
                            pos += 1 # go to the end of line
                        self.GotoPos (pos)
                    else:
                        event.Skip ()
                else:
                    event.Skip ()
            elif event.KeyCode () in [WXK_LEFT, WXK_BACK] and pos > 0 and self.GetStyleAt (pos-1) == STYLE_HEADER:
                # trying to move left onto a header, veto
                pass
            elif event.KeyCode () == WXK_UP:
                line = self.LineFromPosition (pos)
                col = self.GetColumn (pos)
                if line > 0:
                    line -= 1
                    lineend = self.GetLineEndPosition (line)
                    pos = self.PositionFromLine (line) + col
                    if (pos <= lineend and self.GetStyleAt (pos) == STYLE_HEADER) or pos > lineend:
                        self.GotoPos (lineend)
                    else:
                        #print "line : %d pos: %d lineend: %d" % (line, pos, lineend)
                        event.Skip ()
            elif event.KeyCode () == WXK_DOWN:
                line = self.LineFromPosition (pos)
                col = self.GetColumn (pos)
                line += 1
                pos = self.PositionFromLine (line) + col
                lineend  = self.GetLineEndPosition (line)
                if pos > 0 and not (pos < lineend and self.GetStyleAt (pos) == STYLE_HEADER):
                    event.Skip ()
                else:
                    self.GotoPos (lineend)
            else:
                event.Skip ()
        if event.KeyCode () < 255:
            ch = string.lower (chr (event.KeyCode ()))
            if ch in string.letters:
                self.autocompstr += ch
                if not self.AutoCompActive ():
                    clist = []
                    for i in completions:
                        if string.find (i, self.autocompstr) == 0:
                            clist.append (i)
                    if len (clist) > 0 and len (clist) < 7:
                        clist.sort ()
                        self.UserListShow (1, string.join (clist, '\n'))
            else:
                if ch != '\r':
                    self.autocompstr = ''

    def __userlist (self, event):
        pos = self.GetCurrentPos ()
        self.SetTargetEnd (pos)
        start = pos - len (self.autocompstr)
        self.SetTargetStart (start)
        text = event.GetText ()
        self.ReplaceTarget (text)
        self.StartStyling (start, 0xFF)
        self.SetStyling (len (text), STYLE_KEYWORD)
        self.GotoPos (start + len (text))
        
    def __mouse_down (self, event):
        pos = self.PositionFromPoint (event.GetPosition ())
        if self.GetStyleAt (pos) == STYLE_HEADER:
            doclen = self.GetLength ()
            while pos < doclen and self.GetCharAt (pos) != 10:
                pos += 1 # go to the end of line
            self.GotoPos (pos)
        else:
            event.Skip ()


### For testing only


completions = ['oesophagus', 'febrile', 'phlegmon', 'anaesthetic', 'phenoxybenzylpenicillin', 'penicillinamine']

class testFrame(wxFrame):
    def __init__(self, title):
        # begin wxGlade: MyFrame.__init__
        wxFrame.__init__(self, None, wxNewId (), title)
        self.text_ctrl_1 = SOAPTextCtrl(self, -1)
        self.text_ctrl_1.set_data ({'Subjective':'earache', 'Assessment':'otitis media'})
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
        print self.text_ctrl_1.get_data ()
        self.Destroy ()

# end of class MyFrame


class testApp (wxApp):
    def OnInit (self):
        self.frame = testFrame ("Test SOAP")
        self.frame.Show ()
        return 1

if __name__ == '__main__':
    app = testApp (0)
    app.MainLoop ()
