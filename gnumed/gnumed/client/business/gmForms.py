# -*- coding: latin-1 -*-
"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.31 2005-04-03 20:06:51 ncq Exp $
__version__ = "$Revision: 1.31 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types

try:
	from Gnumed.pycommon import gmLog, gmPG, gmWhoAmI, gmCfg, gmExceptions, gmMatchProvider
	from Gnumed.pycommon.gmPyCompat import *
	if __name__ == "__main__":
		from Gnumed.pycommon import gmI18N
	from Gnumed.business import gmDemographicRecord, gmPerson
except:
	_ = lambda x: x

# start logging
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
class gmFormEngine:
	"""Ancestor for forms.

	No real functionality as yet
	Descendants should override class variables country, type, electronic,
	date as neccessary
	"""

	def __init__ (self, pk_def=None, template=None):
		self.template = template
		self.patient = gmPerson.gmCurrentPatient ()
		self.whoami = gmWhoAmI.cWhoAmI ()
		self.workplace = self.whoami.get_workplace ()

	def convert (self, item):
		"""
		Perform whatever character set conversions are required for this form
		"""
		return item

	def process (self, params, escape='@'):
		"""Merge values into the form template.

		Accept a template [format specific to the engine] and
		dictionary of parameters [specific to the template] for processing into a form.
		Returns a Python file or file-like object representing the
		transmittable form of the form.
		For paper forms, this should be PostScript data or similar.
		"""
		pass

	def cleanup (self):
		"""
		A sop to TeX which can't act as a true filter: to delete temporary files
		"""
		pass

	def exe (self, command):
		"""
		Executes the provided command.
		If command cotains %F. it is substituted with the filename
		Otherwise, the file is fed in on stdin
		"""
		pass


	def flags (self):
		"""
		A list of flags (true/false options) available in this form instance
		"""
		return self.flags
	#--------------------------------------------------------
	def store(self, params=None):
		"""Stores the parameters in the backend.

		- link_obj can be a cursor, a connection or a service name
		- assigning a cursor to link_obj allows the calling code to
		  group the call to store() into an enclosing transaction
		  (for an example see gmReferral.send_referral()...)
		"""
		# some forms may not have values ...
		if params is None:
			params = {}
		patient_clinical = self.patient.get_clinical_record()
		encounter = patient_clinical.get_active_encounter()['pk_encounter']
		# FIXME: get_active_episode is no more
		#episode = patient_clinical.get_active_episode()['pk_episode']
		# generate "forever unique" name
		cmd = "select name_short || ': <' || name_long || '::' || revision || '>' from form_defs where pk=%s";
		rows = gmPG.run_ro_query('reference', cmd, None, self.pk_def)
		form_name = None
		if rows is None:
			_log.Log(gmLog.lErr, 'error retrieving form def for [%s]' % self.pk_def)
		elif len(rows) == 0:
			_log.Log(gmLog.lErr, 'no form def for [%s]' % self.pk_def)
		else:
			form_name = rows[0][0]
		# we didn't get a name but want to store the form anyhow
		if form_name is None:
			form_name=time.time()	# hopefully unique enough
		# in one transaction
		queries = []
		# - store form instance in form_instance
		cmd = "insert into form_instances(fk_form_def, form_name, fk_episode, fk_encounter) values (%s, %s, %s, %s)"
		queries.append((cmd, [self.pk_def, form_name, episode, encounter]))
		# - store params in form_data
		for key in params.keys():
			cmd = """
				insert into form_data(fk_instance, place_holder, value)
				values ((select currval('form_instances_pk_seq')), %s, %s::text)
			"""
			queries.append((cmd, [key, params[key]]))
		# - get inserted PK
		queries.append(("select currval ('form_instances_pk_seq')", []))
		status, err = gmPG.run_commit('historica', queries, True)
		if status is None:
			_log.Log(gmLog.lErr, 'failed to store form [%s] (%s): %s' % (self.pk_def, form_name, err))
			return None
		return status
#============================================================
class TextForm (gmFormEngine):
	"""
	Takes a plain text form and subsitutes the fields
	which are marked using an escape character.

	The fields are a dictionary of strings, string lists, or functions that return these
	Lists of lists ae allowed, and will be printed as tab-separated tables 
	If lists, the lines containing these fields are repeated until one
	of the lists is exhausted.
	"""


	def __init__ (self, *args):
		gmFormEngine.__init__ (self, *args)

	def convert (self, item, table_sep='\n'):
		"""
		Convert lists and tuples to tab-separated lines
		"""
		if type (item) is types.ListType or type (item) is types.TupleType:
			return string.join ([self.convert (i, '\t') for i in item], table_sep)
		elif type (item) is types.IntType or type (item) is types.FloatType:
			return str (item)
		else:
			return item
		
	#--------------------------------------------------------
	def process (self, params):
		self.params = params
		regex = "\$([A-Za-z_]+)"
		self.result = cStringIO.StringIO()
		_subst = self.__subst   # scope hack
		self.result.write(re.sub (regex, lambda x: _subst (x.group (1)), self.template) + '\n')
		self.result.seek (0)
		return self.result
	#--------------------------------------------------------
        def __subst (self, match, list_level=0):
                """
                Perform a substitution on the string using a parameters dictionary,
                returns the subsitution
                """
		if self.params.has_key (match):
			r = self.params[match]
		else:
			r = getattr (self, match, "")
		if callable (r):
			self.params[match] = r ()
			r = self.params[match]
		return self.convert (r)
        #--------------------------------------------------------

	#--------------------------------------------------------
	def exe (self, command):
		if "%F" in command:
			tmp = tempfile.mktemp ()
			f = file (tmp, "w")
			f.write (self.result.read ())
			f.close ()
			command.replace ("%F", tmp)
			os.system (command)
			os.unlink (tmp)
		else:
			stdin = os.popen (command, "w", 2048)
			stdin.write (self.result.read ())
			stdin.close ()
	#----------------------------------------------------------
	
	def printout (self):
		command, set1 = gmCfg.getDBParam (workplace = self.workplace, option = 'main.comms.print')
		self.exe (command)
#============================================================
class LaTeXForm (TextForm):
	"""A forms engine wrapping LaTeX.
	"""
	def convert (self, item, table_sep=" \\\\\n"  ):
		"""
		Convience function to escape ISO-Latin-1 strings for TeX output
		WARNING: not all ISO-Latin-1 characters are expressible in TeX
		FIXME: nevertheless, there are a few more we could support

		Also intelligently convert lists and tuples into TeX-style table lines
		"""
		if type (item) is types.UnicodeType or type (item) is types.StringType:
			item = item.replace ("\\", "\\backslash") # I wonder about this, do we want users to be able to use raw TeX?
			item = item.replace ("&", "\\&")
			item = item.replace ("$", "\\$")
			item = item.replace ('"', "") # okay, that's not right, but easiest solution for now
			item = item.replace ("\n", "\\\\ ")
			if len (item.strip ()) == 0:
				item = "\\relax " # sometimes TeX really hates empty strings, this seems to mollify it
			# FIXME: cover all of ISO-Latin-1 which can be expressed in TeX
			if type (item) is types.UnicodeType:
				item = item.encode ('latin-1', 'replace')
				trans = {'ß':'\\ss{}', 'ä': '\\"{a}', 'Ä' :'\\"{A}', 'ö': '\\"{o}', 'Ö': '\\"{O}',	'ü': '\\"{u}', 'Ü': '\\"{U}',
					 '\x8a':'\\v{S}', '\x8a':'\\OE{}', '\x9a':'\\v{s}', '\x9c': '\\oe{}', '\a9f':'\\"{Y}', #Microsloth extensions
					 '\x86': '{\\dag}', '\x87': '{\\ddag}', '\xa7':'{\\S}', '\xb6': '{\\P}', '\xa9': '{\\copyright}', '\xbf': '?`',
					 '\xc0':'\\`{A}', '\xa1': "\\'{A}", '\xa2': '\\^{A}', '\xa3':'\\~{A}', '\\xc5': '{\AA}',
					 '\xc7':'\\c{C}', '\xc8':'\\`{E}',	
					 '\xa1': '!`',
				 '\xb5':'$\mu$', '\xa3': '\pounds{}', '\xa2':'cent'}
				for k, i in trans.items ():
					item = item.replace (k, i)
		elif type (item) is types.ListType or type (item) is types.TupleType:
			item = string.join ([self.convert (i, ' & ') for i in item], table_sep)
		elif item is None:
			item = '\\relax % Python None\n'
		elif type (item) is types.IntType or type (item) is types.FloatType:
			item = str (item)
		else:
			item = str (item)
			_log.Log (gmLog.lEWarn, "unknown type %s, string %s" % (type (item), item))
		return item

	def process (self, params):
		try:
			latex = TextForm.process (self, params)
			# create a 'sandbox' directory for LaTeX to play in
			self.tmp = tempfile.mktemp ()
			os.makedirs (self.tmp)
			self.oldcwd = os.getcwd ()
			os.chdir (self.tmp)
			stdin = os.popen ("latex", "w", 2048)
			stdin.write (latex.getvalue ()) # send text. LaTeX spits it's output into stdout.
			# FIXME: send LaTeX output to the logger
			stdin.close ()
			dvips = os.system ("dvips texput.dvi -o texput.ps")
			if dvips != 0:
				raise FormError ('DVIPS returned error [%d]' % dvips)
		except EnvironmentError, e:
			_log.Log (gmLog.lErr, e.strerror)
			raise FormError (e.strerror)
		return file ("texput.ps")

	def xdvi (self):
		"""
		For testing purposes, runs Xdvi on the intermediate TeX output
		WARNING: don't try this on Windows
		"""
		os.system ("xdvi texput.dvi")
		
	def exe (self, command):
		if "%F" in command:
			command.replace ("%F", "texput.ps")
		else:
			command	 = "%s < texput.ps" % command
		try:
			ret = os.system (command)
			if ret != 0:
				_log.Log (gmLog.lErr, "external command %s returned non-zero" % command)
				raise FormError ('external command %s returned %s' % (command, ret))
		except EnvironmentError, e:
			_log.Log (gmLog.lErr, e.strerror)
			raise FormError (e.strerror)		     
		return True

	def cleanup (self):
		"""
		Delete all the LaTeX output iles
		"""
		for i in os.listdir ('.'):
			os.unlink (i)
		os.chdir (self.oldcwd)
		os.rmdir (self.tmp)

#===========================================================
class HL7Form (gmFormEngine):
	pass

#============================================================
# convenience functions
#------------------------------------------------------------

class FormTypeMP (gmMatchProvider.cMatchProvider_SQL):
	def __init__ (self):
		source = [{
			'column':'name',
			'table':'form_types',
			'service':'reference',
			'pk':'pk'}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

class FormMP (gmMatchProvider.cMatchProvider_SQL):
	def __init__ (self):
		source = [{
			'column':'name_long',
			'table':'form_defs',
			'service':'reference',
			'extra conditions':{'type':'fk_type = %s or fk_type is null'},
			'pk':'pk'}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)
	
#------------------------------------------------------------
def get_form(id):
	"""
	Instantiates a FormEngine based on the form ID or name from the backend
	"""
	try:
		# it's a number: match to form ID
		id = int (id)
		cmd = 'select template, engine, flags, pk from form_defs where pk = %s'
	except ValueError:
		# it's a string, match to the form's name
		# FIXME: can we somehow OR like this: where name_short=%s OR name_long=%s ?
		cmd = 'select template, engine, flags, pk from form_defs where name_short = %s'
	result = gmPG.run_ro_query ('reference', cmd, None, id)
	if result is None:
		_log.Log (gmLog.lErr, 'error getting form [%s]' % id)
		raise gmExceptions.FormError ('error getting form [%s]' % id)
	if len(result) == 0:
		_log.Log (gmLog.lErr, 'no form [%s] found' % id)
		raise gmExceptions.FormError ('no such form found [%s]' % id)
	if result[0][1] == 'L':
		return LaTeXForm (result[0][3], result[0][0], result[0][2])
	elif result[0][1] == 'T':
		return TextForm (result[0][3], result[0][0], result[0][2])
	else:
		_log.Log (gmLog.lErr, 'no form engine [%s] for form [%s]' % (result[0][1], id))
		raise FormError ('no engine [%s] for form [%s]' % (result[0][1], id))
		
#-------------------------------------------------------------
class FormError (Exception):
	def __init__ (self, value):
		self.value = value

	def __str__ (self):
		return repr (self.value)
#-------------------------------------------------------------

test_letter = """
\\documentclass{letter}
\\address{ $DOCTOR \\\\
$DOCTORADDRESS}
\\signature{$DOCTOR}

\\begin{document}
\\begin{letter}{$RECIPIENTNAME \\\\
$RECIPIENTADDRESS}

\\opening{Dear $RECIPIENTNAME}

\\textbf{Re:} $PATIENTNAME, DOB: $DOB, $PATIENTADDRESS \\\\

$TEXT

\\ifnum$INCLUDEMEDS>0
\\textbf{Medications List}

\\begin{tabular}{lll}
$MEDSLIST
\\end{tabular}
\\fi

\\ifnum$INCLUDEDISEASES>0
\\textbf{Disease List}

\\begin{tabular}{l}
$DISEASELIST
\\end{tabular}
\\fi

\\closing{$CLOSING}

\\end{letter}
\\end{document}
"""


def test_au():
	f = open('../../test-area/ian/terry-form.tex')
	params = {
	'RECIPIENT': "Dr. R. Terry\n1 Main St\nNewcastle",
	'DOCTORSNAME': 'Ian Haywood',
	'DOCTORSADDRESS': '1 Smith St\nMelbourne',
	'PATIENTNAME':'Joe Bloggs',
	'PATIENTADDRESS':'18 Fred St\nMelbourne',
	'REQUEST':'echocardiogram',
	'THERAPY':'on warfarin',
	'CLINICALNOTES':"""heard new murmur
	Here's some
crap to demonstrate how it can cover multiple lines.""",
	'COPYADDRESS':'Karsten Hilbert\nLeipzig, Germany',
	'ROUTINE':1,
	'URGENT':0,
	'FAX':1,
	'PHONE':1,
	'PENSIONER':1,
	'VETERAN':0,
	'PADS':0,
	'INSTRUCTIONS':u'Take the blue pill, Neo'
	}
	form = LaTeXForm (1, f.read())
	form.process (params)
	form.xdvi ()
	form.cleanup ()
	
def test_au2 ():
	form = LaTeXForm (2, test_letter)
	params = {'RECIPIENTNAME':'Dr. Richard Terry',
		  'RECIPIENTADDRESS':'1 Main St\nNewcastle',
		  'DOCTOR':'Dr. Ian Haywood',
		  'DOCTORADDRESS':'1 Smith St\nMelbourne',
		  'PATIENTNAME':'Joe Bloggs',
		  'PATIENTADDRESS':'18 Fred St, Melbourne',
		  'TEXT':"""This is the main text of the referral letter""",
		  'DOB':'12/3/65',
		  'INCLUDEMEDS':1,
		  'MEDSLIST':[["Amoxycillin", "500mg", "TDS"], ["Perindopril", "4mg", "OD"]],
		  'INCLUDEDISEASES':0,
		  'CLOSING':'Yours sincerely,'
		  }
	form.process (params)
	print os.getcwd ()
	form.xdvi ()
	form.cleanup ()
	
#------------------------------------------------------------
def test_de():
		template = open('../../test-area/ian/Formularkopf-DE.tex')
		form = LaTeXForm(template=template.read())
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
	_log.SetAllLogLevels(gmLog.lData)
	test_au()
	#test_de()

#============================================================
# $Log: gmForms.py,v $
# Revision 1.31  2005-04-03 20:06:51  ncq
# - comment on emr.get_active_episode being no more
#
# Revision 1.30  2005/03/06 08:17:02  ihaywood
# forms: back to the old way, with support for LaTeX tables
#
# business objects now support generic linked tables, demographics
# uses them to the same functionality as before (loading, no saving)
# They may have no use outside of demographics, but saves much code already.
#
# Revision 1.29  2005/02/03 20:17:18  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.28  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.27  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.26  2004/08/20 13:19:06  ncq
# - use getDBParam()
#
# Revision 1.25  2004/07/19 11:50:42  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.24  2004/06/28 12:18:52  ncq
# - more id_* -> fk_*
#
# Revision 1.23  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.22  2004/06/18 13:32:37  ncq
# - just some whitespace cleanup
#
# Revision 1.21  2004/06/17 11:36:13  ihaywood
# Changes to the forms layer.
# Now forms can have arbitrary Python expressions embedded in @..@ markup.
# A proper forms HOWTO will appear in the wiki soon
#
# Revision 1.20  2004/06/08 00:56:39  ncq
# - even if we don't need parameters we need to pass an
#   empty param list to gmPG.run_commit()
#
# Revision 1.19  2004/06/05 12:41:39  ihaywood
# some more comments for gmForms.py
# minor change to gmReferral.py: print last so bugs don't waste toner ;-)
#
# Revision 1.18  2004/05/28 13:13:15  ncq
# - move currval() inside transaction in gmForm.store()
#
# Revision 1.17  2004/05/27 13:40:21  ihaywood
# more work on referrals, still not there yet
#
# Revision 1.16  2004/04/21 22:26:48  ncq
# - it is form_data.place_holder, not placeholder
#
# Revision 1.15  2004/04/21 22:05:28  ncq
# - better error reporting
#
# Revision 1.14  2004/04/21 22:01:15  ncq
# - generic store() for storing instance in form_data/form_instances
#
# Revision 1.13	 2004/04/18 08:39:57  ihaywood
# new config options
#
# Revision 1.12	 2004/04/11 10:15:56  ncq
# - load title in get_names() and use it superceding getFullName
#
# Revision 1.11	 2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.10	 2004/03/12 15:23:36  ncq
# - cleanup, test_de
#
# Revision 1.9	2004/03/12 13:20:29	 ncq
# - remove unneeded import
# - log keyword
#
