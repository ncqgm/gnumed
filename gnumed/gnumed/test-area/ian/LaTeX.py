"""
Module to run a LaTeX session, using the a4form.cls to receive forms data
Stil under active development, watch out!
"""

import re, types, string, tempfile, os, os.path

def texify (item):
    """
    escape a string/list properly according to TeX markup
    """
    if type (item) is types.StringType:
        item = item.replace ("\\", "\\backspace ")
        item = item.replace ("&", "\\&")
        item = item.replace ("$", "\\$")
        item = item.replace ("%", "\\%")
        item = item.replace ('"', "")
        item = item.replace ("\n", "\\\\ ")
        item = item.replace ("\\\\ \\\\ ", "\n\n") # this a cheat to protect double newlines
        item = item.replace ("{", "\\{")
        item = item.replace ("}", "\\}")
        if len (item.strip ()) == 0:
            item = "\\relax"
    if type (item) is types.ListType:
        # convert list of lists to LaTeX table format 
        str = ''
        if len (item) == 0:
            item = '\\relax'
        else:
            for line in item:
                line = [texify (i) for i in line]
                linestr = string.join (line, " & ")
                str += linestr
                str += ' \\\\ '
            item = str
    # LaTeX doesn't cope with null strings. \relax is the the TeX
    # no-op instruction
    if type (item) is types.NoneType:
        item = "\\relax"
    return item

class LaTeX:
    def __init__ (self, file, params = {}):
        """
        file is the filename or python file object of the LaTeX file.
        params is a dictionary of parameters for latex forms
        parameters can be strings, lists of lists (which are mapped to latex tables) and booleans
        """
        self.latex = file
        self.params = params
        # create a 'playground' directory for LaTeX
        self.tmp = tempfile.mktemp ()

    def run (self):
        os.makedirs (self.tmp)
        self.oldcwd = os.getcwd ()
        os.chdir (self.tmp) # move to the playground
        self.old_umask = os.umask (066) # set umask so other users cannot read our files
        if type (self.latex) == types.StringType:
            self.latex = file (self.latex) # open file if necessary
        # run latex as a co-process
        stdin = os.popen ("latex", "w", 2048)
        # push the parameters to the interpreter as TeX commands
        for param in self.params.keys ():
            stdin.write ("\\def\\%s{%s}\n" % (param, texify (self.params[param])))
        # send the template
        stdin.write (self.latex.read ())
        stdin.write ('\n\\end\n')
        stdin.close ()

    def print_unix (self, printer=None, job=None):
        """
        Printing on UNIX via lpr
        printer: printer passed to lpr
        job: the lpr jobname (fax modems use this to hold the fax number)
        """
        # call dvips to do the printing
        if printer:
            if job:
                os.system ("dvips texput.dvi -o !\"lpr -P%s -J%s\"" % (printer, job))
            else:
                os.system ("dvips texput.dvi -o !\"lpr -P%s\"" % printer)
        else:
            os.system ("dvips texput.dvi -o !lpr")

    def print_win (self, printer=None):
        """
        Printing on Windows. Not tested
        """
        # call dvips to make PostScript file
        os.system ("dvips texput.dvi -o texput.ps")
        # call GSPRINT.EXE to do the printing (http://www.cs.wisc.edu/~ghost/gsview/gsprint.htm)
        if printer:
            os.system ("gsprint texput.ps")
        else:
            os.system ("gsprint texput.ps -printer %s" % printer)

    def xdvi (self):
        # for debugging only, previews the document
        os.system ('xdvi texput.dvi')

    def finish (self):
        # delete all files
        for i in os.listdir ('.'):
            os.unlink (i)
        os.chdir (self.oldcwd)
        # delete directory
        os.rmdir (self.tmp)
        # restore umask
        os.umask (self.old_umask)


# test form variables
#<DEBUG>

letter = {'recipient':"""Ian Haywood
2/76 Smith St
North Melbourne 3076""",
          'senderaddress':"""175 Jones Rd
Bluebridge 2675""",
          'sender':'Richard Terry',
          'patientname':"Joe Bloggs",
          'patientaddress':'12 Main Rd, North Melbourne',
          'patientDOB':'1/1/70',
          'patientgender':'M',
          'medslist':[
    ['Frusemide', '80mg', 'nocte'],
    ['Atenolol', '5mg', 'mane']
    ],
          'diseaselist':[
    ['Congestive cardiac failure'],
    ['Ischaemic heart disease']
    ],
          'maintext':"""Thankyou for seeing this patient. No reason in particular

This is a second paragraph.""",
          'salutation':'Dear Ian,',
          'finish':'Yours sincerely,'}

form = {'recipient':"""Ian Haywood
2/76 Smith St
North Melbourne 3076""",
        'senderaddress':"""175 Jones Rd
Bluebridge 2675""",
        'sender':'Richard Terry',
        'patientname':"Joe Bloggs",
        'patientaddress':'12 Main Rd, North Melbourne',
        'patientDOB':'1/1/70',
        'patientgender':'M',
        'request':'Cerebro-vascular',
        'clinicalnotes':'Some meaning clinical notes here.',
        'urgent':1,
        'veteran':1,
        'fax':1,
        'phone':1,
        'veteran':1,
        'pads':1,
        'pensioner':1,
        'routine':1,
        'therapy':'',
        'copyaddress':'',
        'instructions':'Nothing to eat or drink six hours prior.'
        }

script = {'doctorname':'Ian Haywood',
          'prescribernumber':'2197115',
          'providernumber':'2465641J',
          'drugs':[['Frusemide', '80mg', 'BD'],
                   ['Atenolol', '20mg', 'OD']
                   ],
          'patientname':'Joe Bloggs',
          'patientaddress':"""20 Smith St
          North Melbourne 3052""",
          'medicarenumber':'11111111',
          'brandsubstitution':1
          }

def test ():
    l = LaTeX ('/home/ian/gnumed/gnumed/test-area/ian/script.tex', script)
    l.run ()
    l.xdvi ()
    l.finish ()
    l = LaTeX ('/home/ian/gnumed/gnumed/test-area/ian/letter.tex', letter)
    l.run ()
    l.xdvi ()
    l.finish ()
    l = LaTeX ('/home/ian/gnumed/gnumed/test-area/ian/terry-form.tex', form)
    l.run ()
    l.xdvi ()
    l.print_unix (printer = "rlp", job = "1234557")
    l.finish ()

#</DEBUG>
