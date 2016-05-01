# -*- coding: utf-8 -*-
"""GNUmed forms classes

Business layer for printing all manners of forms, letters, scripts etc.

license: GPL v2 or later
"""
#============================================================
__author__ ="Ian Haywood <ihaywood@gnu.org>, karsten.hilbert@gmx.net"


import os
import sys
import time
import os.path
import logging
import re as regex
import shutil
import random
import platform
import subprocess
import io
import codecs
import socket										# needed for OOo on Windows
#, libxml2, libxslt
import shlex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmPraxis


_log = logging.getLogger('gm.forms')

#============================================================
# this order is also used in choice boxes for the engine
form_engine_abbrevs = [u'O', u'L', u'I', u'G', u'P', u'A', u'X', u'T']

form_engine_names = {
	u'O': 'OpenOffice',
	u'L': 'LaTeX',
	u'I': 'Image editor',
	u'G': 'Gnuplot script',
	u'P': 'PDF forms',
	u'A': 'AbiWord',
	u'X': 'Xe(La)TeX',
	u'T': 'text export'
}

form_engine_template_wildcards = {
	u'O': u'*.o?t',
	u'L': u'*.tex',
	u'G': u'*.gpl',
	u'P': u'*.pdf',
	u'A': u'*.abw',
	u'X': u'*.tex',
	u'T': u'*.ini'
}

# is filled in further below after each engine is defined
form_engines = {}

#============================================================
# match providers
#============================================================
class cFormTemplateNameLong_MatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
			SELECT
				name_long AS data,
				name_long AS list_label,
				name_long AS field_label
			FROM ref.v_paperwork_templates
			WHERE name_long %(fragment_condition)s
			ORDER BY list_label
		"""
		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = [query])
#============================================================
class cFormTemplateNameShort_MatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
			SELECT
				name_short AS data,
				name_short AS list_label,
				name_short AS field_label
			FROM ref.v_paperwork_templates
			WHERE name_short %(fragment_condition)s
			ORDER BY name_short
		"""
		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = [query])
#============================================================
class cFormTemplateType_MatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
			SELECT DISTINCT ON (list_label)
				pk AS data,
				_(name) || ' (' || name || ')' AS list_label,
				_(name) AS field_label
			FROM ref.form_types
			WHERE
				_(name) %(fragment_condition)s
					OR
				name %(fragment_condition)s
			ORDER BY list_label
		"""
		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = [query])

#============================================================
class cFormTemplate(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u'SELECT * FROM ref.v_paperwork_templates WHERE pk_paperwork_template = %s'

	_cmds_store_payload = [
		u"""UPDATE ref.paperwork_templates SET
				name_short = %(name_short)s,
				name_long = %(name_long)s,
				fk_template_type = %(pk_template_type)s,
				instance_type = %(instance_type)s,
				engine = %(engine)s,
				in_use = %(in_use)s,
				edit_after_substitution = %(edit_after_substitution)s,
				filename = %(filename)s,
				external_version = %(external_version)s
			WHERE
				pk = %(pk_paperwork_template)s
					AND
				xmin = %(xmin_paperwork_template)s
			RETURNING
				xmin AS xmin_paperwork_template
		"""
	]
	_updatable_fields = [
		u'name_short',
		u'name_long',
		u'external_version',
		u'pk_template_type',
		u'instance_type',
		u'engine',
		u'in_use',
		u'filename',
		u'edit_after_substitution'
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
		form = engine(template_file = fname)
		form.template = self
		return form

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
	cmd = u"""
		INSERT INTO ref.paperwork_templates (
			fk_template_type,
			name_short,
			name_long,
			external_version
		) VALUES (
			%(type)s,
			%(nshort)s,
			%(nlong)s,
			%(ext_version)s
		)
		RETURNING pk
	"""
	args = {'type': template_type, 'nshort': name_short, 'nlong': name_long, 'ext_version': 'new'}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	template = cFormTemplate(aPK_obj = rows[0][0])
	return template

#------------------------------------------------------------
def delete_form_template(template=None):
	rows, idx = gmPG2.run_rw_queries (
		queries = [{
			'cmd': u'DELETE FROM ref.paperwork_templates WHERE pk = %(pk)s',
			'args': {'pk': template['pk_paperwork_template']}
		}]
	)
	return True

#============================================================
# OpenOffice/LibreOffice API
#============================================================
uno = None
cOOoDocumentCloseListener = None
writer_binary = None

# http://forum.openoffice.org/en/forum/viewtopic.php?t=36370
# http://stackoverflow.com/questions/4270962/using-pyuno-with-my-existing-python-installation

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
		'oowriter',
		'swriter'
	])
	if found:
		_log.debug('OOo/LO writer binary found: %s', binary)
		writer_binary = binary
	else:
		_log.debug('OOo/LO writer binary NOT found')
		raise ImportError('LibreOffice/OpenOffice (lowriter/oowriter/swriter) not found')

	_log.debug('python UNO bridge successfully initialized')

#------------------------------------------------------------
class gmOOoConnector(gmBorg.cBorg):
	"""This class handles the connection to OOo.

	Its Singleton instance stays around once initialized.
	"""
	# FIXME: need to detect closure of OOo !
	def __init__(self):

		init_ooo()

		self.__setup_connection_string()

		self.resolver_uri = "com.sun.star.bridge.UnoUrlResolver"
		self.desktop_uri = "com.sun.star.frame.Desktop"

		self.max_connect_attempts = 5

		self.local_context = uno.getComponentContext()
		self.uri_resolver = self.local_context.ServiceManager.createInstanceWithContext(self.resolver_uri, self.local_context)

		self.__desktop = None
	#--------------------------------------------------------
	# external API
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
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = u'workplace',
			default = 3.0
		)
	#--------------------------------------------------------
	def __setup_connection_string(self):

		# socket:
#		ooo_port = u'2002'
#		#self.ooo_start_cmd = 'oowriter -invisible -norestore -nofirststartwizard -nologo -accept="socket,host=localhost,port=%s;urp;StarOffice.ServiceManager"' % ooo_port
#		self.ooo_start_cmd = 'oowriter -invisible -norestore -accept="socket,host=localhost,port=%s;urp;"' % ooo_port
#		self.remote_context_uri = "uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % ooo_port

		# pipe:
		pipe_name = "uno-gm2lo-%s" % str(random.random())[2:]
		_log.debug('expecting OOo/LO server on named pipe [%s]', pipe_name)
		self.ooo_start_cmd = '%s --invisible --norestore --accept="pipe,name=%s;urp" &' % (
			writer_binary,
			pipe_name
		)
		_log.debug('startup command: %s', self.ooo_start_cmd)

		self.remote_context_uri = "uno:pipe,name=%s;urp;StarOffice.ComponentContext" % pipe_name
		_log.debug('remote context URI: %s', self.remote_context_uri)
	#--------------------------------------------------------
	def __startup_ooo(self):
		_log.info('trying to start OOo server')
		_log.debug('startup command: %s', self.ooo_start_cmd)
		os.system(self.ooo_start_cmd)
		self.__get_startup_settle_time()
		_log.debug('waiting %s seconds for OOo to start up', self.ooo_startup_settle_time)
		time.sleep(self.ooo_startup_settle_time)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_desktop(self):
		if self.__desktop is not None:
			return self.__desktop

		self.remote_context = None

		attempts = self.max_connect_attempts
		while attempts > 0:

			_log.debug(u'attempt %s/%s', self.max_connect_attempts - attempts + 1, self.max_connect_attempts)

			try:
				self.remote_context = self.uri_resolver.resolve(self.remote_context_uri)
				break
			except oooNoConnectException:
				_log.exception('cannot connect to OOo')

			# first loop ?
			if attempts == self.max_connect_attempts:
				self.__startup_ooo()
			else:
				time.sleep(1)

			attempts = attempts - 1

		if self.remote_context is None:
			raise OSError(-1, u'cannot connect to OpenOffice', self.remote_context_uri)

		_log.debug('connection seems established')
		self.__desktop = self.remote_context.ServiceManager.createInstanceWithContext(self.desktop_uri, self.remote_context)
		_log.debug('got OOo desktop handle')
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
				val = _('error with placeholder [%s]') % placeholder_instance.String
				_log.exception(val)

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
			unlock_patient = True,
			pk_org_unit = gmPraxis.gmCurrentPraxisBranch()['pk_org_unit']
		)
		self.ooo_doc = None
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------

#============================================================
class cFormEngine(object):
	"""Ancestor for forms."""

	def __init__(self, template_file=None):
		self.template = None
		self.template_filename = template_file
		_log.debug('working on template file [%s]', self.template_filename)
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
	#--------------------------------------------------------
#	def process(self, data_source=None):
#		"""Merge values into the form template.
#		"""
#		pass
#	#--------------------------------------------------------
#	def cleanup(self):
#		"""
#		A sop to TeX which can't act as a true filter: to delete temporary files
#		"""
#		pass
#	#--------------------------------------------------------
#	def exe(self, command):
#		"""
#		Executes the provided command.
#		If command cotains %F. it is substituted with the filename
#		Otherwise, the file is fed in on stdin
#		"""
#		pass
#	#--------------------------------------------------------
#	def store(self, params=None):
#		"""Stores the parameters in the backend.
#
#		- link_obj can be a cursor, a connection or a service name
#		- assigning a cursor to link_obj allows the calling code to
#		  group the call to store() into an enclosing transaction
#		  (for an example see gmReferral.send_referral()...)
#		"""
#		# some forms may not have values ...
#		if params is None:
#			params = {}
#		patient_clinical = self.patient.get_emr()
#		encounter = patient_clinical.active_encounter['pk_encounter']
#		# FIXME: get_active_episode is no more
#		#episode = patient_clinical.get_active_episode()['pk_episode']
#		# generate "forever unique" name
#		cmd = "select name_short || ': <' || name_long || '::' || external_version || '>' from paperwork_templates where pk=%s";
#		rows = gmPG.run_ro_query('reference', cmd, None, self.pk_def)
#		form_name = None
#		if rows is None:
#			_log.error('error retrieving form def for [%s]' % self.pk_def)
#		elif len(rows) == 0:
#			_log.error('no form def for [%s]' % self.pk_def)
#		else:
#			form_name = rows[0][0]
#		# we didn't get a name but want to store the form anyhow
#		if form_name is None:
#			form_name=time.time()	# hopefully unique enough
#		# in one transaction
#		queries = []
#		# - store form instance in form_instance
#		cmd = "insert into form_instances(fk_form_def, form_name, fk_episode, fk_encounter) values (%s, %s, %s, %s)"
#		queries.append((cmd, [self.pk_def, form_name, episode, encounter]))
#		# - store params in form_data
#		for key in params.keys():
#			cmd = """
#				insert into form_data(fk_instance, place_holder, value)
#				values ((select currval('form_instances_pk_seq')), %s, %s::text)
#			"""
#			queries.append((cmd, [key, params[key]]))
#		# - get inserted PK
#		queries.append(("select currval ('form_instances_pk_seq')", []))
#		status, err = gmPG.run_commit('historica', queries, True)
#		if status is None:
#			_log.error('failed to store form [%s] (%s): %s' % (self.pk_def, form_name, err))
#			return None
#		return status

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
# AbiWord template forms
#----------------------------------------------------------------
class cAbiWordForm(cFormEngine):
	"""A forms engine wrapping AbiWord."""

	placeholder_regex = r'\$&lt;.+?&gt;\$'

	def __init__(self, template_file=None):

		super(cAbiWordForm, self).__init__(template_file = template_file)

		# detect abiword
		found, self.abiword_binary = gmShellAPI.detect_external_binary(binary = r'abiword')
		if not found:
			raise ImportError('<abiword(.exe)> not found')
	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):
		# should *actually* properly parse the XML

		path, ext = os.path.splitext(self.template_filename)
		if ext in [r'', r'.']:
			ext = r'.abw'
		self.instance_filename = r'%s-instance%s' % (path, ext)

		template_file = io.open(self.template_filename, mode = 'rt', encoding = 'utf8')
		instance_file = io.open(self.instance_filename, mode = 'wt', encoding = 'utf8')

		if self.template is not None:
			# inject placeholder values
			data_source.set_placeholder(u'form_name_long', self.template['name_long'])
			data_source.set_placeholder(u'form_name_short', self.template['name_short'])
			data_source.set_placeholder(u'form_version', self.template['external_version'])
			data_source.set_placeholder(u'form_version_internal', self.template['gnumed_revision'])
			data_source.set_placeholder(u'form_last_modified', gmDateTime.pydt_strftime(self.template['last_modified'], '%Y-%b-%d %H:%M'))

		data_source.escape_style = u'xml'
		data_source.escape_function = None			# gmTools.xml_escape_text() ?

		for line in template_file:

			if line.strip() in [u'', u'\r', u'\n', u'\r\n']:
				instance_file.write(line)
				continue

			# 1) find placeholders in this line
			placeholders_in_line = regex.findall(cAbiWordForm.placeholder_regex, line, regex.IGNORECASE)
			# 2) and replace them
			for placeholder in placeholders_in_line:
				try:
					val = data_source[placeholder.replace(u'&lt;', u'<').replace(u'&gt;', u'>')]
				except:
					val = _('error with placeholder [%s]') % gmTools.xml_escape_string(placeholder)
					_log.exception(val)

				if val is None:
					val = _('error with placeholder [%s]') % gmTools.xml_escape_string(placeholder)

				line = line.replace(placeholder, val)

			instance_file.write(line)

		instance_file.close()
		template_file.close()

		if self.template is not None:
			# remove temporary placeholders
			data_source.unset_placeholder(u'form_name_long')
			data_source.unset_placeholder(u'form_name_short')
			data_source.unset_placeholder(u'form_version')
			data_source.unset_placeholder(u'form_version_internal')
			data_source.unset_placeholder(u'form_last_modified')

		return
	#--------------------------------------------------------
	def edit(self):
		enc = sys.getfilesystemencoding()
		cmd = (r'%s %s' % (self.abiword_binary, self.instance_filename.encode(enc))).encode(enc)
		result = gmShellAPI.run_command_in_shell(command = cmd, blocking = True)
		self.re_editable_filenames = [self.instance_filename]
		return result
	#--------------------------------------------------------
	def generate_output(self, instance_file=None, format=None):

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

		pdf_name = os.path.splitext(self.instance_filename)[0] + u'.pdf'
		cmd = u'%s --to=pdf --to-name=%s %s' % (
			self.abiword_binary,
			pdf_name,
			self.instance_filename
		)
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = True):
			_log.error('problem running abiword, cannot generate form output')
			gmDispatcher.send(signal = 'statustext', msg = _('Error running AbiWord. Cannot generate PDF.'), beep = True)
			return None

		self.final_output_filenames = [pdf_name]
		return pdf_name

#----------------------------------------------------------------
form_engines[u'A'] = cAbiWordForm

#================================================================
# text template forms
#----------------------------------------------------------------
class cTextForm(cFormEngine):
	"""A forms engine outputting data as text for further processing."""

	def __init__(self, template_file=None):

		super(self.__class__, self).__init__(template_file = template_file)

		# create sandbox to play in (and don't assume much
		# of anything about the template_file except that it
		# is at our disposal for reading)
		self.__sandbox_dir = gmTools.mk_sandbox_dir()
		_log.debug('sandbox directory: [%s]', self.__sandbox_dir)

		# parse template file which is an INI style config
		# file containing the actual template plus metadata
		self.form_definition_filename = self.template_filename
		_log.debug('form definition file: [%s]', self.form_definition_filename)
		cfg_file = io.open(self.form_definition_filename, mode = 'rt', encoding = u'utf8')
		self.form_definition = gmCfg2.parse_INI_stream(stream = cfg_file)
		cfg_file.close()

		# extract actual template into a file
		template_text = self.form_definition['form::template']
		if isinstance(template_text, type([])):
			template_text = u'\n'.join(self.form_definition['form::template'])
		self.template_filename = gmTools.get_unique_filename (
			prefix = 'gm-',
			suffix = '.txt',
			tmp_dir = self.__sandbox_dir
		)
		_log.debug('template file: [%s]', self.template_filename)
		f = io.open(self.template_filename, mode = 'wt', encoding = 'utf8')
		f.write(template_text)
		f.close()

	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):

		if self.template is not None:
			# inject placeholder values
			data_source.set_placeholder(u'form_name_long', self.template['name_long'])
			data_source.set_placeholder(u'form_name_short', self.template['name_short'])
			data_source.set_placeholder(u'form_version', self.template['external_version'])
			data_source.set_placeholder(u'form_version_internal', self.template['gnumed_revision'])
			data_source.set_placeholder(u'form_last_modified', gmDateTime.pydt_strftime(self.template['last_modified'], '%Y-%b-%d %H:%M'))

		base = os.path.join(self.__sandbox_dir, gmTools.fname_stem(self.template_filename))
		filenames = [
			self.template_filename,
			r'%s-result-pass-1.txt' % base,
			r'%s-result-pass-2.txt' % base,
			r'%s-result-pass-3.txt' % base
		]
		regexen = [
			'dummy',
			data_source.first_pass_placeholder_regex,
			data_source.second_pass_placeholder_regex,
			data_source.third_pass_placeholder_regex
		]

		current_pass = 1
		while current_pass < 4:
			_log.debug('placeholder substitution pass #%s', current_pass)
			found_placeholders = self.__substitute_placeholders (
				input_filename = filenames[current_pass-1],
				output_filename = filenames[current_pass],
				data_source = data_source,
				placeholder_regex = regexen[current_pass]
			)
			current_pass += 1

		# remove temporary placeholders
		data_source.unset_placeholder(u'form_name_long')
		data_source.unset_placeholder(u'form_name_short')
		data_source.unset_placeholder(u'form_version')
		data_source.unset_placeholder(u'form_version_internal')
		data_source.unset_placeholder(u'form_last_modified')

		self.instance_filename = self.re_editable_filenames[0]

		return True

	#--------------------------------------------------------
	def __substitute_placeholders(self, data_source=None, input_filename=None, output_filename=None, placeholder_regex=None):

		_log.debug('[%s] -> [%s]', input_filename, output_filename)
		_log.debug('searching for placeholders with pattern: %s', placeholder_regex)

		template_file = io.open(input_filename, mode = 'rt', encoding = 'utf8')
		instance_file = io.open(output_filename, mode = 'wt', encoding = 'utf8')

		for line in template_file:
			# empty lines
			if line.strip() in [u'', u'\r', u'\n', u'\r\n']:
				instance_file.write(line)
				continue

			# 1) find placeholders in this line
			placeholders_in_line = regex.findall(placeholder_regex, line, regex.IGNORECASE)
			if len(placeholders_in_line) == 0:
				instance_file.write(line)
				continue

			# 2) replace them
			_log.debug('%s placeholders found in this line', len(placeholders_in_line))
			for placeholder in placeholders_in_line:
				try:
					val = data_source[placeholder]
				except:
					val = _('error with placeholder [%s]') % placeholder
					_log.exception(val)
				if val is None:
					val = _('error with placeholder [%s]') % placeholder

				line = line.replace(placeholder, val)

			instance_file.write(line)

		instance_file.close()
		self.re_editable_filenames = [output_filename]
		template_file.close()

	#--------------------------------------------------------
	def edit(self):

		editor_cmd = None
		try:
			editor_cmd = self.form_definition['form::editor'] % self.instance_filename
		except KeyError:
			_log.debug('no explicit editor defined for text template')

		if editor_cmd is None:
			mimetype = u'text/plain'
			editor_cmd = gmMimeLib.get_editor_cmd(mimetype, self.instance_filename)
			if editor_cmd is None:
				# also consider text *viewers* since pretty much any of them will be an editor as well
				editor_cmd = gmMimeLib.get_viewer_cmd(mimetype, self.instance_filename)

		if editor_cmd is not None:
			result = gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = True)
		self.re_editable_filenames = [self.instance_filename]

		return result

	#--------------------------------------------------------
	def generate_output(self, format=None):
		try:
			post_processor = self.form_definition['form::post processor'] % {
				'input_name': self.instance_filename,
				'output_name': self.instance_filename + u'.output'
			}
		except KeyError:
			_log.debug('no explicit post processor defined for text template')
			return True

		self.final_output_filenames = [self.instance_filename + u'.output']

		return gmShellAPI.run_command_in_shell(command = post_processor, blocking = True)
#------------------------------------------------------------
form_engines[u'T'] = cTextForm

#================================================================
# LaTeX template forms
#----------------------------------------------------------------
class cLaTeXForm(cFormEngine):
	"""A forms engine wrapping LaTeX."""

	def __init__(self, template_file=None):

		# create sandbox for LaTeX to play in (and don't assume
		# much of anything about the template_file except that it
		# is at our disposal for reading)
		sandbox_dir = gmTools.mk_sandbox_dir(prefix = gmTools.fname_stem(template_file) + '_')
		_log.debug('LaTeX sandbox directory: [%s]', sandbox_dir)
		shutil.copy(template_file, sandbox_dir)
		template_file = os.path.join(sandbox_dir, os.path.split(template_file)[1])

		super(self.__class__, self).__init__(template_file = template_file)

		self.__sandbox_dir = sandbox_dir

	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):

		if self.template is not None:
			# inject placeholder values
			data_source.set_placeholder(u'form_name_long', self.template['name_long'])
			data_source.set_placeholder(u'form_name_short', self.template['name_short'])
			data_source.set_placeholder(u'form_version', self.template['external_version'])
			data_source.set_placeholder(u'form_version_internal', self.template['gnumed_revision'])
			data_source.set_placeholder(u'form_last_modified', gmDateTime.pydt_strftime(self.template['last_modified'], '%Y-%b-%d %H:%M'))

		data_source.escape_function = gmTools.tex_escape_string
		data_source.escape_style = u'latex'

		path, ext = os.path.splitext(self.template_filename)
		if ext in [r'', r'.']:
			ext = r'.tex'

		filenames = [
			self.template_filename,
			r'%s-result-pass-1%s' % (path, ext),
			r'%s-result-pass-2%s' % (path, ext),
			r'%s-result-pass-3%s' % (path, ext)
		]
		regexen = [
			'dummy',
			data_source.first_pass_placeholder_regex,
			data_source.second_pass_placeholder_regex,
			data_source.third_pass_placeholder_regex
		]

		current_pass = 1
		while current_pass < 4:
			_log.debug('placeholder substitution pass #%s', current_pass)
			found_placeholders = self.__substitute_placeholders (
				input_filename = filenames[current_pass-1],
				output_filename = filenames[current_pass],
				data_source = data_source,
				placeholder_regex = regexen[current_pass]
			)
			current_pass += 1

		# remove temporary placeholders
		data_source.unset_placeholder(u'form_name_long')
		data_source.unset_placeholder(u'form_name_short')
		data_source.unset_placeholder(u'form_version')
		data_source.unset_placeholder(u'form_version_internal')
		data_source.unset_placeholder(u'form_last_modified')

		self.instance_filename = self.re_editable_filenames[0]

		return
	#--------------------------------------------------------
	def __substitute_placeholders(self, data_source=None, input_filename=None, output_filename=None, placeholder_regex=None):

		_log.debug('[%s] -> [%s]', input_filename, output_filename)
		_log.debug('searching for placeholders with pattern: %s', placeholder_regex)

		template_file = io.open(input_filename, mode = 'rt', encoding = 'utf8')
		instance_file = io.open(output_filename, mode = 'wt', encoding = 'utf8')

		for line in template_file:
			# empty lines
			if line.strip() in [u'', u'\r', u'\n', u'\r\n']:
				instance_file.write(line)
				continue
			# TeX-comment-only lines
			if line.lstrip().startswith('%'):
				instance_file.write(line)
				continue

			# 1) find placeholders in this line
			placeholders_in_line = regex.findall(placeholder_regex, line, regex.IGNORECASE)
			if len(placeholders_in_line) == 0:
				instance_file.write(line)
				continue

			# 2) replace them
			_log.debug('%s placeholders found in this line', len(placeholders_in_line))
			for placeholder in placeholders_in_line:
				try:
					val = data_source[placeholder]
				except:
					_log.exception('error with placeholder [%s]', placeholder)
					val = gmTools.tex_escape_string(_('error with placeholder [%s]') % placeholder)
				if val is None:
					_log.debug('error with placeholder [%s]', placeholder)
					val = gmTools.tex_escape_string(_('error with placeholder [%s]') % placeholder)
				line = line.replace(placeholder, val)
			instance_file.write(line)

		instance_file.close()
		self.re_editable_filenames = [output_filename]
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
			# LaTeX code is text: also consider text *viewers*
			# since pretty much any of them will be an editor as well
			for mimetype in mimetypes:
				editor_cmd = gmMimeLib.get_viewer_cmd(mimetype, self.instance_filename)
				if editor_cmd is not None:
					break

		if editor_cmd is None:
			return False

		result = gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = True)
		self.re_editable_filenames = [self.instance_filename]
		return result
	#--------------------------------------------------------
	def generate_output(self, instance_file=None, format=None):

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

		# LaTeX can need up to three runs to get cross references et al right
		if platform.system() == 'Windows':
			draft_cmd = r'pdflatex.exe -draftmode -recorder -interaction=nonstopmode -output-directory=%s %s' % (self.__sandbox_dir, self.instance_filename)
			final_cmd = r'pdflatex.exe -recorder -interaction=nonstopmode -output-directory=%s %s' % (self.__sandbox_dir, self.instance_filename)
		else:
			draft_cmd = r'pdflatex -draftmode -recorder -interaction=nonstopmode -output-directory=%s %s' % (self.__sandbox_dir, self.instance_filename)
			final_cmd = r'pdflatex -recorder -interaction=nonstopmode -output-directory=%s %s' % (self.__sandbox_dir, self.instance_filename)
		for run_cmd in [draft_cmd, draft_cmd, final_cmd]:
			if not gmShellAPI.run_command_in_shell(command = run_cmd, blocking = True, acceptable_return_codes = [0, 1]):
				_log.error('problem running pdflatex, cannot generate form output')
				gmDispatcher.send(signal = 'statustext', msg = _('Error running pdflatex. Cannot turn LaTeX template into PDF.'), beep = True)
				return None

		sandboxed_pdf_name = u'%s.pdf' % os.path.splitext(self.instance_filename)[0]
		target_dir = os.path.normpath(os.path.join(os.path.split(sandboxed_pdf_name)[0], '..'))
		final_pdf_name = os.path.join (
			target_dir,
			os.path.split(sandboxed_pdf_name)[1]
		)
		_log.debug('copying sandboxed PDF: %s -> %s', sandboxed_pdf_name, final_pdf_name)
		try:
			shutil.copy2(sandboxed_pdf_name, target_dir)
		except IOError:
			_log.exception('cannot open/move sandboxed PDF')
			gmDispatcher.send(signal = 'statustext', msg = _('PDF output file cannot be opened.'), beep = True)
			return None

		self.final_output_filenames = [final_pdf_name]

		return final_pdf_name
#------------------------------------------------------------
form_engines[u'L'] = cLaTeXForm

#================================================================
# Xe(La)TeX template forms
#----------------------------------------------------------------
# Xe(La)TeX: http://www.scholarsfonts.net/xetextt.pdf
class cXeTeXForm(cFormEngine):
	"""A forms engine wrapping Xe(La)TeX."""

	def __init__(self, template_file=None):

		# create sandbox for LaTeX to play in (and don't assume
		# much of anything about the template_file except that it
		# is at our disposal)
		sandbox_dir = gmTools.mk_sandbox_dir(prefix = gmTools.fname_stem(template_file) + '_')
		_log.debug('Xe(La)TeX sandbox directory: [%s]', sandbox_dir)
		shutil.copy(template_file, sandbox_dir)
		template_file = os.path.join(sandbox_dir, os.path.split(template_file)[1])

		super(self.__class__, self).__init__(template_file = template_file)

		self.__sandbox_dir = sandbox_dir
	#--------------------------------------------------------
	def substitute_placeholders(self, data_source=None):

		if self.template is not None:
			# inject placeholder values
			data_source.set_placeholder(u'form_name_long', self.template['name_long'])
			data_source.set_placeholder(u'form_name_short', self.template['name_short'])
			data_source.set_placeholder(u'form_version', self.template['external_version'])
			data_source.set_placeholder(u'form_version_internal', self.template['gnumed_revision'])
			data_source.set_placeholder(u'form_last_modified', gmDateTime.pydt_strftime(self.template['last_modified'], '%Y-%b-%d %H:%M'))

		data_source.escape_function = gmTools.xetex_escape_string
		data_source.escape_style = u'xetex'

		path, ext = os.path.splitext(self.template_filename)
		if ext in [r'', r'.']:
			ext = r'.tex'

		filenames = [
			self.template_filename,
			r'%s-result_run1%s' % (path, ext),
			r'%s-result_run2%s' % (path, ext),
			r'%s-result_run3%s' % (path, ext)
		]

		found_placeholders = True
		current_run = 1
		while found_placeholders and (current_run < 4):
			_log.debug('placeholder substitution run #%s', current_run)
			found_placeholders = self.__substitute_placeholders (
				input_filename = filenames[current_run-1],
				output_filename = filenames[current_run],
				data_source = data_source
			)
			current_run += 1

		if self.template is not None:
			# remove temporary placeholders
			data_source.unset_placeholder(u'form_name_long')
			data_source.unset_placeholder(u'form_name_short')
			data_source.unset_placeholder(u'form_version')
			data_source.unset_placeholder(u'form_version_internal')
			data_source.unset_placeholder(u'form_last_modified')

		self.instance_filename = self.re_editable_filenames[0]

		return
	#--------------------------------------------------------
	def __substitute_placeholders(self, data_source=None, input_filename=None, output_filename=None):
		_log.debug('[%s] -> [%s]', input_filename, output_filename)

		found_placeholders = False

		template_file = io.open(input_filename, mode = 'rt', encoding = 'utf8')
		instance_file = io.open(output_filename, mode = 'wt', encoding = 'utf8')

		for line in template_file:

			if line.strip() in [u'', u'\r', u'\n', u'\r\n']:		# empty lines
				instance_file.write(line)
				continue
			if line.startswith('%'):		# TeX comment
				instance_file.write(line)
				continue

			for placeholder_regex in [data_source.first_pass_placeholder_regex, data_source.second_pass_placeholder_regex, data_source.third_pass_placeholder_regex]:
				# 1) find placeholders in this line
				placeholders_in_line = regex.findall(placeholder_regex, line, regex.IGNORECASE)
				if len(placeholders_in_line) == 0:
					continue
				_log.debug('%s placeholders found with pattern: %s', len(placeholders_in_line), placeholder_regex)
				found_placeholders = True
				# 2) replace them
				for placeholder in placeholders_in_line:
					try:
						val = data_source[placeholder]
					except:
						_log.exception('error with placeholder [%s]', placeholder)
						val = gmTools.tex_escape_string(_('error with placeholder [%s]') % placeholder)

					if val is None:
						_log.debug('error with placeholder [%s]', placeholder)
						val = _('error with placeholder [%s]') % gmTools.tex_escape_string(placeholder)

					line = line.replace(placeholder, val)

			instance_file.write(line)

		instance_file.close()
		self.re_editable_filenames = [output_filename]
		template_file.close()

		return found_placeholders
	#--------------------------------------------------------
	def edit(self):

		mimetypes = [
			u'application/x-xetex',
			u'application/x-latex',
			u'application/x-tex',
			u'text/plain'
		]

		for mimetype in mimetypes:
			editor_cmd = gmMimeLib.get_editor_cmd(mimetype, self.instance_filename)
			if editor_cmd is not None:
				break

		if editor_cmd is None:
			# Xe(La)TeX code is utf8: also consider text *viewers*
			# since pretty much any of them will be an editor as well
			for mimetype in mimetypes:
				editor_cmd = gmMimeLib.get_viewer_cmd(mimetype, self.instance_filename)
				if editor_cmd is not None:
					break

		if editor_cmd is None:
			return False

		result = gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = True)
		self.re_editable_filenames = [self.instance_filename]
		return result
	#--------------------------------------------------------
	def generate_output(self, instance_file=None, format=None):

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

		# Xe(La)TeX can need up to three runs to get cross references et al right
		if platform.system() == 'Windows':
			# not yet supported: -draftmode
			# does not support: -shell-escape
			draft_cmd = r'xelatex.exe -interaction=nonstopmode -output-directory=%s %s' % (self.__sandbox_dir, self.instance_filename)
			final_cmd = r'xelatex.exe -interaction=nonstopmode -output-directory=%s %s' % (self.__sandbox_dir, self.instance_filename)
		else:
			# not yet supported: -draftmode
			draft_cmd = r'xelatex -interaction=nonstopmode -output-directory=%s -shell-escape %s' % (self.__sandbox_dir, self.instance_filename)
			final_cmd = r'xelatex -interaction=nonstopmode -output-directory=%s -shell-escape %s' % (self.__sandbox_dir, self.instance_filename)

		for run_cmd in [draft_cmd, draft_cmd, final_cmd]:
			if not gmShellAPI.run_command_in_shell(command = run_cmd, blocking = True, acceptable_return_codes = [0, 1]):
				_log.error('problem running xelatex, cannot generate form output')
				gmDispatcher.send(signal = 'statustext', msg = _('Error running xelatex. Cannot turn Xe(La)TeX template into PDF.'), beep = True)
				return None

		sandboxed_pdf_name = u'%s.pdf' % os.path.splitext(self.instance_filename)[0]
		target_dir = os.path.normpath(os.path.join(os.path.split(sandboxed_pdf_name)[0], '..'))
		final_pdf_name = os.path.join (
			target_dir,
			os.path.split(sandboxed_pdf_name)[1]
		)
		_log.debug('copying sandboxed PDF: %s -> %s', sandboxed_pdf_name, final_pdf_name)
		try:
			shutil.copy2(sandboxed_pdf_name, target_dir)
		except IOError:
			_log.exception('cannot open/move sandboxed PDF')
			gmDispatcher.send(signal = 'statustext', msg = _('PDF output file cannot be opened.'), beep = True)
			return None

		self.final_output_filenames = [final_pdf_name]

		return final_pdf_name

#------------------------------------------------------------
form_engines[u'X'] = cXeTeXForm

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
		conf_file = io.open(self.conf_filename, mode = 'wt', encoding = 'utf8')
		conf_file.write(u'# setting the gnuplot data file\n')
		conf_file.write(u"gm2gpl_datafile = '%s'\n" % self.data_filename)
		conf_file.close()

		# FIXME: cater for configurable path
		if platform.system() == 'Windows':
			exec_name = 'gnuplot.exe'
		else:
			exec_name = 'gnuplot'

		args = [
			exec_name,
			'-p',					# let plot window persist after main gnuplot process exits
			self.conf_filename,		# contains the gm2gpl_datafile setting which, in turn, contains the actual data
			self.template_filename	# contains the plotting instructions (IOW a user provided gnuplot script)
		]
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
		fdf_dumped_file = io.open(self.fdf_dumped_filename, mode = 'rt', encoding = u'utf8')
		fdf_replaced_file = io.open(self.fdf_replaced_filename, mode = 'wt', encoding = u'utf8')

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

			fdf_replaced_file.write(u'/V (')
			fdf_replaced_file.write(codecs.BOM_UTF16_BE)
			fdf_replaced_file.write(replaced_line)
			fdf_replaced_file.write(u')\n')

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
		html_file = io.open(fname, mode = 'wt', encoding = 'utf8', errors = 'strict')		# or 'replace' ?
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
	f = io.open('../../test-area/ian/terry-form.tex')
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
	'COPYADDRESS':'Jack Jones\nHannover, Germany',
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
		template = io.open('../../test-area/ian/Formularkopf-DE.tex')
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

		gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())

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

		gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())

		path = os.path.abspath(sys.argv[2])
		form = cPDFForm(template_file = path)

		from Gnumed.wxpython import gmMacro
		ph = gmMacro.gmPlaceholderHandler()
		ph.debug = True
		instance_file = form.substitute_placeholders(data_source = ph)
		pdf_name = form.generate_output(instance_file = instance_file)
		print "final PDF file is:", pdf_name
	#--------------------------------------------------------
	def test_abiword_form():
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())

		path = os.path.abspath(sys.argv[2])
		form = cAbiWordForm(template_file = path)

		from Gnumed.wxpython import gmMacro
		ph = gmMacro.gmPlaceholderHandler()
		ph.debug = True
		instance_file = form.substitute_placeholders(data_source = ph)
		form.edit()
		final_name = form.generate_output(instance_file = instance_file)
		print "final file is:", final_name
	#--------------------------------------------------------
	def test_text_form():

		from Gnumed.business import gmPraxis

		branches = gmPraxis.get_praxis_branches()
		praxis = gmPraxis.gmCurrentPraxisBranch(branches[0])
		print praxis

		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPerson.set_active_patient(patient = pat)

		gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())

		path = os.path.abspath(sys.argv[2])
		form = cTextForm(template_file = path)

		from Gnumed.wxpython import gmMacro
		ph = gmMacro.gmPlaceholderHandler()
		ph.debug = True
		print "placeholder substitution worked:", form.substitute_placeholders(data_source = ph)
		print form.re_editable_filenames
		form.edit()
		form.generate_output()
	#--------------------------------------------------------
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
	#test_pdf_form()
	#test_abiword_form()
	test_text_form()

#============================================================
