# -*- coding: latin-1 -*-
"""GNUmed forms classes

Business layer for printing all manners of forms, letters, scripts etc.
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.58 2008-04-29 18:27:44 ncq Exp $
__version__ = "$Revision: 1.58 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>, karsten.hilbert@gmx.net"


import os, sys, time, os.path, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools, gmBorg, gmMatchProvider, gmExceptions, gmPG2, gmDispatcher, gmBusinessDBObject, gmCfg
from Gnumed.business import gmPerson, gmSurgery


_log = logging.getLogger('gm.forms')
_log.info(__version__)

engine_ooo = 'O'
engine_names = {
	u'O': 'OpenOffice',
	u'L': 'LaTeX'
}

#============================================================
def get_form_templates(engine=None, active_only=False):
	"""Load form templates."""
	if active_only:
		query = u"select * from ref.v_paperwork_templates where engine = %(eng)s and in_use is True"
	else:
		query = u"select * from ref.v_paperwork_templates where engine = %(eng)s order by in_use desc"

	rows, idx = gmPG2.run_ro_queries (
		queries = [{'cmd': query, 'args': {'eng': engine, 'in_use': active_only}}],
		get_col_idx = True
	)
	templates = [ cFormTemplate(row = {'pk_field': 'pk_paperwork_template', 'data': r, 'idx': idx}) for r in rows ]

	return templates
#============================================================
# match providers
#============================================================
class cFormTemplateNameLong_MatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
			select name_long, name_long
			from ref.v_paperwork_templates
			where name_long %(fragment_condition)s
			order by name_long
		"""
		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = [query])
#============================================================
class cFormTemplateNameShort_MatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
			select name_short, name_short
			from ref.v_paperwork_templates
			where name_short %(fragment_condition)s
			order by name_short
		"""
		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = [query])
#============================================================
class cFormTemplateType_MatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
			select * from (
				select pk, _(name) as l10n_name from ref.form_types
				where _(name) %(fragment_condition)s

				union

				select pk, _(name) as l10n_name from ref.form_types
				where name %(fragment_condition)s
			) as union_result
			order by l10n_name
		"""
		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = [query])
#============================================================
class cFormTemplate(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u'select * from ref.v_paperwork_templates where pk_paperwork_template = %s'

	_cmds_store_payload = [
		u"""update ref.paperwork_templates set
				name_short = %(name_short)s,
				name_long = %(name_long)s,
				fk_template_type = %(pk_template_type)s,
				instance_type = %(instance_type)s,
				engine = %(engine)s,
				in_use = %(in_use)s,
				filename = %(filename)s,
				external_version = %(external_version)s
			where
				pk = %(pk_paperwork_template)s and
				xmin = %(xmin_paperwork_template)s
		""",
		u"""select xmin_paperwork_template from ref.v_paperwork_templates where pk_paperwork_template = %(pk_paperwork_template)s"""
	]

	_updatable_fields = [
		u'name_short',
		u'name_long',
		u'external_version',
		u'pk_template_type',
		u'instance_type',
		u'engine',
		u'in_use',
		u'filename'
	]

	_suffix4engine = {
		u'O': u'.ott',
		u'L': u'.tex',
		u'T': u'.txt'
	}

	#--------------------------------------------------------
	def export_to_file(self, filename=None, chunksize=0):
		"""Export form template from database into file."""

		if filename is None:
			if self._payload[self._idx['filename']] is None:
				suffix = self.__class__._suffix4engine[self._payload[self._idx['engine']]]
			else:
				suffix = os.path.splitext(self._payload[self._idx['filename']].strip())[1].strip()
				if suffix in [u'', u'.']:
					suffix = self.__class__._suffix4engine[self._payload[self._idx['engine']]]

			filename = gmTools.get_unique_filename (
				prefix = 'gm-%s-Template-' % self._payload[self._idx['engine']],
				suffix = suffix,
				dir = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp'))
			)

		data_query = {
			'cmd': u'SELECT substring(data from %(start)s for %(size)s) FROM ref.paperwork_templates WHERE pk = %(pk)s',
			'args': {'pk': self.pk_obj}
		}

		data_size_query = {
			'cmd': u'select octet_length(data) from ref.paperwork_templates where pk = %(pk)s',
			'args': {'pk': self.pk_obj}
		}

		result = gmPG2.bytea2file (
			data_query = data_query,
			filename = filename,
			data_size_query = data_size_query,
			chunk_size = chunksize
		)
		if result is False:
			return None

		return filename
	#--------------------------------------------------------
	def update_template_from_file(self, filename=None):
		gmPG2.file2bytea (
			filename = filename,
			query = u'update ref.paperwork_templates set data = %(data)s::bytea where pk = %(pk)s and xmin = %(xmin)s',
			args = {'pk': self.pk_obj, 'xmin': self._payload[self._idx['xmin_paperwork_template']]}
		)
		# adjust for xmin change
		self.refetch_payload()
#============================================================
def create_form_template(template_type=None, name_short=None, name_long=None):

	cmd = u'insert into ref.paperwork_templates (fk_template_type, name_short, name_long, external_version) values (%(type)s, %(nshort)s, %(nlong)s, %(ext_version)s)'
	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd, 'args': {'type': template_type, 'nshort': name_short, 'nlong': name_long, 'ext_version': 'new'}},
			{'cmd': u"select currval(pg_get_serial_sequence('ref.paperwork_templates', 'pk'))"}
		],
		return_data = True
	)
	template = cFormTemplate(aPK_obj = rows[0][0])
	return template
#------------------------------------------------------------
def delete_form_template(template=None):
	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': u'delete from ref.paperwork_templates where pk=%(pk)s', 'args': {'pk': template['pk_paperwork_template']}}
		]
	)
	return True
#============================================================
# OpenOffice API
#============================================================
uno = None
cOOoDocumentCloseListener = None

def init_ooo():
	"""FIXME: consider this:

	try:
	    import uno
	except:
	    print "This Script needs to be run with the python from OpenOffice.org"
	    print "Example: /opt/OpenOffice.org/program/python %s" % (
	        os.path.basename(sys.argv[0]))
	    print "Or you need to insert the right path at the top, where uno.py is."
	    print "Default: %s" % default_path
	"""
	global uno
	if uno is not None:
		return

	global unohelper, oooXCloseListener, oooNoConnectException, oooPropertyValue

	import uno, unohelper
	from com.sun.star.util import XCloseListener as oooXCloseListener
	from com.sun.star.connection import NoConnectException as oooNoConnectException
	from com.sun.star.beans import PropertyValue as oooPropertyValue

	#----------------------------------
	class _cOOoDocumentCloseListener(unohelper.Base, oooXCloseListener):
		"""Listens for events sent by OOo during the document closing
		   sequence and notifies the GNUmed client GUI so it can
		   import the closed document into the database.
		"""
		def __init__(self, document=None):
			self.document = document

		def queryClosing(self, evt, owner):
			# owner is True/False whether I am the owner of the doc
			pass

		def notifyClosing(self, evt):
			pass

		def disposing(self, evt):
			self.document.on_disposed_by_ooo()
			self.document = None
	#----------------------------------

	global cOOoDocumentCloseListener
	cOOoDocumentCloseListener = _cOOoDocumentCloseListener

	_log.debug('python UNO bridge successfully initialized')

#------------------------------------------------------------
class gmOOoConnector(gmBorg.cBorg):
	"""This class handles the connection to OOo.

	Its Singleton instance stays around once initialized.
	"""
	# FIXME: need to detect closure of OOo !
	def __init__(self):

		init_ooo()

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
		desktop = self.desktop

		if desktop is None:
			return None

		doc = desk.loadComponentFromURL(document_uri, "_blank", 0, ())
		return doc
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_desktop(self):
		opt_name = 'external.ooo.startup_settle_time'
		if self.__desktop is None:
			try:
				self.remote_context = self.uri_resolver.resolve(self.remote_context_uri)
			except oooNoConnectException:
				_log.exception('Cannot connect to OOo server.')
				_log.error('Trying to start OOo server with: [%s]' % self.ooo_start_cmd)
				os.system(self.ooo_start_cmd)
				dbcfg = gmCfg.cCfgSQL()
				ooo_wait_time = dbcfg.get2 (
					option = opt_name,
					workplace = gmSurgery.gmCurrentPractice().active_workplace,
					bias = 'workplace',
					default = 2.0
				)
				_log.debug('waiting %s seconds for OOo to start up' % ooo_wait_time)
				time.sleep(ooo_wait_time)	# OOo sometimes needs a bit
				try:
					self.remote_context	= self.uri_resolver.resolve(self.remote_context_uri)
				except oooNoConnectException:
					_log.exception('Cannot start (or connect to started) OOo server. You may need to increase <%s>.' % opt_name)
					return None

			self.__desktop = self.remote_context.ServiceManager.createInstanceWithContext(self.desktop_uri, self.remote_context)

		return self.__desktop

	def _set_desktop(self, desktop):
		pass

	desktop = property(_get_desktop, _set_desktop)
#------------------------------------------------------------
class cOOoLetter(object):

	def __init__(self, template_file=None, instance_type=None):

		self.template_file = template_file
		self.instance_type = instance_type
		self.ooo_doc = None

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def open_in_ooo(self):
		# connect to OOo
		ooo_srv = gmOOoConnector()
		# open doc in OOo
		self.ooo_doc = ooo_srv.open_document(filename=self.template_file)
		if self.ooo_doc is None:
			return False
		# listen for close events
		pat = gmPerson.gmCurrentPatient()
		pat.locked = True
		listener = cOOoDocumentCloseListener(document=self)
		self.ooo_doc.addCloseListener(listener)

		return True
	#--------------------------------------------------------
	def show(self, visible=True):
		self.ooo_doc.CurrentController.Frame.ContainerWindow.setVisible(visible)
	#--------------------------------------------------------
	def replace_placeholders(self, handler=None):

		text_fields = self.ooo_doc.getTextFields().createEnumeration()
		while text_fields.hasMoreElements():
			text_field = text_fields.nextElement()

			# placeholder ?
			if not text_field.supportsService('com.sun.star.text.TextField.JumpEdit'):
				continue
			# placeholder of type text ?
			if text_field.PlaceHolderType != 0:
				continue

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
	def on_disposed_by_ooo(self):
		# get current file name from OOo, user may have used Save As
		filename = uno.fileUrlToSystemPath(self.ooo_doc.URL)
		# tell UI to import the file
		gmDispatcher.send (
			signal = u'import_document_from_file',
			filename = filename,
			document_type = self.instance_type,
			unlock_patient = True
		)
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
		self.patient = gmPerson.gmCurrentPatient()
		self.workplace = gmSurgery.gmCurrentPractice().active_workplace

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
		cmd = "select name_short || ': <' || name_long || '::' || external_version || '>' from paperwork_templates where pk=%s";
		rows = gmPG.run_ro_query('reference', cmd, None, self.pk_def)
		form_name = None
		if rows is None:
			_log.error('error retrieving form def for [%s]' % self.pk_def)
		elif len(rows) == 0:
			_log.error('no form def for [%s]' % self.pk_def)
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
			_log.error('failed to store form [%s] (%s): %s' % (self.pk_def, form_name, err))
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
			_log.warning("unknown type %s, string %s" % (type (item), item))
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
			_log.error(e.strerror)
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
				_log.error("external command %s returned non-zero" % command)
				raise FormError ('external command %s returned error' % command)
		except EnvironmentError, e:
			_log.error(e.strerror)
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
def get_form(id):
	"""
	Instantiates a FormEngine based on the form ID or name from the backend
	"""
	try:
		# it's a number: match to form ID
		id = int (id)
		cmd = 'select template, engine, pk from paperwork_templates where pk = %s'
	except ValueError:
		# it's a string, match to the form's name
		# FIXME: can we somehow OR like this: where name_short=%s OR name_long=%s ?
		cmd = 'select template, engine, flags, pk from paperwork_templates where name_short = %s'
	result = gmPG.run_ro_query ('reference', cmd, None, id)
	if result is None:
		_log.error('error getting form [%s]' % id)
		raise gmExceptions.FormError ('error getting form [%s]' % id)
	if len(result) == 0:
		_log.error('no form [%s] found' % id)
		raise gmExceptions.FormError ('no such form found [%s]' % id)
	if result[0][1] == 'L':
		return LaTeXForm (result[0][2], result[0][0])
	elif result[0][1] == 'T':
		return TextForm (result[0][2], result[0][0])
	else:
		_log.error('no form engine [%s] for form [%s]' % (result[0][1], id))
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

	from Gnumed.pycommon import gmI18N, gmDateTime
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	gmDateTime.init()

	#--------------------------------------------------------
	def play_with_ooo():
		try:
			doc = open_uri_in_ooo(filename=sys.argv[1])
		except:
			_log.exception('cannot open [%s] in OOo' % sys.argv[1])
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
	def test_cOOoLetter():
		pat = gmPerson.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		doc = cOOoLetter(template_file = sys.argv[1])
		doc.open_in_ooo()
		doc.replace_placeholders()
		doc.save_in_ooo('~/test_cOOoLetter.odt')
		doc = None
#		doc.close_in_ooo()
		raw_input('press <ENTER> to continue')
	#--------------------------------------------------------
	def test_cFormTemplate():
		template = cFormTemplate(aPK_obj = sys.argv[2])
		print template
		print template.export_to_file()
	#--------------------------------------------------------
	def set_template_from_file():
		template = cFormTemplate(aPK_obj = sys.argv[2])
		template.update_template_from_file(filename = sys.argv[3])
	#--------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		# now run the tests
		#test_au()
		#test_de()
		#play_with_ooo()
		#test_cOOoLetter()
		test_cFormTemplate()
		#set_template_from_file()

#============================================================
# $Log: gmForms.py,v $
# Revision 1.58  2008-04-29 18:27:44  ncq
# - cOOoConnector -> gmOOoConnector
#
# Revision 1.57  2008/02/25 17:31:41  ncq
# - logging cleanup
#
# Revision 1.56  2008/01/30 13:34:50  ncq
# - switch to std lib logging
#
# Revision 1.55  2007/11/10 20:49:22  ncq
# - handle failing to connect to OOo much more gracefully
#
# Revision 1.54  2007/10/21 20:12:42  ncq
# - make OOo startup settle time configurable
#
# Revision 1.53  2007/10/07 12:27:08  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.52  2007/09/01 23:31:36  ncq
# - fix form template type phrasewheel query
# - settable of external_version
# - delete_form_template()
#
# Revision 1.51  2007/08/31 23:03:45  ncq
# - improved docs
#
# Revision 1.50  2007/08/31 14:29:52  ncq
# - optionalized UNO import
# - create_form_template()
#
# Revision 1.49  2007/08/29 14:32:25  ncq
# - remove data_modified property
# - adjust to external_version
#
# Revision 1.48  2007/08/20 14:19:48  ncq
# - engine_names
# - match providers
# - fix active_only logic in get_form_templates() and sort properly
# - adjust to renamed database fields
# - cleanup
#
# Revision 1.47  2007/08/15 09:18:07  ncq
# - cleanup
# - cOOoLetter.show()
#
# Revision 1.46  2007/08/13 22:04:32  ncq
# - factor out placeholder handler
# - use view in get_form_templates()
# - add cFormTemplate() and test
# - move export_form_template() to cFormTemplate.export_to_file()
#
# Revision 1.45  2007/08/11 23:44:01  ncq
# - improve document close listener, get_form_templates(), cOOoLetter()
# - better test suite
#
# Revision 1.44  2007/07/22 08:59:19  ncq
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
