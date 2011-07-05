# -*- coding: latin-1 -*-
"""GNUmed forms classes

Business layer for printing all manners of forms, letters, scripts etc.
 
license: GPL v2 or later
"""
#============================================================
__version__ = "$Revision: 1.79 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>, karsten.hilbert@gmx.net"


import os, sys, time, os.path, logging
import codecs
import re as regex
import shutil
import random, platform, subprocess
import socket										# needed for OOo on Windows
#, libxml2, libxslt
import shlex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2

from Gnumed.business import gmPerson
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmSurgery


_log = logging.getLogger('gm.forms')
_log.info(__version__)

#============================================================
# this order is also used in choice boxes for the engine
form_engine_abbrevs = [u'O', u'L', u'I', u'G', u'P']

form_engine_names = {
	u'O': 'OpenOffice',
	u'L': 'LaTeX',
	u'I': 'Image editor',
	u'G': 'Gnuplot script',
	u'P': 'PDF forms'
}

form_engine_template_wildcards = {
	u'O': u'*.o?t',
	u'L': u'*.tex',
	u'G': u'*.gpl',
	u'P': u'*.pdf'
}

# is filled in further below after each engine is defined
form_engines = {}

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
		u'T': u'.txt',
		u'X': u'.xslt',
		u'I': u'.img',
		u'P': u'.pdf'
	}

	#--------------------------------------------------------
	def _get_template_data(self):
		"""The template itself better not be arbitrarily large unless you can handle that.

		Note that the data type returned will be a buffer."""

		cmd = u'SELECT data FROM ref.paperwork_templates WHERE pk = %(pk)s'
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}], get_col_idx = False)

		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError('cannot retrieve data for template pk = %s' % self.pk_obj)

		return rows[0][0]

	template_data = property(_get_template_data, lambda x:x)
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
				suffix = suffix
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
	#--------------------------------------------------------
	def instantiate(self):
		fname = self.export_to_file()
		engine = form_engines[self._payload[self._idx['engine']]]
		return engine(template_file = fname)
#============================================================
def get_form_template(name_long=None, external_version=None):
	cmd = u'select pk from ref.paperwork_templates where name_long = %(lname)s and external_version = %(ver)s'
	args = {'lname': name_long, 'ver': external_version}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	if len(rows) == 0:
		_log.error('cannot load form template [%s - %s]', name_long, external_version)
		return None

	return cFormTemplate(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def get_form_templates(engine=None, active_only=False, template_types=None, excluded_types=None):
	"""Load form templates."""

	args = {'eng': engine, 'in_use': active_only}
	where_parts = [u'1 = 1']

	if engine is not None:
		where_parts.append(u'engine = %(eng)s')

	if active_only:
		where_parts.append(u'in_use IS true')

	if template_types is not None:
		args['incl_types'] = tuple(template_types)
		where_parts.append(u'template_type IN %(incl_types)s')

	if excluded_types is not None:
		args['excl_types'] = tuple(excluded_types)
		where_parts.append(u'template_type NOT IN %(excl_types)s')

	cmd = u"SELECT * FROM ref.v_paperwork_templates WHERE %s ORDER BY in_use desc, name_long" % u'\nAND '.join(where_parts)

	rows, idx = gmPG2.run_ro_queries (
		queries = [{'cmd': cmd, 'args': args}],
		get_col_idx = True
	)
	templates = [ cFormTemplate(row = {'pk_field': 'pk_paperwork_template', 'data': r, 'idx': idx}) for r in rows ]

	return templates
#------------------------------------------------------------
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
# OpenOffice/LibreOffice API
#============================================================
uno = None
cOOoDocumentCloseListener = None
writer_binary = None

#-----------------------------------------------------------
def __configure_path_to_UNO():

	try:
		which = subprocess.Popen (
			args = ('which', 'soffice'),
			stdout = subprocess.PIPE,
			stdin = subprocess.PIPE,
			stderr = subprocess.PIPE,
			universal_newlines = True
		)
	except (OSError, ValueError, subprocess.CalledProcessError):
		_log.exception('there was a problem executing [which soffice]')
		return

	soffice_path, err = which.communicate()
	soffice_path = soffice_path.strip('\n')
	uno_path = os.path.abspath ( os.path.join (
		os.path.dirname(os.path.realpath(soffice_path)),
		'..',
		'basis-link',
		'program'
	))

	_log.info('UNO should be at [%s], appending to sys.path', uno_path)

	sys.path.append(uno_path)
#-----------------------------------------------------------
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

	try:
		import uno
	except ImportError:
		__configure_path_to_UNO()
		import uno

	global unohelper, oooXCloseListener, oooNoConnectException, oooPropertyValue

	import unohelper
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

	# search for writer binary
	global writer_binary
	found, binary = gmShellAPI.find_first_binary(binaries = [
		'lowriter',
		'oowriter'
	])
	if found:
		_log.debug('OOo/LO writer binary found: %s', binary)
		writer_binary = binary
	else:
		_log.debug('OOo/LO writer binary NOT found')
		raise ImportError('LibreOffice/OpenOffice (lowriter/oowriter) not found')

	_log.debug('python UNO bridge successfully initialized')

#------------------------------------------------------------
class gmOOoConnector(gmBorg.cBorg):
	"""This class handles the connection to OOo.

	Its Singleton instance stays around once initialized.
	"""
	# FIXME: need to detect closure of OOo !
	def __init__(self):

		init_ooo()

		#self.ooo_start_cmd = 'oowriter -invisible -accept="socket,host=localhost,port=2002;urp;"'
		#self.remote_context_uri = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"

		pipe_name = "uno-gm2lo-%s" % str(random.random())[2:]
		_log.debug('pipe name: %s', pipe_name)

		#self.ooo_start_cmd = 'oowriter -invisible -norestore -accept="pipe,name=%s;urp"' % pipe_name
		self.ooo_start_cmd = '%s -invisible -norestore -accept="pipe,name=%s;urp"' % (
			writer_binary,
			pipe_name
		)
		_log.debug('startup command: %s', self.ooo_start_cmd)

		self.remote_context_uri = "uno:pipe,name=%s;urp;StarOffice.ComponentContext" % pipe_name
		_log.debug('remote context URI: %s', self.remote_context_uri)

		self.resolver_uri = "com.sun.star.bridge.UnoUrlResolver"
		self.desktop_uri = "com.sun.star.frame.Desktop"

		self.local_context = uno.getComponentContext()
		self.uri_resolver = self.local_context.ServiceManager.createInstanceWithContext(self.resolver_uri, self.local_context)

		self.__desktop = None
	#--------------------------------------------------------
	def cleanup(self, force=True):
		if self.__desktop is None:
			_log.debug('no desktop, no cleanup')
			return

		try:
			self.__desktop.terminate()
		except:
			_log.exception('cannot terminate OOo desktop')
	#--------------------------------------------------------
	def open_document(self, filename=None):
		"""<filename> must be absolute"""

		if self.desktop is None:
			_log.error('cannot access OOo desktop')
			return None

		filename = os.path.expanduser(filename)
		filename = os.path.abspath(filename)
		document_uri = uno.systemPathToFileUrl(filename)

		_log.debug('%s -> %s', filename, document_uri)

		doc = self.desktop.loadComponentFromURL(document_uri, "_blank", 0, ())
		return doc
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __get_startup_settle_time(self):
		# later factor this out !
		dbcfg = gmCfg.cCfgSQL()
		self.ooo_startup_settle_time = dbcfg.get2 (
			option = u'external.ooo.startup_settle_time',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'workplace',
			default = 3.0
		)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_desktop(self):
		if self.__desktop is not None:
			return self.__desktop

		try:
			self.remote_context = self.uri_resolver.resolve(self.remote_context_uri)
		except oooNoConnectException:
			_log.exception('cannot connect to OOo server')
			_log.info('trying to start OOo server')
			os.system(self.ooo_start_cmd)
			self.__get_startup_settle_time()
			_log.debug('waiting %s seconds for OOo to start up', self.ooo_startup_settle_time)
			time.sleep(self.ooo_startup_settle_time)	# OOo sometimes needs a bit
			try:
				self.remote_context	= self.uri_resolver.resolve(self.remote_context_uri)
			except oooNoConnectException:
				_log.exception('cannot start (or connect to started) OOo server')
				return None

		self.__desktop = self.remote_context.ServiceManager.createInstanceWithContext(self.desktop_uri, self.remote_context)
		_log.debug('connection seems established')
		return self.__desktop

	desktop = property(_get_desktop, lambda x:x)
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
		self.ooo_doc = ooo_srv.open_document(filename = self.template_file)
		if self.ooo_doc is None:
			_log.error('cannot open document in OOo')
			return False

		# listen for close events
		pat = gmPerson.gmCurrentPatient()
		pat.locked = True
		listener = cOOoDocumentCloseListener(document = self)
		self.ooo_doc.addCloseListener(listener)

		return True
	#--------------------------------------------------------
	def show(self, visible=True):
		self.ooo_doc.CurrentController.Frame.ContainerWindow.setVisible(visible)
	#--------------------------------------------------------
	def replace_placeholders(self, handler=None, old_style_too = True):

		# new style embedded, implicit placeholders
		searcher = self.ooo_doc.createSearchDescriptor()
		searcher.SearchCaseSensitive = False
		searcher.SearchRegularExpression = True
		searcher.SearchWords = True
		searcher.SearchString = handler.placeholder_regex

		placeholder_instance = self.ooo_doc.findFirst(searcher)
		while placeholder_instance is not None:
			try:
				val = handler[placeholder_instance.String]
			except:
				_log.exception(val)
				val = _('error with placeholder [%s]') % placeholder_instance.String

			if val is None:
				val = _('error with placeholder [%s]') % placeholder_instance.String

			placeholder_instance.String = val
			placeholder_instance = self.ooo_doc.findNext(placeholder_instance.End, searcher)

		if not old_style_too:
			return

		# old style "explicit" placeholders
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
class cFormEngine(object):
	"""Ancestor for forms."""

	def __init__(self, template_file=None):
		self.template_filename = template_file
	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):
		"""Parse the template into an instance and replace placeholders with values."""
		raise NotImplementedError
	#--------------------------------------------------------
	def edit(self):
		"""Allow editing the instance of the template."""
		raise NotImplementedError
	#--------------------------------------------------------
	def generate_output(self, format=None):
		"""Generate output suitable for further processing outside this class, e.g. printing."""
		raise NotImplementedError
	#--------------------------------------------------------
	def process(self, data_source=None):
		"""Merge values into the form template.
		"""
		pass
	#--------------------------------------------------------
	def cleanup(self):
		"""
		A sop to TeX which can't act as a true filter: to delete temporary files
		"""
		pass
	#--------------------------------------------------------
	def exe(self, command):
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
		encounter = patient_clinical.active_encounter['pk_encounter']
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

#================================================================
# OOo template forms
#----------------------------------------------------------------
class cOOoForm(cFormEngine):
	"""A forms engine wrapping OOo."""

	def __init__(self, template_file=None):
		super(self.__class__, self).__init__(template_file = template_file)


		path, ext = os.path.splitext(self.template_filename)
		if ext in [r'', r'.']:
			ext = r'.odt'
		self.instance_filename = r'%s-instance%s' % (path, ext)

#================================================================
# LaTeX template forms
#----------------------------------------------------------------
class cLaTeXForm(cFormEngine):
	"""A forms engine wrapping LaTeX."""

	def __init__(self, template_file=None):
		super(self.__class__, self).__init__(template_file = template_file)
		path, ext = os.path.splitext(self.template_filename)
		if ext in [r'', r'.']:
			ext = r'.tex'
		self.instance_filename = r'%s-instance%s' % (path, ext)
	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):

		template_file = codecs.open(self.template_filename, 'rU', 'utf8')
		instance_file = codecs.open(self.instance_filename, 'wb', 'utf8')

		for line in template_file:

			if line.strip() in [u'', u'\r', u'\n', u'\r\n']:
				instance_file.write(line)
				continue

			# 1) find placeholders in this line
			placeholders_in_line = regex.findall(data_source.placeholder_regex, line, regex.IGNORECASE)
			# 2) and replace them
			for placeholder in placeholders_in_line:
				#line = line.replace(placeholder, self._texify_string(data_source[placeholder]))
				try:
					val = data_source[placeholder]
				except:
					_log.exception(val)
					val = _('error with placeholder [%s]') % placeholder

				if val is None:
					val = _('error with placeholder [%s]') % placeholder

				line = line.replace(placeholder, val)

			instance_file.write(line)

		instance_file.close()
		template_file.close()

		return
	#--------------------------------------------------------
	def edit(self):

		mimetypes = [
			u'application/x-latex',
			u'application/x-tex',
			u'text/plain'
		]

		for mimetype in mimetypes:
			editor_cmd = gmMimeLib.get_editor_cmd(mimetype, self.instance_filename)
			if editor_cmd is not None:
				break

		if editor_cmd is None:
			editor_cmd = u'sensible-editor %s' % self.instance_filename

		result = gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = True)
		self.re_editable_filenames = [self.instance_filename]

		return result
	#--------------------------------------------------------
	def generate_output(self, instance_file = None, format=None):

		if instance_file is None:
			instance_file = self.instance_filename

		try:
			open(instance_file, 'r').close()
		except:
			_log.exception('cannot access form instance file [%s]', instance_file)
			gmLog2.log_stack_trace()
			return None

		self.instance_filename = instance_file

		_log.debug('ignoring <format> directive [%s], generating PDF', format)

		# create sandbox for LaTeX to play in
		sandbox_dir = os.path.splitext(self.template_filename)[0]
		_log.debug('LaTeX sandbox directory: [%s]', sandbox_dir)

		old_cwd = os.getcwd()
		_log.debug('CWD: [%s]', old_cwd)

		gmTools.mkdir(sandbox_dir)

		os.chdir(sandbox_dir)
		try:
			sandboxed_instance_filename = os.path.join(sandbox_dir, os.path.split(self.instance_filename)[1])
			shutil.move(self.instance_filename, sandboxed_instance_filename)

			# LaTeX can need up to three runs to get cross references et al right
			if platform.system() == 'Windows':
				draft_cmd = r'pdflatex.exe -draftmode -interaction nonstopmode %s' % sandboxed_instance_filename
				final_cmd = r'pdflatex.exe -interaction nonstopmode %s' % sandboxed_instance_filename
			else:
				draft_cmd = r'pdflatex -draftmode -interaction nonstopmode %s' % sandboxed_instance_filename
				final_cmd = r'pdflatex -interaction nonstopmode %s' % sandboxed_instance_filename
			for run_cmd in [draft_cmd, draft_cmd, final_cmd]:
				if not gmShellAPI.run_command_in_shell(command = run_cmd, blocking = True, acceptable_return_codes = [0, 1]):
					_log.error('problem running pdflatex, cannot generate form output')
					gmDispatcher.send(signal = 'statustext', msg = _('Error running pdflatex. Cannot turn LaTeX template into PDF.'), beep = True)
					os.chdir(old_cwd)
					return None
		finally:
			os.chdir(old_cwd)

		sandboxed_pdf_name = u'%s.pdf' % os.path.splitext(sandboxed_instance_filename)[0]
		target_dir = os.path.split(self.instance_filename)[0]
		try:
			shutil.move(sandboxed_pdf_name, target_dir)
		except IOError:
			_log.exception('cannot move sandboxed PDF: %s -> %s', sandboxed_pdf_name, target_dir)
			gmDispatcher.send(signal = 'statustext', msg = _('Sandboxed PDF output file cannot be moved.'), beep = True)
			return None

		final_pdf_name = u'%s.pdf' % os.path.splitext(self.instance_filename)[0]

		try:
			open(final_pdf_name, 'r').close()
		except IOError:
			_log.exception('cannot open target PDF: %s', final_pdf_name)
			gmDispatcher.send(signal = 'statustext', msg = _('PDF output file cannot be opened.'), beep = True)
			return None

		self.final_output_filenames = [final_pdf_name]

		return final_pdf_name
#------------------------------------------------------------
form_engines[u'L'] = cLaTeXForm
#============================================================
# Gnuplot template forms
#------------------------------------------------------------
class cGnuplotForm(cFormEngine):
	"""A forms engine wrapping Gnuplot."""

	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):
		"""Parse the template into an instance and replace placeholders with values."""
		pass
	#--------------------------------------------------------
	def edit(self):
		"""Allow editing the instance of the template."""
		self.re_editable_filenames = []
		return True
	#--------------------------------------------------------
	def generate_output(self, format=None):
		"""Generate output suitable for further processing outside this class, e.g. printing.

		Expects .data_filename to be set.
		"""
		self.conf_filename = gmTools.get_unique_filename(prefix = 'gm2gpl-', suffix = '.conf')
		fname_file = codecs.open(self.conf_filename, 'wb', 'utf8')
		fname_file.write('# setting the gnuplot data file\n')
		fname_file.write("gm2gpl_datafile = '%s'\n" % self.data_filename)
		fname_file.close()

		# FIXME: cater for configurable path
		if platform.system() == 'Windows':
			exec_name = 'gnuplot.exe'
		else:
			exec_name = 'gnuplot'

		args = [exec_name, '-p', self.conf_filename, self.template_filename]
		_log.debug('plotting args: %s' % str(args))

		try:
			gp = subprocess.Popen (
				args = args,
				close_fds = True
			)
		except (OSError, ValueError, subprocess.CalledProcessError):
			_log.exception('there was a problem executing gnuplot')
			gmDispatcher.send(signal = u'statustext', msg = _('Error running gnuplot. Cannot plot data.'), beep = True)
			return

		gp.communicate()

		self.final_output_filenames = [
			self.conf_filename,
			self.data_filename,
			self.template_filename
		]

		return
#------------------------------------------------------------
form_engines[u'G'] = cGnuplotForm

#============================================================
# fPDF form engine
#------------------------------------------------------------
class cPDFForm(cFormEngine):
	"""A forms engine wrapping PDF forms.

	Johann Felix Soden <johfel@gmx.de> helped with this.

	http://partners.adobe.com/public/developer/en/pdf/PDFReference16.pdf

	http://wwwimages.adobe.com/www.adobe.com/content/dam/Adobe/en/devnet/acrobat/pdfs/fdf_data_exchange.pdf
	"""

	def __init__(self, template_file=None):

		super(cPDFForm, self).__init__(template_file = template_file)

		# detect pdftk
		found, self.pdftk_binary = gmShellAPI.detect_external_binary(binary = r'pdftk')
		if not found:
			raise ImportError('<pdftk(.exe)> not found')
			return		# should be superfluous, actually

		enc = sys.getfilesystemencoding()
		self.pdftk_binary = self.pdftk_binary.encode(enc)

		base_name, ext = os.path.splitext(self.template_filename)
		self.fdf_dumped_filename = (u'%s.fdf' % base_name).encode(enc)
		self.fdf_replaced_filename = (u'%s-replaced.fdf' % base_name).encode(enc)
		self.pdf_filled_filename = (u'%s-filled.pdf' % base_name).encode(enc)
		self.pdf_flattened_filename = (u'%s-filled-flattened.pdf' % base_name).encode(enc)
	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):

		# dump form fields from template
		cmd_line = [
			self.pdftk_binary,
			self.template_filename,
			r'generate_fdf',
			r'output',
			self.fdf_dumped_filename
		]
		_log.debug(u' '.join(cmd_line))
		try:
			pdftk = subprocess.Popen(cmd_line)
		except OSError:
			_log.exception('cannot run <pdftk> (dump data from form)')
			gmDispatcher.send(signal = u'statustext', msg = _('Error running pdftk. Cannot extract fields from PDF form template.'), beep = True)
			return False

		pdftk.communicate()
		if pdftk.returncode != 0:
			_log.error('<pdftk> returned [%s], failed to dump data from PDF form into FDF', pdftk.returncode)
			return False

		# parse dumped FDF file for "/V (...)" records
		# and replace placeholders therein
		fdf_dumped_file = open(self.fdf_dumped_filename, 'rbU')
		fdf_replaced_file = codecs.open(self.fdf_replaced_filename, 'wb')

		string_value_regex = r'\s*/V\s*\(.+\)\s*$'
		for line in fdf_dumped_file:
			if not regex.match(string_value_regex, line):
				fdf_replaced_file.write(line)
				continue

			# strip cruft around the string value
			raw_str_val = line.strip()							# remove framing whitespace
			raw_str_val = raw_str_val[2:]						# remove leading "/V"
			raw_str_val = raw_str_val.lstrip()					# remove whitespace between "/V" and "("
			raw_str_val = raw_str_val[1:]						# remove opening "("
			raw_str_val = raw_str_val[2:]						# remove BOM-16-BE
			raw_str_val = raw_str_val.rstrip()					# remove trailing whitespace
			raw_str_val = raw_str_val[:-1]						# remove closing ")"

			# work on FDF escapes
			raw_str_val = raw_str_val.replace('\(', '(')		# remove escaping of "("
			raw_str_val = raw_str_val.replace('\)', ')')		# remove escaping of ")"

			# by now raw_str_val should contain the actual
			# string value, albeit encoded as UTF-16, so
			# decode it into a unicode object,
			# split multi-line fields on "\n" literal
			raw_str_lines = raw_str_val.split('\x00\\n')
			value_template_lines = []
			for raw_str_line in raw_str_lines:
				value_template_lines.append(raw_str_line.decode('utf_16_be'))

			replaced_lines = []
			for value_template in value_template_lines:
				# find any placeholders within
				placeholders_in_value = regex.findall(data_source.placeholder_regex, value_template, regex.IGNORECASE)
				for placeholder in placeholders_in_value:
					try:
						replacement = data_source[placeholder]
					except:
						_log.exception(replacement)
						replacement = _('error with placeholder [%s]') % placeholder
					if replacement is None:
						replacement = _('error with placeholder [%s]') % placeholder
					value_template = value_template.replace(placeholder, replacement)

				value_template = value_template.encode('utf_16_be')

				if len(placeholders_in_value) > 0:
					value_template = value_template.replace(r'(', r'\(')
					value_template = value_template.replace(r')', r'\)')

				replaced_lines.append(value_template)

			replaced_line = '\x00\\n'.join(replaced_lines)

			fdf_replaced_file.write('/V (')
			fdf_replaced_file.write(codecs.BOM_UTF16_BE)
			fdf_replaced_file.write(replaced_line)
			fdf_replaced_file.write(')\n')

		fdf_replaced_file.close()
		fdf_dumped_file.close()

		# merge replaced data back into form
		cmd_line = [
			self.pdftk_binary,
			self.template_filename,
			r'fill_form',
			self.fdf_replaced_filename,
			r'output',
			self.pdf_filled_filename
		]
		_log.debug(u' '.join(cmd_line))
		try:
			pdftk = subprocess.Popen(cmd_line)
		except OSError:
			_log.exception('cannot run <pdftk> (merge data into form)')
			gmDispatcher.send(signal = u'statustext', msg = _('Error running pdftk. Cannot fill in PDF form template.'), beep = True)
			return False

		pdftk.communicate()
		if pdftk.returncode != 0:
			_log.error('<pdftk> returned [%s], failed to merge FDF data into PDF form', pdftk.returncode)
			return False

		return True
	#--------------------------------------------------------
	def edit(self):
		mimetypes = [
			u'application/pdf',
			u'application/x-pdf'
		]

		for mimetype in mimetypes:
			editor_cmd = gmMimeLib.get_editor_cmd(mimetype, self.pdf_filled_filename)
			if editor_cmd is not None:
				break

		if editor_cmd is None:
			_log.debug('editor cmd not found, trying viewer cmd')
			for mimetype in mimetypes:
				editor_cmd = gmMimeLib.get_viewer_cmd(mimetype, self.pdf_filled_filename)
				if editor_cmd is not None:
					break

		if editor_cmd is None:
			return False

		result = gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = True)

		path, fname = os.path.split(self.pdf_filled_filename)
		candidate = os.path.join(gmTools.gmPaths().home_dir, fname)

		if os.access(candidate, os.R_OK):
			_log.debug('filled-in PDF found: %s', candidate)
			os.rename(self.pdf_filled_filename, self.pdf_filled_filename + '.bak')
			shutil.move(candidate, path)
		else:
			_log.debug('filled-in PDF not found: %s', candidate)

		self.re_editable_filenames = [self.pdf_filled_filename]

		return result
	#--------------------------------------------------------
	def generate_output(self, format=None):
		"""Generate output suitable for further processing outside this class, e.g. printing."""

		# eventually flatten the filled in form so we
		# can keep  both a flattened and an editable copy:
		cmd_line = [
			self.pdftk_binary,
			self.pdf_filled_filename,
			r'output',
			self.pdf_flattened_filename,
			r'flatten'
		]
		_log.debug(u' '.join(cmd_line))
		try:
			pdftk = subprocess.Popen(cmd_line)
		except OSError:
			_log.exception('cannot run <pdftk> (flatten filled in form)')
			gmDispatcher.send(signal = u'statustext', msg = _('Error running pdftk. Cannot flatten filled in PDF form.'), beep = True)
			return None

		pdftk.communicate()
		if pdftk.returncode != 0:
			_log.error('<pdftk> returned [%s], failed to flatten filled in PDF form', pdftk.returncode)
			return None

		self.final_output_filenames = [self.pdf_flattened_filename]

		return self.pdf_flattened_filename
#------------------------------------------------------------
form_engines[u'P'] = cPDFForm

#============================================================
# older code
#------------------------------------------------------------
class cIanLaTeXForm(cFormEngine):
	"""A forms engine wrapping LaTeX.
	"""
	def __init__(self, id, template):
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




#================================================================
# define a class for HTML forms (for printing)
#================================================================
class cXSLTFormEngine(cFormEngine):
	"""This class can create XML document from requested data,
	then process it with XSLT template and display results
	"""

	# FIXME: make the path configurable ?
	_preview_program = u'oowriter '	#this program must be in the system PATH

	def __init__(self, template=None):

		if template is None:
			raise ValueError(u'%s: cannot create form instance without a template' % __name__)

		cFormEngine.__init__(self, template = template)

		self._FormData = None

		# here we know/can assume that the template was stored as a utf-8
		# encoded string so use that conversion to create unicode:
		#self._XSLTData = unicode(str(template.template_data), 'UTF-8')
		# but in fact, unicode() knows how to handle buffers, so simply:
		self._XSLTData = unicode(self.template.template_data, 'UTF-8', 'strict')

		# we must still devise a method of extracting the SQL query:
		# - either by retrieving it from a particular tag in the XSLT or
		# - by making the stored template actually be a dict which, unpickled,
		#	has the keys "xslt" and "sql"
		self._SQL_query = u'select 1'			#this sql query must output valid xml
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def process(self, sql_parameters):
		"""get data from backend and process it with XSLT template to produce readable output"""

		# extract SQL (this is wrong but displays what is intended)
		xslt = libxml2.parseDoc(self._XSLTData)
		root = xslt.children
		for child in root:
			if child.type == 'element':
				self._SQL_query = child.content
				break

		# retrieve data from backend
		rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': self._SQL_query, 'args': sql_parameters}], get_col_idx = False)

		__header = '<?xml version="1.0" encoding="UTF-8"?>\n'
		__body = rows[0][0]

		# process XML data according to supplied XSLT, producing HTML
		self._XMLData =__header + __body
		style = libxslt.parseStylesheetDoc(xslt)
		xml = libxml2.parseDoc(self._XMLData)
		html = style.applyStylesheet(xml, None)
		self._FormData = html.serialize()

		style.freeStylesheet()
		xml.freeDoc()
		html.freeDoc()
	#--------------------------------------------------------
	def preview(self):
		if self._FormData is None:
			raise ValueError, u'Preview request for empty form. Make sure the form is properly initialized and process() was performed'

		fname = gmTools.get_unique_filename(prefix = u'gm_XSLT_form-', suffix = u'.html')
		#html_file = os.open(fname, 'wb')
		#html_file.write(self._FormData.encode('UTF-8'))
		html_file = codecs.open(fname, 'wb', 'utf8', 'strict')		# or 'replace' ?
		html_file.write(self._FormData)
		html_file.close()

		cmd = u'%s %s' % (self.__class__._preview_program, fname)

		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = False):
			_log.error('%s: cannot launch report preview program' % __name__)
			return False

		#os.unlink(self.filename) #delete file
		#FIXME: under Windows the temp file is deleted before preview program gets it (under Linux it works OK) 

		return True
	#--------------------------------------------------------
	def print_directly(self):
		#not so fast, look at it first
		self.preview()


#=====================================================
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


#===========================================================
class cHL7Form (cFormEngine):
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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N, gmDateTime
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	gmDateTime.init()

	#--------------------------------------------------------
	# OOo
	#--------------------------------------------------------
	def test_init_ooo():
		init_ooo()
	#--------------------------------------------------------
	def test_ooo_connect():
		srv = gmOOoConnector()
		print srv
		print srv.desktop
	#--------------------------------------------------------
	def test_open_ooo_doc_from_srv():
		srv = gmOOoConnector()
		doc = srv.open_document(filename = sys.argv[2])
		print "document:", doc
	#--------------------------------------------------------
	def test_open_ooo_doc_from_letter():
		doc = cOOoLetter(template_file = sys.argv[2])
		doc.open_in_ooo()
		print "document:", doc
		raw_input('press <ENTER> to continue')
		doc.show()
		#doc.replace_placeholders()
		#doc.save_in_ooo('~/test_cOOoLetter.odt')
#		doc = None
#		doc.close_in_ooo()
		raw_input('press <ENTER> to continue')
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
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		doc = cOOoLetter(template_file = sys.argv[2])
		doc.open_in_ooo()
		print doc
		doc.show()
		#doc.replace_placeholders()
		#doc.save_in_ooo('~/test_cOOoLetter.odt')
		doc = None
#		doc.close_in_ooo()
		raw_input('press <ENTER> to continue')
	#--------------------------------------------------------
	# other
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
	def test_latex_form():
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		gmPerson.gmCurrentProvider(provider = gmPerson.cStaff())

		path = os.path.abspath(sys.argv[2])
		form = cLaTeXForm(template_file = path)

		from Gnumed.wxpython import gmMacro
		ph = gmMacro.gmPlaceholderHandler()
		ph.debug = True
		instance_file = form.substitute_placeholders(data_source = ph)
		pdf_name = form.generate_output(instance_file = instance_file)
		print "final PDF file is:", pdf_name
	#--------------------------------------------------------
	def test_pdf_form():
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		gmPerson.gmCurrentProvider(provider = gmPerson.cStaff())

		path = os.path.abspath(sys.argv[2])
		form = cLaPDFForm(template_file = path)

		from Gnumed.wxpython import gmMacro
		ph = gmMacro.gmPlaceholderHandler()
		ph.debug = True
		instance_file = form.substitute_placeholders(data_source = ph)
		pdf_name = form.generate_output(instance_file = instance_file)
		print "final PDF file is:", pdf_name
	#--------------------------------------------------------
	#--------------------------------------------------------
	# now run the tests
	#test_au()
	#test_de()

	# OOo
	#test_init_ooo()
	#test_ooo_connect()
	#test_open_ooo_doc_from_srv()
	#test_open_ooo_doc_from_letter()
	#play_with_ooo()
	#test_cOOoLetter()

	#test_cFormTemplate()
	#set_template_from_file()
	#test_latex_form()
	test_pdf_form()

#============================================================
