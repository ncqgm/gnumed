# -*- coding: latin-1 -*-
"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.

This code is PROOF OF CONCEPT only
I give no warrant that it will work, or even compile
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.11 2004-04-10 01:48:31 ihaywood Exp $
__version__ = "$Revision: 1.11 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types
from Gnumed.business import gmDemographicRecord, gmPatient

# access our modules
if __name__ == "__main__":
	sys.path.append('../..')

# start logging
from Gnumed.pycommon import gmLog, gmPG, gmWhoAmI
_log = gmLog.gmDefLog
if __name__ == "__main__":
    _log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)


# we make these assumptions about the assignment of form IDs on the backend.
ID_STANDARD_REFERRAL=101
ID_STANDARD_REFERRAL_EMAIL=102
ID_STANDARD_SCRIPT = 201

#============================================================
class gmFormEngine:
    """Ancestor for forms.

    No real functionality as yet
    Descendants should override class variables country, type, electronic, date as neccessary
    """

    def __init__ (self, template, flags=[]):
        self.template = template
        self.flags = flags

    def process (self, params):
        """
        Accept a template [format specific to the engine] and
        dictionary of parameters [specific to the template] for processing into a form.
        Returns a Python file or file-like object representing the
        transmittable form of the form.
        For paper forms, this should be PostScript data or similar.
        """
        pass

    def cleanup (self):
        """
        A sop to TeX which can't act as a true filter to delete temporary files
        """
        pass

    def flags (self):
        """
        A list of flags (true/false options) available in this form instance
        """
        return self.flags

#============================================================
class TextForm (gmFormEngine):
    """
    Takes a plain text form and subsitutes the fields
    which are marked using an escape character.

    The fields are a dictionary of strings or string lists
    If lists, the lines containing these list fields are repeated until one
    of the lists is exhausted.
    """

    def __subst (self, match):
        if self.params.has_key (match): # we have a parameter matching the field
            if type (self.params[match]) is types.ListType:
                self.start_list = 1 # we've got a list, keep repeating this line
                if self.index >= len (self.params[match]):
                    _log.Log (gmLog.lErr, "array field %s exhausted at index %d" % (match, self.index))
                    return ""
                elif len (self.params[match]) == self.index+1: # stop when list exhausted, separate flag so other flags don't overwrite
                    self.stop_list = 1
                return self.params[match][self.index]
            else:
                return self.params[match]
        else:
            _log.Log (gmLog.lInfo, "can't find %s in form dictionary" % match)
            return ""
    
    def process (self, params, escape='@'):
        regex = "%s(\\w+)" % escape
        result = cStringIO.StringIO ()
        self.params = params
        for line in self.template.split ('\n'):
            self.index = 0
            self.start_list = 0
            self.stop_list = 0
            result.write (re.sub (regex, lambda x: self.__subst (x.group (1)), line) + '\n')
            if self.start_list:
                while not self.stop_list:
                    self.index += 1
                    result.write (re.sub (regex, lambda x: self.__subst (x.group (1)), line) + '\n')
        result.seek (0)
        return result

#============================================================
class LaTeXForm (TextForm):
    """A forms engine wrapping LaTeX.
    """
    def __texify (self, item):
        """
        Convience function to escape strings for TeX output
        """

        if type (item) is types.StringType or type (item) is types.UnicodeType:
            item = item.replace ("\\", "\\backspace") # I wonder about this, do we want users to be able to use raw TeX?
            item = item.replace ("&", "\\&")
            item = item.replace ("$", "\\$")
            item = item.replace ('"', "") # okay, that's not right, but easiest solution for now
            item = item.replace ("\n", "\\\\ ")
            if len (item.strip ()) == 0:
                item = "\relax " # sometimes TeX really hates empty strings, this seems to mollify it
		# FIXME: cover all of ISO-Latin-1 which can be expressed in TeX
	    if type (item) is types.UnicodeType:
	        item = item.encode ('latin-1', 'replace')
	    trans = {'ß':'\\ss{}', 'ä': '\\"{a}', 'Ä' :'\\"{A}', "ö ": '\\"{o}', "Ö": '\\"{O}',  "ü": '\\"{u}', "Ü": '\\"{U}',
		     '\x8a':'\\v{S}', '\x8a':'\\OE{}', '\x9a':'\\v{s}', '\x9c': '\\oe{}', '\a9f':'\\"{Y}', #Microsloth extensions
		     '\x86': '{\\dag}', '\x87': '{\\ddag}', '\xa7':'{\\S}', '\xb6': '{\\P}', '\xa9': '{\\copyright}', '\xbf': '?`',
		     '\xc0':'\\`{A}', '\xa1': "\\'{A}", '\xa2': '\\^{A}', '\xa3':'\\~{A}', '\\xc5': '{\AA}',
		     '\xa1': '!`',
		     '\xb5':'$\mu$', '\xa3': '\pounds{}'}
	    for k, i in trans.items ():
                item = item.replace (k, i)
        if type (item) is types.ListType: 
            item = [self.texify (i) for i in item]
        if type (item) is types.IntType:
            item = str(item)
        if type (item) is types.DictType:
            for i in item.keys ():
                item[i] = self.__texify (item[i])
        return item

    def process (self, params):
        params = self.__texify (params)
        latex = TextForm.process (self, params)
        # create a 'sandbox' directory for LaTeX to play in
        self.tmp = tempfile.mktemp ()
        os.makedirs (self.tmp)
        self.oldcwd = os.getcwd ()
        os.chdir (self.tmp)
        stdin = os.popen ("latex", "w", 2048)
        stdin.write (latex.getvalue ()) # send text. LaTeX spits it's output into stdout.
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

#============================================================
# convenience functions
#------------------------------------------------------------
def search_form (discipline = None, electronic=0):
    """
    Searches for available forms given the discipline and electronicity
    """

    cmd = "select name_short, name_long, version, id from form_types, lnk_form2discipline where id_form = id and discipline like %%s and %s electronic" % (electronic or 'not') and ''
    result = gmPG.run_ro_query ('reference', cmd, None, discipline)
    if result is None:
        return []
    else:
        return [{'name_short':r[0], 'name_long':r[1], 'version':r[2], 'id':r[3]} for r in result]
#------------------------------------------------------------
def get_form (id):
    """
    Instantiates a FormEngine based on the form ID from the backend
    """
    result = gmPG.run_ro_query ('reference', 'select template, engine, flags from form_defs where pk = %s', None, id)
    if result[0][1] == 'L':
        return LaTeXForm (result[0][0], result[0][2])
    elif result[1] == 'T':
        return TextForm (result[0][0], result[0][2])
    else:
        _log.Log (gmLog.lErr, 'no such form engine %s' % result[1])
        return None
#------------------------------------------------------------
def send_referral (recipient, channel, addr, text, flags):
	whoami = gmWhoAmI.cWhoAmI ().get_staff_identity ()
	sender = gmDemographicRecord.cDemographicRecord_SQL (whoami)
	patient = gmPatient.gmCurrentPatient ()
	patient_demo = patient.get_demographic_record ()
	params = {}
	params['SENDER'] = sender.getFullName ()
	params['PATIENTNAME'] = patient_demo.getFullName ()
	params['RECIPIENT'] = recipient.getFullName ()
	params['DOB'] = patient_demo.getDOB ().Format ('%x')
	params['PATIENTADDRESS'] = _("%(number)s %(street)s, %(urb)s %(postcode)s") % patient_demo.getAddresses ('home', 1)
	params['TEXT'] = text
	params['INCLUDEMEDS'] = flags['meds']
	# FUTURE
	# params['MEDLIST'] = patient_epr.getMedicationsList ()
	params['INCLUDEPASTHX'] = flags['pasthx']
	#F FUTURE
	# params['PASTHXLIST'] = patient_epr.getPastHistory ()
	
	if channel == 'post':
		params['RECIPIENTADDRESS'] = _('%(number)s %(street)s\n%(urb)s %(postcode)s') % addr
		sndr_addr = sender.getAddresses ('work', 1)
		if sndr_addr:
			params['SENDERADDRESS'] = _('%(number)s %(street)s\n%(urb)s %(postcode)s') % sender.getAddresses('work', 1)
		else:
			params['SENDERADDRESS'] = _('No address')
		form = get_form (ID_STANDARD_REFERRAL)
		form.process (params)
		form.xdvi ()
		form.cleanup ()
	if channel == 'fax':
		params['RECIPIENTADDRESS'] = _('FAX: %s') % addr
		sender_addr = sender.getAddresses('work', 1)
		if sender_addr:
			sender_addr['fax'] = sender.getCommChannel (gmDemographicRecord.FAX)
			params['SENDERADDRESS'] = _('%(number)s %(street)s\n%(urb)s %(postcode)s\nFAX: %(fax)s' % sender_addr)
		else:
			params['SENDERADDRESS'] = _('No address')
		form = get_form (ID_STANDARD_REFERRAL)
		form.process (params)
		form.xdvi ()
		form.cleanup ()
	if channel == 'email':
		params['RECIPIENTADDRESS'] = addr
		params['SENDERADDRESS'] = sender.getCommChannel (gmDemographicRecord.EMAIL)
		form = get_form (ID_STANDARD_REFERRAL_EMAIL)
		form.process (params)
		print form.read ()
		
#-------------------------------------------------------------
def test_au():
	f = open('../../test-area/ian/terry-form.tex')
	params = {
		'RECIPIENT': "Dr. R. Terry\n1 Main St\nNewcastle",
		'DOCTORSNAME': 'Ian Haywood',
		'DOCTORSADDRESS': '1 Smith St\nMelbourne',
		'PATIENTNAME':'Joe Bloggs',
		'PATIENTADDRESS':'18 Fred St\nMelbourne',
		'REQUEST':'ultrasound',
		'THERAPY':'on warfarin',
		'CLINICALNOTES':'heard new murmur',
		'COPYADDRESS':'Karsten Hilbert\nLeipzig, Germany',
		'ROUTINE':1,
		'URGENT':0,
		'FAX':1,
		'PHONE':1,
		'PENSIONER':1,
		'VETERAN':0,
		'PADS':0,
		'INSTRUCTIONS':'Take the blue pill, Neo\nThis is \xa9 copyright.'
	}
	form = LaTeXForm (f.read())
	form.process (params)
	form.xdvi ()
	form.cleanup ()

#------------------------------------------------------------
def test_de():
	template = open('../../test-area/ian/Formularkopf-DE.tex')
	form = LaTeXForm(template.read())
	params = {
		'PATIENT LASTNAME': 'Kirk',
		'PATIENT FIRSTNAME': 'James T.',
		'PATIENT STREET': 'Hauptstrasse',
		'PATIENT ZIP': '02999',
		'PATIENT TOWN': 'Gross Saerchen',
		'PATIENT DOB': '22.03.1931'
	}
	form.process(params)
	form.xdvi()
	form.cleanup()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	test_au()
	#test_de()

#============================================================
# $Log: gmForms.py,v $
# Revision 1.11  2004-04-10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.10  2004/03/12 15:23:36  ncq
# - cleanup, test_de
#
# Revision 1.9  2004/03/12 13:20:29  ncq
# - remove unneeded import
# - log keyword
#
