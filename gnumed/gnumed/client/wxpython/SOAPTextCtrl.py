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

import string, re, time

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
    def ReplaceText (self, start, length, text, style=-1, space=0):
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
        if space:
            self.ReplaceTarget (text + " ")
        else:
            self.ReplaceTarget (text)
        if style > -1:
            self.StartStyling (start, 0xFF)
            self.SetStyling (len (text), style)

    def __get_word_by_style (self, pos, style):
        oldpos = pos
        s = ''
        m = self.GetLength ()
        while pos < m and self.GetStyleAt (pos) == style:
            s += chr (self.GetCharAt (pos))
            pos += 1
        pos = oldpos-1
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
        self.__data = {}
        self.__text = None
        self.__we_are_new = 1
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
        Sets the list of headers, must be overrided by descendants
        - header: the string labelling the section
        - type: one of TEXT, NUMBER, DATE, SELECTION
        SELECTION behaves like text except the match provider result replaces
        all text in that section
        @return: list of tuple (header, type, match provider, poppers)
        """
        return []


    def GetSummary (self, data):
        """
        Returns a brief summary string for displaying in embeds
        """
        return 'SOAP'


    def Process (self, data):
        """
        Performs processing: i.e. commits data to the backend
        """
        pass
    
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
        if data and data.has_key ('__data'):
            self.__we_are_new = 0
            self.__data = data['__data']
        if data and data.has_key ('__text'):
            self.__text = data['__text']

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
            
        self.section = 0
        self.section_start = len (self.headers[0][0])+1
        self.section_end = len (self.headers[0][0])+1
        if data.has_key (self.headers[0][0]):
            self.section_end += 1+len (data[self.headers[0][0]])
        self.GotoPos (self.section_end)
        
    def __validate_number (self):
        s = ''
        pos = self.section_start
        while pos < self.GetLength () and self.GetCharAt (pos) != 10: 
            s += chr (self.GetCharAt (pos))
            pos += 1
        s = s.strip ()
        try:
            self.__data[self.headers[self.section][0]] = float (s)
            return 1
        except:
            #wxMessageBox ("%s is not a valid number" % s, "Invalid entry", wxICON_ERROR | wxOK)
            wxBell ()
            return 0

    def __validate_date (self):
        s = ''
        pos = self.section_start
        while pos < self.GetLength () and self.GetCharAt (pos) != 10: 
            s += chr (self.GetCharAt (pos))
            pos += 1
        s_len = len (s)
        s = s.strip ()
        t = time.localtime (time.time ())
        year = -1
        unit = ''
        day = t[2]
        month = t[1]
        year = t[0]
        m = re.match ("([0-9]+)/([0-9]+)$", s)
        if m:
            day = int (m.group (1))
            month = int (m.group (2))
            if month < t[1] or (month == t[1] and day < t[2]):
                year +=1
            self.display_date (day, month, year, s_len)
            return 1
        else:
            m = re.match ("([0-9]+)([%s])" % _('dwmy'), s)
            if m:
                incr = int (m.group (1))
                unit = m.group (2)
            else:
                m = re.match ("-([0-9]+)([%s])" % _('dwmy'), s)
                if m:
                    incr = -int (m.group (1))
                    unit = m.group (2)
            if unit:
                incr *= 86400 # day in seconds
                if unit == _('dwmy')[1]:
                    incr *= 7 # a week is 7 days
                elif unit == _('dwmy')[2]:
                    incr *= 30
                elif unit == _('dwmy')[3]:
                    incr *= 365
                # now we have offset in seconds
                t = time.time () # UNIX time (seconds since 1970)
                t += incr # do offset
                t = time.localtime (t)
                year = t[0]
                month = t[1]
                day = t[2]
                self.display_date (day, month, year, s_len)
                return 1
            else:
                m = re.match ("([0-9]+)/([0-9]+)/([0-9]+)", s)
                if m:
                    day = int (m.group (1))
                    month = int (m.group (2))
                    year = int (m.group (3))
                    self.__data[self.headers[self.section][0]] = (day, month, year)
                    return 1
                else:
                    #wxMessageBox ("%s is not a valid date" % s, "Invalid entry", wxICON_ERROR | wxOK)
                    wxBell ()
                    return 0
        

    def display_date (self, day, month, year, s_len):
        self.ReplaceText (self.section_start, s_len, "%d/%d/%d" % (day, month, year))
        self.__data[self.headers[self.section][0]] = (day, month, year)

    def __selectionBad (self, start, end):
        for i in range (start, end):
            if self.GetStyleAt (i) in [STYLE_HEADER, STYLE_EMBED]:
                return 1
        return 0
    
    def Embed (self, text, clas, state):
        n= 1
        ending = ''
        while self.__embeds.has_key (text + ending):
            n += 1
            ending = '#%d' % n
        state['__text'] = text+ending
        self.__embeds[text+ ending] = {'class':clas, 'state':state}
        self.ReplaceText (self.GetCurrentPos ()-self.replace_len, self.replace_len, text+ending, STYLE_EMBED, 1)
        self.GotoPos (self.GetCurrentPos ()+len (text+ending)+1)

    def Reembed (self, state):
        self.__embeds[state['__text']]['state'] = state

    def get_data (self):
        """
        Parses the contents and obtains the text by heading.
        If parsing fails (ie. the user has edited the headers
        despite my best efforts to prevent that) the whole
        widget text is returned under the key 'text'

        Extra fields used:
        __text: the label for this widget used in an embed
        __data: a dictionary by header label, for SELECTION types
        the backend ID returned by the match provider,
        None or not present if the user has made no selection
        (there still may be text under this heading, which
        should be used as a new value) For DATE a value as
        (day, month, year) triple may be present, for NUMBER
        a Python numeric object may be present

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
                ret[hdr] = string.strip (mo.group (i))
                i += 1
            ret['__data'] = self.__data
            if self.__text:
                ret['__text'] = self.__text
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
            if self.GetCharAt (pos) == 10 and not event.AltDown ():
                # we are at the end of a line
                self.__cursorMoved (pos + 1)
            elif self.GetStyleAt (pos) in  [STYLE_HEADER, STYLE_EMBED]:
                self.__cursorMoved (pos)
            else:
                if typ == TEXT:
                    self.InsertText (self.GetCurrentPos (), chr (10))
                    self.GotoPos (self.GetCurrentPos ()+1)
        elif event.KeyCode () == WXK_F12:
            if self.popup:
                data = self.get_data ()
                if self.__we_are_new:
                    self.parent.Embed (self.GetSummary (data), self.__class__, data)
                else:
                    self.parent.Reembed (data)
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
            if style == STYLE_HEADER:
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
                    if chr (event.KeyCode ()) in '0123456789/.-%s\x08\x7F' % _('dwmy').upper ():
                        event.Skip ()
                elif typ == SELECTION:
                    if self.__data.has_key (hdr):
                        del self.__data[hdr]
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
        oldpos = self.GetCurrentPos ()
        m = self.GetLength ()
        moved_section = pos < self.section_start or pos-oldpos > 1 or pos >= m
        hdr, typ, matcher, poppers = self.headers[self.section]
        if moved_section and typ == NUMBER:
            if not self.__validate_number ():
                self.GotoPos (oldpos)
                return
        if moved_section and typ == DATE:
            if not self.__validate_date ():
                self.GotoPos (oldpos)
                return
        if pos < m:
            style = self.GetStyleAt (pos)
            if style == STYLE_HEADER:
                self.__cursorMoved (pos+1)
            elif style == STYLE_EMBED:
                start, word = self.__get_word_by_style (pos, STYLE_EMBED)
                if pos < start+len (word)-1:
                    self.GotoPos (start+len (word))
                else:
                    self.GotoPos (start)
                self.__pop (self.__embeds[word]['class'], self.__embeds[word]['state'])
            else:
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
                data = self.get_data ()
                if self.__we_are_new:
                    self.parent.Embed (self.GetSummary (data), self.__class__, data)
                else:
                    self.parent.Reembed (data)
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
            self.__data[hdr] = self.__map_text_to_id[text]
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


class RecallCtrl (SOAPTextCtrl):
    def GetHeaders (self):
        return [('Reason', TEXT, None, {}),
                ('Date', DATE, None, {})]

    def GetSummary (self, data):
        return 'recall -- %s' % data['Reason']
        
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
            (_('Plan'), TEXT, cMatchProvider_FixedList (Planlist), {'recall':RecallCtrl})
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
