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
This widget allows the display of SOAP notes, or similar, with
highlighted headings which are protected from user editing.
A pluggable autocompletion mechanism is provided
"""

import string, re

from wxPython.wx import *
from wxPython.stc import *

#if __name__ == "__main__":
import sys
sys.path.append ("../..")
from Gnumed.pycommon import gmLog, gmI18N

STYLE_HEADER=1
STYLE_TEXT=2
STYLE_EMBED=4
STYLE_KEYWORD=3

TEXT=1
NUMBER=2
DATE=3
SELECTION=4

class myTimer (wxTimer):

    def __init__ (self, funct):
        self.funct = funct
        wxTimer.__init__ (self)
        self.Start (300, wxTIMER_ONE_SHOT)

    def Notify (self):
        self.funct ()

class SOAPTextCtrl (wxStyledTextCtrl):
    def ReplaceText (self, start, length, text, style=-1):
        """
        Oddly, the otherwise very rich wxSTC API does not provide an
        easy way to replace text, so we provide it here.

        @param start: the position in the text to start from
        @param length: the length of the string to replace
        @param text: the new string
        @param style: the style for the replaced string
        """
        self.SetTargetStart (start)
        self.SetTargetEnd (start+length)
        self.ReplaceTarget (text)
        if style > -1:
            self.StartStyling (start, 0xFF)
            self.SetStyling (length, style)


    def __get_word_by_style (self, pos, style):
        oldpos = pos
        s = ''
        m = self.GetLength ()
        while pos < m and self.GetStyleAt (pos) == style:
            s += chr (self.GetCharAt (pos))
            pos += 1
        oldpos = oldpos-1
        while pos >= 0  and self.GetStyleAt (pos) == style:
            s = chr (self.GetCharAt (pos)) + s
            pos -= 1
        return pos+1, s

    def __get_word_by_lex (self, pos):
        s = ''
        pos = pos-1
        while pos >= 0  and chr (self.GetCharAt (pos)) in string.letters:
            s = chr (self.GetCharAt (pos)) + s
            pos -= 1
        return pos+1, s

    def __calc_section (self, pos):
        self.section_end = pos
        m = self.GetLength ()
        while self.section_end < m and self.GetStyleAt (self.section_end) != STYLE_HEADER:
            self.section_end += 1
        self.section_end -=1
        self.section_start = pos-1
        while self.section_start >= 0 and self.GetStyleAt (self.section_start) != STYLE_HEADER:
            self.section_start -= 1
        section_name = ''
        pos = self.section_start -1
        self.section_start += 1
        while pos >= 0  and chr (self.GetCharAt (pos)) in string.letters:
            section_name = chr (self.GetCharAt (pos)) + section_name
            pos -= 1
        self.section = 0
        while self.headers[self.section][0] != section_name:
            self.section += 1
            if self.section >= len (self.headers):
                sys.exit (1)
            
    def __init__ (self, parent, id, pos=wxDefaultPosition, size= None, style=0):
        """
        @type parent: wxWindow
        @param parent: the parent widget
        @type id: number
        @param id: the window ID
        @type pos: wxPoint
        @param pos: the window position
        @type size: wxSize
        @param size: the window's size
        @type style: integer
        @param style: the window's style
        """
        if size is None:
            size = wxSize (400, 200)
        wxStyledTextCtrl.__init__ (self, parent, id, pos, size, style)
        self.parent = parent
        id = self.GetId ()
        self.SetWrapMode (wxSTC_WRAP_WORD)
        self.StyleSetSpec (STYLE_HEADER, "fore:#7F11010,bold,face:Times,size:12")
        self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
        self.StyleSetSpec (STYLE_KEYWORD, "fore:#3030A0")
        self.SetEOLMode (wxSTC_EOL_LF)
        self.SetMarginWidth (1, 0)
        self.AutoCompStops ("()<>,.;:'\"[]{}\\|/? !@#$%^&*")
        self.__embeds = {}
        self.autocompstr = ''
        self.__ids = {}
        self.headers = self.GetHeaders ()
        self.timer = None
        self.__popup = None
        self.replace_len = 0
        self.popup = 0
        self.AutoCompSetSeparator (10)
        EVT_KEY_DOWN (self, self.__keypressed)
        EVT_LEFT_DOWN (self, self.__mouse_down)
        EVT_STC_USERLISTSELECTION (self, id, self.__userlist)

    def GetHeaders (self):
        """
        Sets the list of headers

        @return: list of tuple (header, type, match provider, poppers)
        """
        return []
    
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
        self.__write_headings (data or {})
        if data and data.has_key ('__ids'):
            self.__ids = data['__ids']

    def __write_headings (self, data={}):
        pos = 0
        for heading, type, matcher, poppers in self.headers:
            if data.has_key (heading):
                text = "%s: %s\n" % (heading, data[heading])
            else:
                text = "%s:\n" % heading
            self.AddText (text)
            self.StartStyling (pos, 0xFF)
            self.SetStyling (len (heading)+1, STYLE_HEADER)
            pos += len (text)
            
        self.GotoPos (len (self.headers[0][0])+1)
        self.section = 0
        self.section_start = len (self.headers[0][0])+1
        self.section_end = len (self.headers[0][0])+1
        if data.has_key (self.headers[0][0]):
            self.section_end += 1+len (data[self.headers[0][0]])

    def __validate_number (self):
        pass

    def __validate_date (self):
        pass

    def __selectionBad (self):
        return 0
    
    def Embed (self, text, clas, state):
        n= 1
        ending = ''
        while self.__embeds.has_key (text + ending):
            n += 1
            ending = '#%d' % n
        self.__embeds[text+ ending] = {'class':clas, 'state':state}
        self.ReplaceText (self.GetCurrentPos ()-self.replace_len, self.replace_len, text+ending, STYLE_EMBED)
        

    def get_data (self):
        """
        Parses the contents and obtains the text by heading.
        If parsing fails (ie. the user has edited the headers
        despite my best efforts to prevent that) the whole
        widget text is returned under the key 'text'

        @rtype: dictionary of strings
        @return: dictionary keyed by header name
        """
        r = re.compile (string.join ([h[0] for h in self.headers], ':(.*)') + ':(.*)', re.S)
        mo = r.match (self.GetText ())
        if not mo:
            gmLog.gmDefLog.Log (gmLog.lErr, "the SOAP structure has been corrupted")
            return {'text':self.GetText ()}
        else:
            ret = {}
            i = 1
            for hdr, type, matcher, poppers in self.headers:
                ret[hdr] = mo.group (i)
                i += 1
            ret['__ids'] = self.__ids
            return ret

        
    def __keypressed (self, event):
        pos = self.GetCurrentPos ()
        if self.timer:
            self.timer.Stop ()
            self.timer = None
        if self.__popup:
            self.__popup.Destroy ()
            self.__popup = None
        if self.AutoCompActive ():
            event.Skip ()
            return
        hdr, typ, matcher, poppers = self.headers[self.section]
        if event.KeyCode () == WXK_RETURN:
            if self.GetCharAt (pos) == 10 and not event.ControlDown ():
                # we are at the end of a line
                self.__cursorMoved (pos + 1)
            elif self.GetStyleAt (pos) in  [STYLE_HEADER, STYLE_EMBED]:
                self.__cursorMoved (pos)
            else:
                if typ == TEXT:
                    event.Skip ()
        elif event.KeyCode () == WXK_F12:
            if self.popup:
                self.parent.Embed (self.GetSummary (), self.get_data ())
                self.parent.SetFocus ()
                self.Destroy ()
            else:
                self.Process (self.get_data ())
        elif event.KeyCode () == WXK_LEFT:
            if pos > 0:
                self.__cursorMoved (pos -1)
        elif event.KeyCode () == WXK_RIGHT:
            m = self.GetLength ()
            if pos < m:
                self.__cursorMoved (pos+1)
        elif event.KeyCode () == WXK_UP:
            line = self.LineFromPosition (pos)
            col = self.GetColumn (pos)
            if line > 0:
                line -= 1
                lineend = self.GetLineEndPosition (line)
                pos = self.PositionFromLine (line) + col
                if pos > lineend:
                    pos = lineend
                self.__cursorMoved (pos)
        elif event.KeyCode () == WXK_DOWN:
            line = self.LineFromPosition (pos)
            col = self.GetColumn (pos)
            line += 1
            pos = self.PositionFromLine (line) + col
            lineend  = self.GetLineEndPosition (line)
            if pos > lineend:
                pos = lineend
            self.__cursorMoved (pos)
        elif event.KeyCode () == WXK_ESCAPE:
            self.escape ()
        elif event.KeyCode () < 256 and not (event.ControlDown () and event.AltDown ()):
            # these are "text-damaging" events
            if event.KeyCode () == WXK_BACK and pos > 0:
                pos -= 1
            style = self.GetStyleAt (pos)
            if self.__selectionBad ():
                return
            elif style == STYLE_HEADER:
                # this should never happen
                self.__cursorMoved (pos)
            elif style == STYLE_EMBED:
                # delete the embedded
                start, word = self.__get_word_by_style (pos, STYLE_EMBED)
                self.ReplaceText (start, len (word), '')
                if not event.KeyCode () in [WXK_DELETE, WXK_BACK]:
                    self.Skip ()
                del self.__embeds[word]
            else:
                if typ == NUMBER:
                    if chr(event.KeyCode ()) in '0123456789.,-+E\x08\x7F':
                        event.Skip ()
                elif typ == DATE:
                    if chr (event.KeyCode ()) in '0123456789/.-DWMY\x08\x7F':
                        event.Skip ()
                elif typ == SELECTION:
                    if self.__ids.has_key (hdr):
                        del self.__ids[hdr]
                    event.Skip ()
                else:
                    event.Skip ()
                if typ == TEXT or typ == SELECTION:
                    if chr (event.KeyCode ()) in string.letters:
                        start, word = self.__get_word_by_lex (pos)
                        word += chr (event.KeyCode ())
                        word = word.lower ()
                        if matcher:
                            flag, self.mlist = matcher.getMatches (word)
                            if flag:
                                self.replace_len = len (word)
                                self.__map_text_to_id = dict ([(i['label'], i['data']) for i in self.mlist])
                                self.UserListShow (1, string.join ([i['label'] for i in self.mlist], '\n'))
                        if poppers.has_key (word):
                            self.replace_len = len (word)
                            self.__pop (poppers[word], None)             
        else:
            # FIXME: need to provide for Undo, delete word, etc.
            pass

    def __cursorMoved (self, pos):
        m = self.GetLength ()
        if pos < m:
            style = self.GetStyleAt (pos)
            if style == STYLE_HEADER:
                self.__cursorMoved (pos+1)
            elif style == STYLE_EMBED:
                start, word = self.__get_word_by_style (pos, STYLE_EMBED)
                if pos < start+len (word)-1:
                    self.GotoPos (start+len (word))
                else:
                    self.GotoPos (start-1)
                self.__pop (self.__embeds[word]['class'], self.__embeds[word]['state'])
            else:
                oldpos = self.GetCurrentPos ()
                moved_section = pos < self.section_start or pos-oldpos > 1
                hdr, typ, matcher, poppers = self.headers[self.section]
                if moved_section and typ == NUMBER:
                    self.__validate_number ()
                if moved_section and typ == DATE:
                    self.__validate_date ()
                self.__calc_section (pos)
                hdr, typ, matcher, poppers = self.headers[self.section]
                self.GotoPos (pos)
                if typ == SELECTION and moved_section:
                    flag, self.mlist = matcher.getAllMatches ()
                    if flag:
                        self.replace_len = 0
                        self.__map_text_to_id = dict ([(i['label'], i['data']) for i in self.mlist])
                        self.UserListShow (1, string.join ([i['label'] for i in self.mlist], '\n'))
        else:
            if self.popup:
                self.parent.SetFocus ()
                self.parent.Embed (self.GetSummary (), self.get_data ())
                self.Destroy ()
                
    def __userlist (self, event):
        text = event.GetText ()
        hdr, typ, matchers, poppers = self.headers[self.section]
        if typ == TEXT:
            pos = self.GetCurrentPos ()
            start = pos - self.replace_len
        else:
            start = self.section_start
            pos = self.section_end
            self.__ids[hdr] = self.__map_text_to_id[text]
        self.SetTargetEnd (pos)
        self.SetTargetStart (start)
        self.ReplaceTarget (text)
        self.StartStyling (start, 0xFF)
        self.SetStyling (len (text), STYLE_KEYWORD)
        self.__cursorMoved (start + len (text)+1)
        
    def __mouse_down (self, event):
        if self.AutoCompActive ():
            self.AutoCompCancel ()
        if self.__popup:
            self.__popup.Destroy ()
            self.__popup = None
        if self.timer:
            self.timer.Stop ()
            self.timer = None
        pos = self.PositionFromPoint (event.GetPosition ())
        self.__cursorMoved (pos)

    def escape (self):
        """
        Escape pressed
        Descendants may want to override this
        """
        if self.popup:
            self.parent.SetFocus ()
            self.Destroy ()
            

    def __pop (self, pclass, state):
            x, y = self.GetSizeTuple ()
            pos = self.PointFromPosition (self.GetCurrentPos ())
            x = x/4
            width = x*3
            height = y/2
            if pos.y > height:
                # cursor is in the bottom half of the window
                y = pos.y-height
            else:
                y = pos.y
            self.__popup = pclass (self, -1, wxPoint (x, y), wxSize (width, height), wxSIMPLE_BORDER)
            self.__popup.set_data (state)
            self.__popup.popup = 1
            self.__popup.Show ()
            self.__popup.SetFocus ()

### For testing only


class RxCtrl (SOAPTextCtrl):
    def GetHeaders (self):
        return [('Drug', TEXT, None, {}),
                ('Dose', TEXT, None, {}),
                ('Frequency', NUMBER, None, {}),
                ('Date', DATE, None, {})]

        
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

class MySOAPCtrl (SOAPTextCtrl):
    def GetHeaders (self):
        return [
            (_('Subjective'), TEXT, cMatchProvider_FixedList (Subjlist), {}),
            (_('Objective'), TEXT, None, {}),
            (_('Assessment'), SELECTION, cMatchProvider_FixedList (AOElist), {}),
            (_('Plan'), TEXT, cMatchProvider_FixedList (Planlist), {'prescribe':RxCtrl})
            ]



class testFrame(wxFrame):
    def __init__(self, title):
        # begin wxGlade: MyFrame.__init__
        wxFrame.__init__(self, None, wxNewId (), title)
        self.text_ctrl_1 = MySOAPCtrl(self, -1)
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
