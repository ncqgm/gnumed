"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.

This code is PROOF OF CONCEPT only
I give no warrant that it will work, or even compile
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.4 2004-03-07 08:10:22 ihaywood Exp $
__version__ = "$Revision: 1.4 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types

# access our modules
if __name__ == "__main__":
    sys.path.append(os.path.join('..', 'pycommon'))
 
# start logging
from Gnumed.client.pycommon import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
    _log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)
 
from mx import DateTime
#============================================================

class gmFormEngine:
    """
    Ancestor for forms
    No real functionality as yet
    Descendants should override class variables country, type, electronic, date as neccessary
    """

    def process (self, template, params):
        """
        Accept a template [format specific to the engine] and
        dictionary of parameters [specific to the template] for processing into a form.
        Returns a Python file or file-like object representing the
        transmittable form of the form.
        For paper forms, this should be PostScript data or similar.
        """
        pass


class BasicTextForm (gmForm):
    """
    Takes a plain text form and subsitutes the fields
    which are marked using an escape character.
    """

    def __subst (self, match):
        elif self.params.has_key (match): # we have a parameter matching the field
            if type (self.params[match]) is types.ListType:
                self.start_list = 1 # we've got a list, keep repeating this line
                if len (self.params[match]) >= self.index:
                    _log.gmLog (gmLog.lErr, "array field %s exhausted at index %d" % (match, self.index))
                    return ""
                elif len (self.params[match]) == self.index+1: # stop when list exhausted, separate flag so other flags don't overwrite
                    self.stop_list = 1
                return self.params[match][self.index]
            else:
                return self.params[match]
        else:
            _log.Log (gmLog.lErr, "can't find %s in form dictionary" % match)
            return ""
    
    def process (self, template, params, escape='@'):
        regex = "%s(\\w)+" % escape
        result = cStringIO.StringIO ()
        for line in template.split ('\n'):
            self.index = 0
            self.start_list = 0
            self.stop_list = 0
            result.write (re.sub (regex, lambda x: self.__subst (x.group (1)), line) + '\n')
            if self.start_list:
                while not self.stop_list:
                    self.index += 1
                    result.write (re.sub (regex, lambda x: self.__subst (x.group (1)), line) + '\n')
        result.seek (0)
                
                
        
class LaTeXForm (gmForm):
    """
    A forms engine wrapping LaTeX
    """

    def texify (self, item):
        """
        Convience function to escape strings for TeX output
        """

        if type (item) is types.StringType or type (item) is types.UnicodeType:
            item = item.replace ("\\", "\\backspace")
            item = item.replace ("&", "\\&")
            item = item.replace ("$", "\\$")
            item = item.replace ('"', "")
            item = item.replace ("\n", "\\\\ ")
            if len (item).strip () == 0:
                item = "\relax " # sometimes TeX really hates empty strings, this seems to mollify it
        if type (item) is types.ListType: 
            item = [self.texify (i) for i in item]
        if type (item) is types.DictType:
            for i in item.keys ():
                item[i] = self.texify (i)
        return item

    def process (self, params):
        self.params = self.texify (params)
        # create a 'playground' directory
        self.tmp = tempfile.mktemp ()
        os.makedirs (self.tmp)
        self.oldcwd = os.getcwd ()
        os.chdir (self.tmp) # move to the playground
        stdin = popen ("latex", "w", 2048)
        stdin.write (self.latex) # send text. LaTeX spits it's output into stdout.
        # FIXME: send LaTeX  output to the logger
        stdin.close ()
        os.system ("dvips texput.dvi -o texput.ps")
        return file ("texput.ps")

def xdvi (self):
    """
    For testing purposes
    """
    os.system ("xdvi texput.dvi")

    def cleanup (self):
        for i in os.listdir ('.'):
            os.unlink (i)
            os.chdir (self.oldcwd)
            os.rmdir (self.tmp)

class HL7Form (gmForm):
    """
    A base class for forms in the HL7 format.
    Descendants override template () method which uses provided
    methods to form a HL7 message
    When template starts, the MSH segments has already begun, and only fields that need to be filled in
    are 
    """
    
    electronic = 1

    # yes, you could override these
    # don't ask me why
    fieldsep = "|"
    rep = "~"
    comp = "^"
    subcomp = "&"
    esc = "\\"
    maxfield = {"MSH":12}

    def date (self, d):
        """
        Return a date in HL7 format from mxDateTime
        """
        return "%04d%02d%02d" % (d.year, d.month, d.day)

    def time (self, t):
        """
        Return a time in HL7 format
        """
        s = "%02d%02d" % (t.hour, t.minute)
        if t.second > 0:
            if t.second < 10:
                s += "0"
            s += "%.4f" % python.second
        # FIXME: we should add our timezone here
        # FIXME: mx.DateTime lacks any way to express timezone and time precision
        return s

    def timestamp (self, ts):
        return self.date (ts) + self.time (ts)
    
    def text (self, s):
        """
        escape any control chars and newlines that have slipped into the string
        WARNING: we do not escape the escape character itself (usually '\') so
        that HL7 control sequences, which can have various meanings at an application
        logic level, can be included
        """
        s.replace (self.fieldsep, self.esc + 'F' + self.esc)
        s.replace (self.comp, self.esc + 'S' + self.esc)
        s.replace (self.subcomp, self.esc + 'T' + self.esc)
        s.replace (self.rep, self.esc + 'R' + self.esc)
        s.replace ('\n', self.esc + '.br' + self.esc)
        return s

    def process (self, params):
        self.params = params
        self.fields = { # dictionary of fields, key is number, contents is string
            2:self.comp + self.rep + self.esc + self.subcomp,
            3:"GNUMed 0.0.1",
            7:self.datetime (DateTime.now ()),
            10:"123467", # this is our unique ID!!!
            11:"D", # D for debugging, P = production
            12:"2.3.1"} # HL7 version
        self.file = cStringIO.StringIO ("")
        self.seg_name = "MSH"
        self.template ()
        self.push_segment () # push out the last segment
        return self.file
        

    def segment (self, name):
        """
        Announces a formation of a new segment, prints the old one
        """
        self.push_segment ()
        self.fields = {}
        self.seg_name = name

    def push_segment (self):
        self.file.write (self.seg_name)
        self.file.write (self.fieldsep)
        start = 1
        if self.seg_name == "MSH":
            start = 2 # MSH is numbered differently as our first "field" is the separator
        list = []
        for i in range (start, self.maxfield[self.seg_name]):
            if self.fields.has_key (i):
                list.append (self.fields[i])
            else:
                list.append ('')
        self.file.write (string.join (list, self.fieldsep))
        self.file.write ('\n')
        

    def field (self, pos, value, rep = 0):
        """
        pos = position of field
        rep = set to true if this is a repeating field
        value = value as string (or list of strings, for repeating fields/components/subcomponents)
        Instead of a list, a dictionary with numeric keys can be used for discontinuous lists
        """
	if rep:
		r = self.rep
	else:
		r = self.comp
        self.fields[pos] = self.__emit_field (rep, value)

    def __emit_field (rep, value):
        if rep == self.rep:
            nextrep = self.comp
        if rep = self.comp:
            nextrep = self.subcomp
        if rep = self.subcomp:
            nextrep = None
        if rep is None:
            # we have a problem
            pass
        if type (value) is types.DictType:
            i = 0
            list = []
            while value:
                if value.has_key (i):
                    list.append (value[i])
                    del value[i]
                else:
                    list.append ('')
                i += 1
            value = list
        if type (value) is types.ListType:
            return string.join ([self.__emit_field (nextrep, i) for i in value], self.rep)
        else:
            return value
