"""GNUmed export area

Think shopping cart in a web shop.

This is where you want to put documents for further
processing by you or someone else, like your secretary.
"""
#============================================================
__license__ = "GPL v2 or later"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging
import shutil
import os
import io


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmCfg2

from Gnumed.business import gmDocuments
from Gnumed.business import gmKeywordExpansion


_log = logging.getLogger('gm.exp_area')

PRINT_JOB_DESIGNATION = u'print'

#============================================================
# export area item handling
#------------------------------------------------------------
_SQL_get_export_items = u"SELECT * FROM clin.v_export_items WHERE %s"

class cExportItem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents an item in the export area table"""

	_cmd_fetch_payload = _SQL_get_export_items % u"pk_export_item = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.export_item SET
				fk_identity = %(pk_identity)s,
				created_by = gm.nullify_empty_string(%(created_by)s),
				created_when = %(created_when)s,
				designation = gm.nullify_empty_string(%(designation)s),
				description = gm.nullify_empty_string(%(description)s),
				fk_doc_obj = %(pk_doc_obj)s,
				data = CASE
					WHEN %(pk_doc_obj)s IS NULL THEN coalesce(data, 'to be replaced by real data')
					ELSE NULL
				END,
				filename = CASE
					WHEN %(pk_doc_obj)s IS NULL THEN gm.nullify_empty_string(%(filename)s)
					ELSE NULL
				END
			WHERE
				pk = %(pk_export_item)s
					AND
				xmin = %(xmin_export_item)s
		""",
		_SQL_get_export_items % u'pk_export_item = %(pk_export_item)s'
	]
	_updatable_fields = [
		u'pk_identity',
		u'created_when',
		u'designation',
		u'description',
		u'pk_doc_obj',
		u'filename'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None, link_obj=None):
		super(cExportItem, self).__init__(aPK_obj = aPK_obj, row = row, link_obj = link_obj)
		# force auto-healing if need be
		if self._payload[self._idx['pk_identity_raw_needs_update']]:
			_log.warning (
				u'auto-healing export item [%s] from identity [%s] to [%s] because of document part [%s] seems necessary',
				self._payload[self._idx['pk_export_item']],
				self._payload[self._idx['pk_identity_raw']],
				self._payload[self._idx['pk_identity']],
				self._payload[self._idx['pk_doc_obj']]
			)
			if self._payload[self._idx['pk_doc_obj']] is None:
				_log.error(u'however, .fk_doc_obj is NULL, which should not happen, leaving things alone for manual inspection')
				return
			# only flag ourselves as modified, do not actually
			# modify any values, better safe than sorry
			self._is_modified = True
			self.save()
			self.refetch_payload(ignore_changes = False, link_obj = link_obj)

	#--------------------------------------------------------
#	def format(self):
#		return u'%s' % self
	#--------------------------------------------------------
	def update_data_from_file(self, filename=None):
		# sanity check
		if not (os.access(filename, os.R_OK) and os.path.isfile(filename)):
			_log.error('[%s] is not a readable file' % filename)
			return False

		cmd = u"""
			UPDATE clin.export_item SET
				data = %(data)s::bytea,
				fk_doc_obj = NULL,
				filename = gm.nullify_empty_string(%(fname)s)
			WHERE pk = %(pk)s"""
		args = {'pk': self.pk_obj, 'fname': filename}
		if not gmPG2.file2bytea(query = cmd, filename = filename, args = args):
			return False

		# must update XMIN now ...
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def save_to_file(self, aChunkSize=0, filename=None, directory=None):

		# data linked from archive
		if self._payload[self._idx['pk_doc_obj']] is not None:
			part = self.document_part
			if filename is None:
				filename = part.get_useful_filename (
					make_unique = False,
					directory = directory,
					include_gnumed_tag = False,
					date_before_type = True,
					name_first = False
				)
			return part.save_to_file (
				aChunkSize = aChunkSize,
				filename = filename,
				ignore_conversion_problems = True,
				adjust_extension = True
			)

		# data in export area table
		if filename is None:
			filename = self.get_useful_filename(directory = directory)

		success = gmPG2.bytea2file (
			data_query = {
				'cmd': u'SELECT substring(data from %(start)s for %(size)s) FROM clin.export_item WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['size']]
		)
		if not success:
			return None

		if filename.endswith(u'.dat'):
			return gmMimeLib.adjust_extension_by_mimetype(filename)

		return filename

	#--------------------------------------------------------
	def display_via_mime(self, chunksize=0, block=None):

		if self._payload[self._idx['pk_doc_obj']] is not None:
			return self.document_part.display_via_mime(chunksize = chunksize, block = block)

		fname = self.save_to_file(aChunkSize = chunksize)
		if fname is None:
			return False, ''

		success, msg = gmMimeLib.call_viewer_on_file(fname, block = block)
		if not success:
			return False, msg

		return True, ''

	#--------------------------------------------------------
	def get_useful_filename(self, patient=None, directory=None):
		patient_part = ''
		if patient is not None:
			patient_part = '-%s' % patient['dirname']

		# preserve original filename extension if available
		suffix = '.dat'
		if self._payload[self._idx['filename']] is not None:
			tmp, suffix = os.path.splitext (
				gmTools.fname_sanitize(self._payload[self._idx['filename']]).lower()
			)
			if suffix == u'':
				suffix = '.dat'

		fname = gmTools.get_unique_filename (
			prefix = 'gm-export_item%s-' % patient_part,
			suffix = suffix,
			tmp_dir = directory
		)

		return os.path.join(directory, fname)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_doc_part(self):
		if self._payload[self._idx['pk_doc_obj']] is None:
			return None
		return gmDocuments.cDocumentPart(aPK_obj = self._payload[self._idx['pk_doc_obj']])

	document_part = property(_get_doc_part, lambda x:x)

	#--------------------------------------------------------
	def _get_is_print_job(self):
		return self._payload[self._idx['designation']] == PRINT_JOB_DESIGNATION

	def _set_is_print_job(self, is_print_job):
		desig = gmTools.bool2subst(is_print_job, PRINT_JOB_DESIGNATION, None, None)
		if self._payload[self._idx['designation']] == desig:
			return
		self['designation'] = desig
		self.save()

	is_print_job = property(_get_is_print_job, _set_is_print_job)

#------------------------------------------------------------
def get_export_items(order_by=None, pk_identity=None, designation=None):

	args = {
		'pat': pk_identity,
		'desig': gmTools.coalesce(designation, PRINT_JOB_DESIGNATION)
	}
	where_parts = []
	if pk_identity is not None:
		where_parts.append(u'pk_identity = %(pat)s')
		# note that invalidly linked items will be
		# auto-healed when instantiated
	if designation is None:
		where_parts.append(u"designation IS DISTINCT FROM %(desig)s")
	else:
		where_parts.append(u'designation = %(desig)s')

	if order_by is None:
		order_by = u''
	else:
		order_by = u' ORDER BY %s' % order_by

	cmd = (_SQL_get_export_items % u' AND '.join(where_parts)) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'}) for r in rows ]

#------------------------------------------------------------
def get_print_jobs(order_by=None, pk_identity=None):
	return get_export_items(order_by = order_by, pk_identity = pk_identity, designation = PRINT_JOB_DESIGNATION)

#------------------------------------------------------------
def create_export_item(description=None, pk_identity=None, pk_doc_obj=None, filename=None):

	args = {
		u'desc': description,
		u'pk_obj': pk_doc_obj,
		u'pk_pat': pk_identity,
		u'fname': filename
	}
	cmd = u"""
		INSERT INTO clin.export_item (
			description,
			fk_doc_obj,
			fk_identity,
			data,
			filename
		) VALUES (
			gm.nullify_empty_string(%(desc)s),
			%(pk_obj)s,
			%(pk_pat)s,
			(CASE
				WHEN %(pk_obj)s IS NULL THEN %(fname)s::bytea
				ELSE NULL::bytea
			END),
			(CASE
				WHEN %(pk_obj)s IS NULL THEN gm.nullify_empty_string(%(fname)s)
				ELSE NULL
			END)
		)
		RETURNING pk
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cExportItem(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_export_item(pk_export_item=None):
	args = {'pk': pk_export_item}
	cmd = u"DELETE FROM clin.export_item WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
_html_start = u"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<link rel="icon" type="image/x-icon" href="gnumed.ico">
<title>%(html_title_header)s %(html_title_patient)s</title>
</head>
<body>

<h1>%(title)s</h1>

<p>
	%(pat_name)s<br>
	%(pat_dob)s
</p>

<p><img src="%(mugshot_url)s" alt="%(mugshot_alt)s" title="%(mugshot_title)s" width="200" border="2"></p>

<h2>%(docs_title)s</h2>

<ul>
	<li><a href="./">%(browse_root)s</a></li>
	<li><a href="documents/">%(browse_docs)s</a></li>
	%(browse_dicomdir)s
	%(run_dicom_viewer)s
</ul>

<ul>
"""

# <li><a href="documents/filename-1.ext">document 1 description</a></li>

_html_list_item = u"""	<li><a href="documents/%s">%s</a></li>
"""

_html_end = u"""
</ul>

<p>
%(date)s<br>
%(branch)s @ %(praxis)s
%(adr)s
</p>

(<a href="http://www.gnumed.de">GNUmed</a> version %(gm_ver)s)

</body>
</html>
"""


_autorun_inf = (							# needs \r\n for Windows
	u'[AutoRun.Amd64]\r\n'					# 64 bit
	u'label=%(label)s\r\n'					# patient name/DOB
	u'shellexecute=index.html\r\n'
	u'action=%(action)s\r\n'				# % _('Browse patient data')
	u'%(icon)s\r\n'							# "icon=gnumed.ico" or ""
	u'UseAutoPlay=1\r\n'
	u'\r\n'
	u'[AutoRun]\r\n'						# 32 bit
	u'label=%(label)s\r\n'					# patient name/DOB
	u'shellexecute=index.html\r\n'
	u'action=%(action)s\r\n'				# % _('Browse patient data')
	u'%(icon)s\r\n'							# "icon=gnumed.ico" or ""
	u'UseAutoPlay=1\r\n'
	u'\r\n'
	u'[Content]\r\n'
	u'PictureFiles=yes\r\n'
	u'VideoFiles=yes\r\n'
	u'MusicFiles=no\r\n'
	u'\r\n'
	u'[IgnoreContentPaths]\r\n'
	u'\documents\r\n'
	u'\r\n'
	u'[unused]\r\n'
	u'open=requires explicit executable\r\n'
)


_cd_inf = (
u'[Patient Info]\r\n'					# needs \r\n for Windows
u'PatientName=%s, %s\r\n'
u'Gender=%s\r\n'
u'BirthDate=%s\r\n'
u'CreationDate=%s\r\n'
u'PID=%s\r\n'
u'EMR=GNUmed\r\n'
u'Version=%s\r\n'
u'#StudyDate=\r\n'
u'#VNRInfo=<body part>\r\n'
u'\r\n'
u'# name format: lastnames, firstnames\r\n'
u'# date format: YYYY-MM-DD (ISO 8601)\r\n'
u'# gender format: %s\r\n'
)

_README = u"""This is a patient data bundle created by the GNUmed Electronic Medical Record.

Patient: %s

Please display <index.html> to browse patient data.

Individual documents are stored under

	./documents/
"""

#------------------------------------------------------------
class cExportArea(object):

	def __init__(self, pk_identity):
		self.__pk_identity = pk_identity

	#--------------------------------------------------------
	def add_form(self, form=None, designation=None):

		if len(form.final_output_filenames) == 0:
			return True

		items = []
		for fname in form.final_output_filenames:
			item = self.add_file(filename = fname)
			if item is None:
				for prev_item in items:
					delete_export_item(pk_export_item = prev_item['pk_export_item'])
				return False
			items.append(item)
			item['description'] = _(u'form: %s %s (%s)') % (form.template['name_long'], form.template['external_version'], fname)
			item['designation'] = designation
			item.save()

		return True
	#--------------------------------------------------------
	def add_forms(self, forms=None, designation=None):
		all_ok = True
		for form in forms:
			all_ok = all_ok and self.add_form(form = form, designation = designation)

		return all_ok
	#--------------------------------------------------------
	def add_file(self, filename=None, hint=None):
		try:
			open(filename).close()
		except Exception:
			_log.exception('cannot open file <%s>', filename)
			return None

		file_md5 = gmTools.file2md5(filename = filename, return_hex = True)
		existing_item = self.md5_exists(md5 = file_md5, include_document_parts = False)
		if existing_item is not None:
			_log.debug('md5 match (%s): %s already in export area', file_md5, filename)
			return existing_item

		path, basename = os.path.split(filename)
		item = create_export_item (
			description = u'%s: %s (%s/)' % (
				gmTools.coalesce(hint, _(u'file'), u'%s'),
				basename,
				path
			),
			pk_identity = self.__pk_identity,
			filename = filename
		)

		if item.update_data_from_file(filename = filename):
			return item

		delete_export_item(pk_export_item = item['pk_export_item'])
		return None

	#--------------------------------------------------------
	def add_files(self, filenames=None, hint=None):
		all_ok = True
		for fname in filenames:
			all_ok = all_ok and (self.add_file(filename = fname, hint = hint) is not None)

		return all_ok

	#--------------------------------------------------------
	def add_documents(self, documents=None):
		for doc in documents:
			doc_tag = _(u'%s (%s)%s') % (
				doc['l10n_type'],
				gmDateTime.pydt_strftime(doc['clin_when'], '%Y %b %d'),
				gmTools.coalesce(doc['comment'], u'', u' "%s"')
			)
			for obj in doc.parts:
				if self.document_part_item_exists(pk_part = obj['pk_obj']):
					continue
				f_ext = u''
				if obj['filename'] is not None:
					f_ext = os.path.splitext(obj['filename'])[1].strip('.').strip()
				if f_ext != u'':
					f_ext = u' .' + f_ext.upper()
				obj_tag = _(u'part %s (%s%s)%s') % (
					obj['seq_idx'],
					gmTools.size2str(obj['size']),
					f_ext,
					gmTools.coalesce(obj['obj_comment'], u'', u' "%s"')
				)
				create_export_item (
					description = u'%s - %s' % (doc_tag, obj_tag),
					pk_doc_obj = obj['pk_obj']
				)

	#--------------------------------------------------------
	def document_part_item_exists(self, pk_part=None):
		cmd = u"SELECT EXISTS (SELECT 1 FROM clin.export_item WHERE fk_doc_obj = %(pk_obj)s)"
		args = {'pk_obj': pk_part}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	#--------------------------------------------------------
	def md5_exists(self, md5=None, include_document_parts=False):
		where_parts = [
			u'pk_identity = %(pat)s',
			u'md5_sum = %(md5)s'
		]
		args = {
			'pat': self.__pk_identity,
			'md5': md5
		}

		if not include_document_parts:
			where_parts.append(u'pk_doc_obj IS NULL')

		cmd = _SQL_get_export_items % u' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			return None

		r = rows[0]
		return cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'})

	#--------------------------------------------------------
	def export(self, base_dir=None, items=None, with_metadata=True, expand_compressed=False):

		if items is None:
			items = self.items

		if len(items) == 0:
			return None

		media_base_dir = base_dir

		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = self.__pk_identity)
		if media_base_dir is None:
			media_base_dir = gmTools.mk_sandbox_dir(prefix = u'exp-%s-' % pat.dirname)
		_log.debug('patient media base dir: %s', media_base_dir)

		doc_dir = os.path.join(media_base_dir, r'documents')
		if os.path.isdir(doc_dir):
			index_existing_docs = True
		else:
			index_existing_docs = False
			gmTools.mkdir(doc_dir)

		_html_start_data = {
			u'html_title_header': _('Patient data for'),
			u'html_title_patient': gmTools.html_escape_string(pat.get_description_gender(with_nickname = False) + u', ' + _(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d')),
			u'title': _('Patient data export'),
			u'pat_name': gmTools.html_escape_string(pat.get_description_gender(with_nickname = False)),
			u'pat_dob': gmTools.html_escape_string(_(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d')),
			u'mugshot_url': u'documents/no-such-file.png',
			u'mugshot_alt': _('no patient photograph available'),
			u'mugshot_title': u'',
			u'docs_title': _(u'Documents'),
			u'browse_root': _(u'browse storage medium'),
			u'browse_docs': _(u'browse documents area'),
			u'browse_dicomdir': u'',
			u'run_dicom_viewer': u''
		}

		mugshot = pat.document_folder.latest_mugshot
		if mugshot is not None:
			_html_start_data['mugshot_url'] = mugshot.save_to_file(directory = doc_dir, adjust_extension = True)
			_html_start_data['mugshot_alt'] =_('patient photograph from %s') % gmDateTime.pydt_strftime(mugshot['date_generated'], '%B %Y')
			_html_start_data['mugshot_title'] = gmDateTime.pydt_strftime(mugshot['date_generated'], '%B %Y')

		if u'DICOMDIR' in os.listdir(media_base_dir):
			_html_start_data[u'browse_dicomdir'] = u'<li><a href="./DICOMDIR">%s</a></li>' % _(u'show DICOMDIR file')
			# copy DWV into target dir
			dwv_target_dir = os.path.join(media_base_dir, u'dwv')
			gmTools.rmdir(dwv_target_dir)
			dwv_src_dir = os.path.join(gmTools.gmPaths().local_base_dir, u'dwv4export')
			if not os.path.isdir(dwv_src_dir):
				dwv_src_dir = os.path.join(gmTools.gmPaths().system_app_data_dir, u'dwv4export')
			try:
				shutil.copytree(dwv_src_dir, dwv_target_dir)
				_html_start_data[u'run_dicom_viewer'] = u'<li><a href="./dwv/viewers/mobile-local/index.html">%s</a></li>' % _(u'run Radiology Images (DICOM) Viewer')
			except shutil.Error, OSError:
				_log.exception('cannot include DWV, skipping')

		# index.html
		# - header
		idx_fname = os.path.join(media_base_dir, u'index.html')
		idx_file = io.open(idx_fname, mode = u'wt', encoding = u'utf8')
		idx_file.write(_html_start % _html_start_data)
		# - middle (side effect ! -> exports items into files ...)
		existing_docs = os.listdir(doc_dir)
		# - export items
		for item in items:
			item_path = item.save_to_file(directory = doc_dir)
			item_fname = os.path.split(item_path)[1]
			idx_file.write(_html_list_item % (
				item_fname,
				gmTools.html_escape_string(item['description'])
			))
		# - preexisting documents
		for doc_fname in existing_docs:
			idx_file.write(_html_list_item % (
				doc_fname,
				gmTools.html_escape_string(_(u'other: %s') % doc_fname)
			))
		# - footer
		_cfg = gmCfg2.gmCfgData()
		from Gnumed.business.gmPraxis import gmCurrentPraxisBranch
		prax = gmCurrentPraxisBranch()
		lines = []
		adr = prax.branch.org_unit.address
		if adr is not None:
			lines.extend(adr.format())
		for comm in prax.branch.org_unit.comm_channels:
			if comm['is_confidential'] is True:
				continue
			lines.append(u'%s: %s' % (
				comm['l10n_comm_type'],
				comm['url']
			))
		adr = u''
		if len(lines) > 0:
			adr = gmTools.html_escape_string(u'\n'.join(lines), replace_eol = True, keep_visual_eol = True)
		_html_end_data = {
			'branch': gmTools.html_escape_string(prax['branch']),
			'praxis': gmTools.html_escape_string(prax['praxis']),
			'date' : gmTools.html_escape_string(gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y %B %d', encoding = u'utf8')),
			'gm_ver': gmTools.html_escape_string(_cfg.get(option = u'client_version')),
			#'gm_ver': 'git HEAD',				# for testing
			'adr': adr
		}
		idx_file.write(_html_end % _html_end_data)
		idx_file.close()

		# start.html (just a copy of index.html, really ;-)
		start_fname = os.path.join(media_base_dir, u'start.html')
		try:
			shutil.copy2(idx_fname, start_fname)
		except Exception:
			_log.exception('cannot copy %s to %s', idx_fname, start_fname)

		# autorun.inf
		# - compute label
		autorun_dict = {}
		name = pat.active_name
		last = name['lastnames'][:14]
		first = name['firstnames'][:min(14, 18 - len(last))]
		autorun_dict['label'] = ((u'%s%s%s' % (
			u'%s,%s' % (last, first),
			gmTools.coalesce(pat['gender'], u'', u' (%s)'),
			pat.get_formatted_dob(format = ' %Y%m%d', none_string = u'', honor_estimation = False)
		)).strip())[:32]		# max 32 chars, supposedly ASCII, but CP1252 likely works pretty well
		# - compute icon
		media_icon_kwd = u'$$gnumed_patient_media_export_icon'
		media_icon_kwd_exp = gmKeywordExpansion.get_expansion (
			keyword = media_icon_kwd,
			textual_only = False,
			binary_only = True
		)
		icon_tmp_file = media_icon_kwd_exp.save_to_file (
			target_mime = u'image/x-icon',
			target_extension = u'.ico',
			ignore_conversion_problems = True
		)
		autorun_dict['icon'] = u''
		if icon_tmp_file is None:
			_log.debug(u'cannot retrieve <%s>', media_icon_kwd)
		else:
			media_icon_fname = os.path.join(media_base_dir, u'gnumed.ico')
			try:
				shutil.move(icon_tmp_file, media_icon_fname)
				autorun_dict['icon'] = u'icon=gnumed.ico'
			except Exception:
				_log.exception('cannot move %s to %s', icon_tmp_file, media_icon_fname)
		# - compute action
		autorun_dict['action'] = _('Browse patient data')
		# - create file
		autorun_fname = os.path.join(media_base_dir, u'autorun.inf')
		autorun_file = io.open(autorun_fname, mode = 'wt', encoding = 'cp1252', errors = 'replace')
		autorun_file.write(_autorun_inf % autorun_dict)
		autorun_file.close()

		# cd.inf
		cd_inf_fname = os.path.join(media_base_dir, u'cd.inf')
		cd_inf_file = io.open(cd_inf_fname, mode = u'wt', encoding = u'utf8')
		cd_inf_file.write(_cd_inf % (
			pat['lastnames'],
			pat['firstnames'],
			gmTools.coalesce(pat['gender'], u'?'),
			pat.get_formatted_dob('%Y-%m-%d'),
			gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y-%m-%d', encoding = u'utf8'),
			pat.ID,
			_cfg.get(option = u'client_version'),
			u' / '.join([ u'%s = %s (%s)' % (g['tag'], g['label'], g['l10n_label']) for g in pat.gender_list ])
		))
		cd_inf_file.close()

		# README
		readme_fname = os.path.join(media_base_dir, u'README')
		readme_file = io.open(readme_fname, mode = u'wt', encoding = u'utf8')
		readme_file.write(_README % (
			pat.get_description_gender(with_nickname = False) + u', ' + _(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d')
		))
		readme_file.close()

		# patient demographics as GDT/XML/VCF
		pat.export_as_gdt(filename = os.path.join(media_base_dir, u'patient.gdt'))
		pat.export_as_xml_linuxmednews(filename = os.path.join(media_base_dir, u'patient.xml'))
		pat.export_as_vcard(filename = os.path.join(media_base_dir, u'patient.vcf'))

		# praxis VCF
		shutil.move(prax.vcf, os.path.join(media_base_dir, u'praxis.vcf'))

		return media_base_dir

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def get_items(self, designation=None, order_by=u'designation, description'):
		return get_export_items(order_by = order_by, pk_identity = self.__pk_identity, designation = designation)

	items = property(get_items, lambda x:x)
	#--------------------------------------------------------
	def get_printouts(self, order_by=u'designation, description'):
		return get_print_jobs(order_by = order_by, pk_identity = self.__pk_identity)

	printouts = property(get_printouts, lambda x:x)

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.business import gmPraxis

	#---------------------------------------
	def test_export_items():
#		items = get_export_items()
#		for item in items:
#			print item.format()
		import random
		create_export_item(description = 'description %s' % random.random(), pk_identity = 12, pk_doc_obj = None, filename = u'dummy.dat')
		items = get_export_items()
		for item in items:
			print item.format()
		item['pk_doc_obj'] = 1
		item.save()
		print item
	#---------------------------------------
	def test_export_area():
		exp = cExportArea(12)
		#print exp.export_with_meta_data()
		#print exp.items
		exp.add_file(sys.argv[2])
		prax = gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.cPraxisBranch(1))
		print prax
		print prax.branch
		print exp.export(with_metadata = True)
	#---------------------------------------
	#test_export_items()
	test_export_area()

	sys.exit(0)

#============================================================
# CDROM "run.bat":
#
#@echo off
#
#if defined ProgramFiles(x86) (
#    ::64-bit
#    start /B x64\mdicom.exe /scan .
#) else (
#    ::32-bit
#    start /B win32\mdicom.exe /scan .
#)
#
#--------------------------------------------------
