# -*- coding: latin-1 -*-
"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.20 2004-06-08 00:56:39 ncq Exp $
__version__ = "$Revision: 1.20 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types

# access our modules
#if __name__ == "__main__":
#		sys.path.append('../..')

from Gnumed.pycommon import gmLog, gmPG, gmWhoAmI, gmCfg, gmExceptions
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
	Descendants should override class variables country, type, electronic, date as neccessary
	"""

	def __init__ (self, pk_def=None, template=None, flags=[]):
		self.template = template
		self.flags = flags
		self.pk_def = pk_def

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
	def store(self, episode, encounter, params=None, link_obj='historica'):
		"""Stores the parameters in the backend.

		- link_obj can be a cursor, a connection or a service name
		- assigning a cursor to link_obj allows the calling code to
		  group the call to store() into an enclosing transaction
		  (for an example see gmReferral.send_referral()...)
		"""
		# some forms may not have values ...
		if params is None:
			params = {}
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
		cmd = "insert into form_instances(fk_form_def, form_name, id_episode, id_encounter) values (%s, %s, %s, %s)"
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
		status, err = gmPG.run_commit(link_obj, queries, True)
		if status is None:
			_log.Log(gmLog.lErr, 'failed to store form [%s] (%s): %s' % (self.pk_def, form_name, err))
			return None
		return status
#============================================================
class TextForm (gmFormEngine):
	"""
	Takes a plain text form and subsitutes the fields
	which are marked using an escape character.

	The fields are a dictionary of strings or string lists
	If lists, the lines containing these fields are repeated until one
	of the lists is exhausted.
	"""
	def __subst (self, match):
		"""
		Perform a substitution on the string using a parameters dictionary,
		returns the subsitution
		"""
		try:
			is_list = (type(self.params[match]) is types.ListType)
		except KeyError:
			_log.Log (gmLog.lInfo, "can't find value for placeholder [%s] in data dictionary" % match)
			return ""

		if is_list:
			self.start_list = 1 # we've got a list, keep repeating this line
			if self.idx >= len (self.params[match]):
				_log.Log (gmLog.lErr, "array field %s exhausted at index %d" % (match, self.idx))
				return ""
			elif len (self.params[match]) == self.idx+1: # stop when list exhausted, separate flag so other flags don't overwrite
				self.stop_list = 1
			return self.params[match][self.idx]
		else:
			return self.params[match]
	#--------------------------------------------------------
	def process (self, params, escape='@'):
		# FIXME: rewrite for @placeholder@ style
		regex = "%s(\\w+)" % escape
		self.result = cStringIO.StringIO ()
		self.params = params
		_subst = self.__subst	# scope hack
		for line in self.template.split ('\n'):
			self.idx = 0
			self.start_list = 0
			self.stop_list = 0
			self.result.write (re.sub (regex, lambda x: _subst (x.group (1)), line) + '\n')
			if self.start_list:
				while not self.stop_list:
					self.idx += 1
					self.result.write (re.sub (regex, lambda x: _subst (x.group (1)), line) + '\n')
		self.result.seek (0)
		return self.result
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

#============================================================
class LaTeXForm (TextForm):
	"""A forms engine wrapping LaTeX.
	"""
	def __texify (self, item):
		"""
		Convience function to escape ISO-Latin-1 strings for TeX output
		WARNING: not all ISO-Latin-1 characters are expressible in TeX
		FIXME: nevertheless, there are a few more we could support
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
			trans = {'ß':'\\ss{}', 'ä': '\\"{a}', 'Ä' :'\\"{A}', 'ö': '\\"{o}', 'Ö': '\\"{O}',	'ü': '\\"{u}', 'Ü': '\\"{U}',
					 '\x8a':'\\v{S}', '\x8a':'\\OE{}', '\x9a':'\\v{s}', '\x9c': '\\oe{}', '\a9f':'\\"{Y}', #Microsloth extensions
					 '\x86': '{\\dag}', '\x87': '{\\ddag}', '\xa7':'{\\S}', '\xb6': '{\\P}', '\xa9': '{\\copyright}', '\xbf': '?`',
					 '\xc0':'\\`{A}', '\xa1': "\\'{A}", '\xa2': '\\^{A}', '\xa3':'\\~{A}', '\\xc5': '{\AA}',
					 '\xc7':'\\c{C}', '\xc8':'\\`{E}',	
					 '\xa1': '!`',
					 '\xb5':'$\mu$', '\xa3': '\pounds{}', '\xa2':'cent'}
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
		try:
			params = self.__texify (params)
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
			if os.system ("dvips texput.dvi -o texput.ps") != 0:
				raise gmExceptions.InvalidInputError ('DVIPS returned error') 
		except EnvironmentError, e:
			_log.Log (gmLog.lErr, '' % e.strerror)
			raise gmExceptions.InvalidInputError ('Form printing failed because [%s]' % e.strerror)
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
		if os.system (command) != 0:
			_log.Log (gmLog.lErr, "external command %s returned non-zero" % command)
			return False
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
def search_form (discipline = None, electronic=0):
	"""
	Searches for available forms given the discipline and electronicity
	(i.e whether the output is  for printing or direct electronic transmission by whatever secure protocol)
	"""

	cmd = "select name_short, name_long, version, id from form_types, lnk_form2discipline where id_form = id and discipline like %%s and %s electronic" % (electronic or 'not') and ''
	result = gmPG.run_ro_query ('reference', cmd, None, discipline)
	if result is None:
		return []
	else:
		return [{'name_short':r[0], 'name_long':r[1], 'version':r[2], 'id':r[3]} for r in result]
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
		cmd = 'select template, engine, flags, pk from form_defs where name_short = %s'
	result = gmPG.run_ro_query ('reference', cmd, None, id)
	if result is None:
		_log.Log (gmLog.lErr, 'error getting form [%s]' % id)
		raise gmExceptions.InvalidInputError ('Error getting form [%s]' % id)
	if len(result) == 0:
		_log.Log (gmLog.lErr, 'no form [%s] found' % id)
		raise gmExceptions.InvalidInputError ('No such form found [%s]' % id)
	if result[0][1] == 'L':
		return LaTeXForm (result[0][3], result[0][0], result[0][2])
	elif result[0][1] == 'T':
		return TextForm (result[0][3], result[0][0], result[0][2])
	else:
		_log.Log (gmLog.lErr, 'no form engine [%s] for form [%s]' % (result[0][1], id))
		raise gmExceptions.InvalidInputError ('no engine [%s] for form [%s]' % (result[0][1], id))
		
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
# Revision 1.20  2004-06-08 00:56:39  ncq
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
