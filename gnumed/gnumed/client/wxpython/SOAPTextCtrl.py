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
A pluggable autocompletion mechanism is provided
"""

import string, re

from wxPython.wx import *
from wxPython.stc import *

if __name__ == "__main__":
    import sys
    sys.path.append ("../..")
from Gnumed.pycommon import gmLog, gmI18N

STYLE_HEADER=1
STYLE_TEXT=2
STYLE_KEYWORD=3

class SOAPTextCtrl (wxStyledTextCtrl):
    def __init__ (self, parent, id, headers = None, matchers = {}):
        """
        @type parent: wxWindow
        @param parent: the parent widget
        @type id: number
        @paramid: the window ID
        @type headers: list of strings
        @param headers: the headers to be displayed in the widget, in order
        @type matchers: dictionary of L{Gnumed.pycommon.gmMatchProvider.cMatchProvider}
        @param matchers: the plugged match providers, by activating keyword,
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
        if headers is None:
		    self.headers = [
                _('Subjective'),
                _('Objective'),
                _('Assessment'),
                _('Plan')
            ]
        else:
            self.headers = headers
        # FIXME: do we need to check that all headers have matchers
        # and set missing ones to gmNull.cNull() ?
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
                self.__matcher = None
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
            elif event.KeyCode () in [WXK_LEFT, WXK_BACK] and pos > 0:
                self.__matcher = None
                if self.GetStyleAt (pos-1) == STYLE_HEADER:
                    # trying to move left onto a header, veto
                    pass
                else:
                    event.Skip ()
            elif event.KeyCode () == WXK_UP:
                self.__matcher = None
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
                self.__matcher = None
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
                if not self.AutoCompActive () and len (self.autocompstr) > 0:
                    if self.__matcher is None:
                        self.__find_matcher ()
                    if self.__matcher:
                        flag, self.mlist = self.__matcher.getMatches (self.autocompstr)
                        if flag:
                            self.UserListShow (1, string.join ([i['label'] for i in self.mlist], '\n'))
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
        self.__matcher = None
        pos = self.PositionFromPoint (event.GetPosition ())
        if self.GetStyleAt (pos) == STYLE_HEADER:
            doclen = self.GetLength ()
            while pos < doclen and self.GetCharAt (pos) != 10:
                pos += 1 # go to the end of line
            self.GotoPos (pos)
        else:
            event.Skip ()

    def __find_matcher (self):
        pos = self.GetCurrentPos ()
        text = self.GetText ()
        highestpos = -1
        for (name, matcher) in self.matchers.items ():
            rfind = string.rfind (text, name, 0, pos)
            if rfind > highestpos:
                highestpos = rfind
                self.__matcher = matcher
            


### For testing only

from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

AOElist = [{'label':'otitis media', 'data':1, 'weight':1}, {'label':'otitis externa', 'data':2, 'weight':1},
            {'label':'cellulitis', 'data':3, 'weight':1}, {'label':'gingvitis', 'data':4, 'weight':1},
            {'label':'ganglion', 'data':5, 'weight':1}]

Subjlist = [{'label':'earache', 'data':1, 'weight':1}, {'label':'earache', 'data':1, 'weight':1},
           {'label':'ear discahrge', 'data':2, 'weight':1}, {'label':'eardrum bulging', 'data':3, 'weight':1},
           {'label':'sore arm', 'data':4, 'weight':1}, {'label':'sore tooth', 'data':5, 'weight':1}]

Planlist = [{'label':'pencillin V', 'data':1, 'weight':1}, {'label':'penicillin X', 'data':2, 'weight':1},
            {'label':'penicillinamine', 'data':3, 'weight':1}, {'label':'penthrane', 'data':4, 'weight':1},
            {'label':'penthidine', 'data':5, 'weight':1}]

class testFrame(wxFrame):
    def __init__(self, title):
        # begin wxGlade: MyFrame.__init__
        wxFrame.__init__(self, None, wxNewId (), title)
        matchers = {"AOE": cMatchProvider_FixedList (AOElist), "Plan": cMatchProvider_FixedList (Planlist),
                    "Subj": cMatchProvider_FixedList (Subjlist), "Obj": None}
        self.text_ctrl_1 = SOAPTextCtrl(self, -1, headers=['RFE', "Subj", "Obj", "Assess", "AOE", "Plan"], matchers = matchers)
        self.text_ctrl_1.set_data ({'RFE':'earache', 'Assess':'otitis media'})
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
