# -*- coding: latin-1 -*-
"""GNUmed forms classes
Business layer for printing all manners of forms, letters, scripts etc.
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.44 2007-07-22 08:59:19 ncq Exp $
__version__ = "$Revision: 1.44 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>, karsten.hilbert@gmx.net"


import os, sys, time, os.path
# string, re as regex, cStringIO, types


import uno, unohelper
from com.sun.star.util import XCloseListener as oooXCloseListener
from com.sun.star.connection import NoConnectException as oooNoConnectException
from com.sun.star.beans import PropertyValue as oooPropertyValue


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmTools, gmBorg, gmMatchProvider, gmExceptions, gmPG2
#gmCfg, gmShellAPI
from Gnumed.business import gmPerson


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


known_placeholders = [
	'lastname',
	'firstname',
	'title',
	'date_of_birth'
]

engine_ooo = 'O'

#============================================================
def get_form_templates(engine=None, all=False):
	"""OOo forms only for now"""
	# FIXME: support any engine/all forms
	engine = engine_ooo
	rows, idx = gmPG2.run_ro_queries (
		queries = [{
			'cmd': u"select pk, name_long, revision, in_use from ref.form_defs where in_use is True and engine = %(eng)s",
			'args': {'eng': engine}
		}]
	)
	return rows
#============================================================
def export_form_template(pk=None, filename=None):

	if filename is None:
		filename = gmTools.get_unique_filename (
			prefix = 'gmOOoFormTemplate-',
			suffix = '.ott',
			dir = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp'))
		)
	data_query = {
		'cmd': u'SELECT substring(template from %(start)s for %(size)s) FROM ref.form_defs WHERE pk = %(pk)s',
		'args': {'pk': pk}
	}
	data_size_query = {
		'cmd': u'select octet_length(template) from ref.form_defs where pk=%(pk)s',
		'args': {'pk': pk}
	}

	result = gmPG2.bytea2file (
		data_query = data_query,
		filename = filename,
		data_size_query = data_size_query,
		chunk_size = 0			# FIXME: load config from backend
	)
	if result is False:
		return None

	return filename
#============================================================
# Placeholder API, move elsewhere, eventually
#============================================================
class gmPlaceholderHandler(gmBorg.cBorg):

	def __init__(self, *args, **kwargs):

		self.debug = False
	#--------------------------------------------------------
	# __getitem__ API
	#--------------------------------------------------------
	def __getitem__(self, placeholder):
		"""Map self['placeholder'] to self.placeholder.

		This is useful for replacing placeholders parsed out
		of documents as strings.

		Unknown placeholders still deliver a result but it will be
		made glaringly obvious that the placeholder was unknown.
		"""
		if placeholder not in known_placeholders:
			if self.debug:
				return _('unknown placeholder: <%s>' % placeholder)
			else:
				return None

		return getattr(self, placeholder)
	#--------------------------------------------------------
	# properties actually handling placeholders
	#--------------------------------------------------------
	def _setter_noop(self, val):
		"""This does nothing, used as a NOOP properties setter."""
		pass
	#--------------------------------------------------------
	def _get_lastname(self):
		pat = gmPerson.gmCurrentPatient()
		return pat.get_active_name()['last']
	#--------------------------------------------------------
	def _get_firstname(self):
		pat = gmPerson.gmCurrentPatient()
		return pat.get_active_name()['first']
	#--------------------------------------------------------
	def _get_title(self):
		pat = gmPerson.gmCurrentPatient()
		return gmTools.coalesce(pat.get_active_name()['title'], u'')
	#--------------------------------------------------------
	def _get_dob(self):
		pat = gmPerson.gmCurrentPatient()
		return pat['dob'].strftime('%x')
	#--------------------------------------------------------
	lastname = property(_get_lastname, _setter_noop)
	firstname = property(_get_firstname, _setter_noop)
	title = property(_get_title, _setter_noop)
	date_of_birth = property(_get_dob, _setter_noop)

#============================================================
# OpenOffice API
#============================================================
class cOOoDocumentCloseListener(unohelper.Base, oooXCloseListener):

	def __init__(self):
		pat = gmPerson.gmCurrentPatient()
		pat.locked = True

	def queryClosing(self, evt, owner):
		# owner is True/False whether I am the owner of the doc
		print "OOo: queryClosing"

	def notifyClosing(self, evt):
		print "OOo: notifyClosing"

	def disposing(self, evt):
		print "OOo: disposing document"
		print "GNUmed: unlocking patient"
		pat = gmPerson.gmCurrentPatient()
		pat.locked = False
#------------------------------------------------------------
class cOOoConnector(gmBorg.cBorg):
	"""This class handles the connection to OOo.

	Its Singleton instance stays around once initialized.
	"""
	# FIXME: need to detect closure of OOo !
	def __init__(self):

		self.ooo_start_cmd = 'oowriter -accept="socket,host=localhost,port=2002;urp;"'
		self.resolver_uri = "com.sun.star.bridge.UnoUrlResolver"
		self.remote_context_uri = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
		self.desktop_uri = "com.sun.star.frame.Desktop"

		self.local_context = uno.getComponentContext()
		self.uri_resolver = self.local_context.ServiceManager.createInstanceWithContext(self.resolver_uri, self.local_context)

		self.__desktop = None
	#--------------------------------------------------------
	def open_document(self, filename=None):
		"""<filename> must be absolute"""
		document_uri = uno.systemPathToFileUrl(os.path.abspath(os.path.expanduser(filename)))
		doc = self.desktop.loadComponentFromURL(document_uri, "_blank", 0, ())
		return doc
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_desktop(self):
		if self.__desktop is None:
			try:
				self.remote_context = self.uri_resolver.resolve(self.remote_context_uri)
			except oooNoConnectException:
				_log.LogException('Cannot connect to OOo server. Trying to start one with: [%s]' % self.ooo_start_cmd)
				os.system(self.ooo_start_cmd)
				time.sleep(0.5)			# OOo sometimes needs a bit
				self.remote_context	= self.uri_resolver.resolve(self.remote_context_uri)
			self.__desktop = self.remote_context.ServiceManager.createInstanceWithContext(self.desktop_uri, self.remote_context)

		return self.__desktop

	def _set_desktop(self, desktop):
		pass

	desktop = property(_get_desktop, _set_desktop)
#------------------------------------------------------------
class cOOoLetter(object):

	def __init__(self, template_file=None):

		self.template_file = template_file
		self.ooo_doc = None

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def open_in_ooo(self):
		# export template from database
		# connect to OOo
		ooo_srv = cOOoConnector()
		# open doc in OOo
		self.ooo_doc = ooo_srv.open_document(filename=self.template_file)
		# listen for close events
		listener = cOOoDocumentCloseListener()
		self.ooo_doc.addCloseListener(listener)
	#--------------------------------------------------------
	def replace_placeholders(self):

		text_fields = self.ooo_doc.getTextFields().createEnumeration()
		handler = gmPlaceholderHandler()
		while text_fields.hasMoreElements():
			text_field = text_fields.nextElement()

			# placeholder ?
			if not text_field.supportsService('com.sun.star.text.TextField.JumpEdit'):
				continue
			# placeholder of type text ?
			if text_field.PlaceHolderType != 0:
				continue

			handler.debug = True
			print 'placeholder (type TEXT) <%s> -> %s (%s)' % (
				text_field.PlaceHolder,
				handler[text_field.PlaceHolder],
				text_field.Hint
			)
			handler.debug = False
			replacement = handler[text_field.PlaceHolder]
			if replacement is None:
				continue

			text_field.Anchor.setString(replacement)

	#--------------------------------------------------------
	def save_in_ooo(self, filename=None):
		if filename is not None:
			target_url = uno.systemPathToFileUrl(os.path.abspath(os.path.expanduser(filename)))
			save_args = (
				oooPropertyValue('Overwrite', 0, True, 0),
				oooPropertyValue('FormatFilter', 0, 'swriter: StarOffice XML (Writer)', 0)

			)
			# "store AS url" stores the doc, marks it unmodified and updates
			# the internal media descriptor - as opposed to "store TO url"
			self.ooo_doc.storeAsURL(target_url, save_args)
		else:
			self.ooo_doc.store()
	#--------------------------------------------------------
	def close_in_ooo(self):
		self.ooo_doc.dispose()
		pat = gmPerson.gmCurrentPatient()
		pat.locked = False
		self.ooo_doc = None
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------

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
		self.workplace = gmPerson.gmCurrentProvider().workplace

	def process (self):
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
		patient_clinical = self.patient.get_emr()
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


#class LaTeXFilter(Cheetah.Filters.Filter):
class LaTeXFilter:
	def filter (self, item, table_sep= " \\\\\n", **kwds):
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
			item = string.join ([self.filter (i, ' & ') for i in item], table_sep)
		elif item is None:
			item = '\\relax % Python None\n'
		elif type (item) is types.IntType or type (item) is types.FloatType:
			item = str (item)
		else:
			item = str (item)
			_log.Log (gmLog.lEWarn, "unknown type %s, string %s" % (type (item), item))
		return item 


#=====================================================
class LaTeXForm (gmFormEngine):
	"""A forms engine wrapping LaTeX.
	"""

	def __init__ (self, id, template):
		self.id = id
		self.template = template
		
	def process (self,params={}):
		try:
			latex = Cheetah.Template.Template (self.template, filter=LaTeXFilter, searchList=[params])
			# create a 'sandbox' directory for LaTeX to play in
			self.tmp = tempfile.mktemp ()
			os.makedirs (self.tmp)
			self.oldcwd = os.getcwd ()
			os.chdir (self.tmp)
			stdin = os.popen ("latex", "w", 2048)
			stdin.write (str (latex)) #send text. LaTeX spits it's output into stdout
			# FIXME: send LaTeX output to the logger
			stdin.close ()
			if not gmShellAPI.run_command_in_shell("dvips texput.dvi -o texput.ps", blocking=True):
				raise FormError ('DVIPS returned error')
		except EnvironmentError, e:
			_log.Log (gmLog.lErr, e.strerror)
			raise FormError (e.strerror)
		return file ("texput.ps")

	def xdvi (self):
		"""
		For testing purposes, runs Xdvi on the intermediate TeX output
		WARNING: don't try this on Windows
		"""
		gmShellAPI.run_command_in_shell("xdvi texput.dvi", blocking=True)

	def exe (self, command):
		if "%F" in command:
			command.replace ("%F", "texput.ps")
		else:
			command	 = "%s < texput.ps" % command
		try:
			if not gmShellAPI.run_command_in_shell(command, blocking=True):
				_log.Log (gmLog.lErr, "external command %s returned non-zero" % command)
				raise FormError ('external command %s returned error' % command)
		except EnvironmentError, e:
			_log.Log (gmLog.lErr, e.strerror)
			raise FormError (e.strerror)		     
		return True

	def printout (self):
		command, set1 = gmCfg.getDBParam (workplace = self.workplace, option = 'main.comms.print')
		self.exe (command)

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

class FormTypeMP (gmMatchProvider.cMatchProvider_SQL2):
	def __init__ (self):
		source = [{
			'column':'name',
			'table':'form_types',
			'service':'reference',
			'pk':'pk'}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

class FormMP (gmMatchProvider.cMatchProvider_SQL2):
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
		cmd = 'select template, engine, pk from form_defs where pk = %s'
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
		return LaTeXForm (result[0][2], result[0][0])
	elif result[0][1] == 'T':
		return TextForm (result[0][2], result[0][0])
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
		  'INCLUDEDISEASES':0, 'DISEASELIST':'',
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

	from Gnumed.pycommon import gmI18N, gmDateTime
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	gmDateTime.init()

	#--------------------------------------------------------
	def play_with_ooo():
		try:
			doc = open_uri_in_ooo(filename=sys.argv[1])
		except:
			_log.LogException('cannot open [%s] in OOo' % sys.argv[1])
			raise

		class myCloseListener(unohelper.Base, oooXCloseListener):
			def disposing(self, evt):
				print "disposing:"
			def notifyClosing(self, evt):
				print "notifyClosing:"
			def queryClosing(self, evt, owner):
				# owner is True/False whether I am the owner of the doc
				print "queryClosing:"

		l = myCloseListener()
		doc.addCloseListener(l)

		tfs = doc.getTextFields().createEnumeration()
		print tfs
		print dir(tfs)
		while tfs.hasMoreElements():
			tf = tfs.nextElement()
			if tf.supportsService('com.sun.star.text.TextField.JumpEdit'):
				print tf.getPropertyValue('PlaceHolder')
				print "  ", tf.getPropertyValue('Hint')

#		doc.close(True)		# closes but leaves open the dedicated OOo window
		doc.dispose()		# closes and disposes of the OOo window
	#--------------------------------------------------------
	def test_open_uri_in_ooo():
		try:
			open_uri_in_ooo(filename=sys.argv[1])
		except:
			_log.LogException('cannot open [%s] in OOo' % sys.argv[1])
			raise
	#--------------------------------------------------------
	def test_placeholders():
		handler = gmPlaceholderHandler()

		for placeholder in ['a', 'b', None]:
			print handler[placeholder]

		pat = gmPerson.ask_for_patient()
		if pat is None:
			return

		gmPerson.set_active_patient(patient = pat)

		for placeholder in known_placeholders:
			print placeholder, "=", handler[placeholder]
	#--------------------------------------------------------
	def test_cOOoLetter():
		pat = gmPerson.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		doc = cOOoLetter(template_file = sys.argv[1])
		doc.open_in_ooo()
		doc.replace_placeholders()
		doc.save_in_ooo('~/test_cOOoLetter.odt')
		raw_input('press <ENTER> to continue')
		doc.close_in_ooo()
	#--------------------------------------------------------


	# now run the tests
	#test_open_uri_in_ooo()
	#test_au()
	#test_de()
	#play_with_ooo()
	#test_placeholders()
	test_cOOoLetter()

#============================================================
# $Log: gmForms.py,v $
# Revision 1.44  2007-07-22 08:59:19  ncq
# - get_form_templates()
# - export_form_template()
# - absolutize -> os.path.abspath
#
# Revision 1.43  2007/07/13 21:00:55  ncq
# - apply uno.absolutize()
#
# Revision 1.42  2007/07/13 12:08:38  ncq
# - do not touch unknown placeholders unless debugging is on, user might
#   want to use them elsewise
# - use close listener
#
# Revision 1.41  2007/07/13 09:15:52  ncq
# - fix faulty imports
#
# Revision 1.40  2007/07/11 21:12:50  ncq
# - gmPlaceholderHandler()
# - OOo API with test suite
#
# Revision 1.39  2007/02/17 14:08:52  ncq
# - gmPerson.gmCurrentProvider.workplace now a property
#
# Revision 1.38  2006/12/23 15:23:11  ncq
# - use gmShellAPI
#
# Revision 1.37  2006/10/25 07:17:40  ncq
# - no more gmPG
# - no more cClinItem
#
# Revision 1.36  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.35  2006/05/12 12:03:01  ncq
# - whoami -> whereami
#
# Revision 1.34  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.33  2005/12/31 18:01:54  ncq
# - spelling of GNUmed
# - clean up imports
#
# Revision 1.32  2005/11/06 12:31:30  ihaywood
# I've discovered that most of what I'm trying to do with forms involves
# re-implementing Cheetah (www.cheetahtemplate.org), so switch to using this.
#
# If this new dependency annoys you, don't import the module: it's not yet
# used for any end-user functionality.
#
# Revision 1.31  2005/04/03 20:06:51  ncq
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
