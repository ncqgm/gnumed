"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.

This code is PROOF OF CONCEPT only
I give no warrant that it will work, or even compile
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.3 2004-02-25 09:46:20 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ ="Ian Haywood <ihaywood@gnu.org"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types

# access our modules
if __name__ == "__main__":
    sys.path.append(os.path.join('..', 'pycommon'))
 
# start logging
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
    _log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)
 
from mx import DateTime
#============================================================

class gmForm:
    """
    Ancestor for forms
    No real functionality as yet
    Descendants should override class variables country, type, electronic, date as neccessary
    """

    country = "UF"
    discipline = ""
    electronic = 0
    date = DateTime.Date (1970, 1, 1)

    def process (self, params):
        """
        Accept a list of parameters for processing into a form.
        Returns a Python file (or file-like) object representing the
        transmitable form of the form.
        For paper forms, this should be PostScript data or similar.
        """
        pass

    def flags (self):
        """
        Return a list of strings representing specific checkbox options to display to the user.
        Can be added a fields to params above, holding a boolean
        """
        return []

    def cleanup (self):
        """
        A sop to LaTeX which can't function as a true filter.
        Deletes temporary files
        """
        pass
    
class LaTeXForm (gmForm):
    """
    A forms ancestor for forms using LaTeX
    Decendants override class variables discipline, country and date as necessary.
    Class variable template holds the LaTeX template document as a python string
    The document may embed calls to methods as @foo where foo (self) is defined in the descendant
    class, the string returned by the function is replaced in the text
    """

    def texify (self, item):
        """
        Convience function to escape strings for TeX output
        """

        if type (item) is types.StringType:
            item = item.replace ("\\", "\\backspace")
            item = item.replace ("&", "\\&")
            item = item.replace ("$", "\\$")
            item = item.replace ('"', "")
            item = item.replace ("\n", "\\\\ ")
        if len (item).strip () == 0:
	    item = "\relax"
        if type (item) is types.ListType:
            # convert to LaTeX table format 
            str = ''
            for line in item:
                line = [texify (i) for i in line]
                linestr = string.join (line, " & ")
                str += linestr
            str += ' \\\\ '
            item = str
        if type (item) is types.NoneType:
            item = "\\relax"
        return item
	    
    def __subst (self, match):
        if self.__dict__.has_key (match): # we have a method matching the field
            return self.__dict__ [match] () # call it and return the result
        elif self.params.has_key (match): # we have a parameter matching the field
            return self.texify (self.params[match]) # escape and return the value
        else:
            return "\relax % Can't get a value for %s\n" % match
    
    def process (self, params):
        self.params = params
        # perform substition with results of method calls
        self.latex = re.sub ("@(\w+)", lambda x: self.__subst (x.group (1)), self.template)
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
