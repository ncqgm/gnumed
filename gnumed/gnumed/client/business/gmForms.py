# -*- coding: latin-1 -*-
"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.23 2004-06-26 07:33:55 ncq Exp $
__version__ = "$Revision: 1.23 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types

# access our modules
#if __name__ == "__main__":
#		sys.path.append('../..')

from Gnumed.pycommon import gmLog, gmPG, gmWhoAmI, gmCfg, gmExceptions, gmMatchProvider
from Gnumed.pycommon.gmPyCompat import *
if __name__ == "__main__":
	from Gnumed.pycommon import gmI18N
from Gnumed.business import gmDemographicRecord, gmPatient

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

	def __init__ (self, pk_def=None, template=None, flags=[]):
		self.template = template
		self.flags = flags
		self.pk_def = pk_def
		self.patient = gmPatient.gmCurrentPatient ()
		self.whoami = gmWhoAmI.cWhoAmI ()
		self.machine = self.whoami.get_workplace ()

	def convert (self, item):
		"""
		Perform whatever character set conversions are reuired for this form
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
		A sop to TeX which can't act as a true filter to delete temporary files
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
		patient_clinical = self.patient.get_clinical_record ()
		encounter = patient_clinical.get_active_encounter()['pk_encounter']
		episode = patient_clinical.get_active_episode()['pk_episode']
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
		cmd = "insert into form_instances(fk_form_def, form_name, fk_episode, id_encounter) values (%s, %s, %s, %s)"
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
		self.basic_params = {}
		self.results = {}
		self.basic_params['sender'] = gmDemographicRecord.cDemographicRecord_SQL (self.whoami.get_staff_identity ())
		self.basic_params['patient'] = self.patient.get_demographic_record ()
		self.basic_params['clinical'] = self.patient.get_clinical_record ()

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
	def process (self, params, escape='@'):
		self.basic_params.update (params)
		regex = "%s(.+)%s" % (escape, escape)
		self.result = cStringIO.StringIO()
		self.params = self.basic_params
		_subst = self.__subst   # scope hack
		for line in self.template.split('\n'):
			self.idx = 0
			self.start_list = 0
			self.stop_list = 0
			self.result.write(re.sub (regex, lambda x: _subst (x.group (1)), line) + '\n')
			if self.start_list:
				while not self.stop_list:
					self.idx += 1
					self.result.write (re.sub (regex, lambda x: _subst (x.group (1)), line) + '\n')

		self.result.seek (0)
		return self.result
	#--------------------------------------------------------
        def __subst (self, match):
                """
                Perform a substitution on the string using a parameters dictionary,
                returns the subsitution
                """
		try:
			self.results[match] = eval (match, self.params)
		except NameError:
			_log.Log (gmLog.lErr, "name error on %s" % match)
			return ""
                if type(self.results[match]) is types.ListType:
                        self.start_list = 1 # we've got a list, keep repeating this line
                        if self.idx >= len (self.params[match]):
                                _log.Log (gmLog.lErr, "array field %s exhausted at index %d" % (match, self.idx))
                                return ""
                        elif len (self.results[match]) == self.idx+1: # stop when list exhausted, separate flag so other flags don't overwrite
                                self.stop_list = 1
                        return self.convert (self.results[match][self.idx])
                else:
                        return self.convert (self.results[match])
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
		command, set1 = gmCfg.getFirstMatchingDBSet (machine = self.machine, option = 'main.comms.print')
		self.exe (command)
#============================================================
class LaTeXForm (TextForm):
	"""A forms engine wrapping LaTeX.
	"""
	def convert (self, item  ):
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
				item = "\relax " # sometimes TeX really hates empty strings, this seems to mollify it
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
			item = string.join ([self.convert (i) in item], ' & ') + ' \\\\\n'
		elif item is None:
			item = '\\relax % Python None\n'
		elif type (item) is types.IntType or type (item) is types.FloatType:
			item = str (item)
		else:
			_log.Log (gmLog.lErr, "unknown type %s " % type (item))
			raise FormError ('unknown type [%s]' % type (item))
		return item

	def process (self, params):
		try:
			latex = TextForm.process (self, params)
			print latex.getvalue ()
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
		form = LaTeXForm (template=f.read())
		form.process (params)
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
# Revision 1.23  2004-06-26 07:33:55  ncq
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
