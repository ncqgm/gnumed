"""
Module to run a LaTeX session
"""

import re, types, string, tempfile, os, os.path

def texify (item):
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

class LaTeX:
    def __init__ (self, file, params = {}):
        """
        file is the filename of the LaTeX file.
        params is a dictionary of parameters for latex forms
        parameters can be strings, lists of lists (which are mapped to latex tables) and booleans
        """
        self.latex = file
        self.params = params
        # create a 'playground' directory
        self.tmp = tempfile.mktemp ()
        os.makedirs (self.tmp)

    def run (self):
        self.oldcwd = os.getcwd ()
        self.stub, ext = os.path.splitext (os.path.basename (self.latex))
        os.chdir (self.tmp) # move to the playground
        stdin, stdout = popen4 ("latex %s" % self.latex, "w", 2048)
        for line in stdout.xreadlines ():
            # script requests a field value
            m = re.match ("^:F(.*)=$", line)
            if m:
                if self.params.has_key (m.group(1)):
                    stdin.write (texify (self.params[m.group (1)]) + "\n")
                else:
                    stdin.write ("\\relax\n")
            # script requests a flag
            m = re.match ("^:C(.*)=$", line)
            if m:
                if self.params.has_key (m.group(1)) and self.params[m.group(1)]:
                    stdin.write ("1\n")
                else:
                    stdin.write ("0\n")
            if re.match ("^!.*", line): # we have an error
                stdin.write ("X\n") # causes LaTeX to quit gracefully
        stdin.close ()
        stdout.close ()

    def printout (self, printer=None, job=None):
        """
        Printing on UNIX via lpr
        printer: printer passed to lpr
        job: the lpr jobname (fax modems use this to hold the fax number)
        """
        # call dvips to do the printing
        if printer:
            if job:
                os.system ("dvips %s.dvi -o ! lpr -P%s -J%s" % (self.stub, printer, job))
            else:
                os.system ("dvips %s.dvi -o ! lpr -P%s" % (self.stub, printer))
        else:
            os.system ("dvips %s.dvi" % self.stub)

    def print_win (self, printer=None):
        """
        Printing on Windows. Not tested
        """
        # call dvips to make PostScript
        os.system ("dvips %s.dvi -o %s.ps" % (self.stub, self.stub))
        # call GSPRINT.EXE to do the printing (http://www.cs.wisc.edu/~ghost/gsview/gsprint.htm)
        if printer:
            os.system ("gsprint %s.ps" % self.stub)
        else:
            os.system ("gsprint %s.ps -printer %s" % (self.stub, printer))

    def xdvi (self):
        # for debugging only
        os.system ('xdvi %s.dvi' % self.stub)

    def finish (self):
        for i in os.listdir ('.'):
            os.unlink (i)
        os.chdir (self.oldcwd)
        os.rmdir (self.tmp)


if __name__ == '__main__':
    letter = {'to_address':"""
    Ian Haywood
    2/76 Smith St
    North Melbourne 3076""",
              'from_address':"""
    Ricard Terry
    175 Jones Rd
    Bluebridge 2675""",
              'patient_name':"Joe Bloggs",
              'patient_address':'12 Main Rd, North Melbourne',
              'patient_DOB':'1/1/70',
              'patient_gender':'M',
              'meds_list':[
        ['Frusemide', '80mg', 'nocte'],
        ['Atenolol', '5mg', 'mane']
        ],
              'disease_list':[
        ['Congestive cardiac failure'],
        ['Ischaemic heart disease']
        ]
              'main_text':"""
              Thankyou for seeing this patient. No reason in particular
              """
              'salutation':'Dear Richard,',
              'closing':'Yours sincerely,'}
              
