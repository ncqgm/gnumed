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

PRINT_JOB_DESIGNATION = 'print'

#============================================================
# export area item handling
#------------------------------------------------------------
_SQL_get_export_items = "SELECT * FROM clin.v_export_items WHERE %s"

class cExportItem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents an item in the export area table"""

	_cmd_fetch_payload = _SQL_get_export_items % "pk_export_item = %s"
	_cmds_store_payload = [
		"""UPDATE clin.export_item SET
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
		_SQL_get_export_items % 'pk_export_item = %(pk_export_item)s'
	]
	_updatable_fields = [
		'pk_identity',
		'created_when',
		'designation',
		'description',
		'pk_doc_obj',
		'filename'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None, link_obj=None):
		super(cExportItem, self).__init__(aPK_obj = aPK_obj, row = row, link_obj = link_obj)
		# force auto-healing if need be
		if self._payload[self._idx['pk_identity_raw_needs_update']]:
			_log.warning (
				'auto-healing export item [%s] from identity [%s] to [%s] because of document part [%s] seems necessary',
				self._payload[self._idx['pk_export_item']],
				self._payload[self._idx['pk_identity_raw']],
				self._payload[self._idx['pk_identity']],
				self._payload[self._idx['pk_doc_obj']]
			)
			if self._payload[self._idx['pk_doc_obj']] is None:
				_log.error('however, .fk_doc_obj is NULL, which should not happen, leaving things alone for manual inspection')
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

		cmd = """
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
				'cmd': 'SELECT substring(data from %(start)s for %(size)s) FROM clin.export_item WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['size']]
		)
		if not success:
			return None

		if filename.endswith('.dat'):
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
			patient_part = '-%s' % patient.subdir_name

		# preserve original filename extension if available
		suffix = '.dat'
		if self._payload[self._idx['filename']] is not None:
			tmp, suffix = os.path.splitext (
				gmTools.fname_sanitize(self._payload[self._idx['filename']]).lower()
			)
			if suffix == '':
				suffix = '.dat'

		fname = gmTools.get_unique_filename (
			prefix = 'gm-export_item%s-' % patient_part,
			suffix = suffix,
			tmp_dir = directory
		)

		return fname

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
		where_parts.append('pk_identity = %(pat)s')
		# note that invalidly linked items will be
		# auto-healed when instantiated
	if designation is None:
		where_parts.append("designation IS DISTINCT FROM %(desig)s")
	else:
		where_parts.append('designation = %(desig)s')

	if order_by is None:
		order_by = ''
	else:
		order_by = ' ORDER BY %s' % order_by

	cmd = (_SQL_get_export_items % ' AND '.join(where_parts)) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'}) for r in rows ]

#------------------------------------------------------------
def get_print_jobs(order_by=None, pk_identity=None):
	return get_export_items(order_by = order_by, pk_identity = pk_identity, designation = PRINT_JOB_DESIGNATION)

#------------------------------------------------------------
def create_export_item(description=None, pk_identity=None, pk_doc_obj=None, filename=None):

	args = {
		'desc': description,
		'pk_obj': pk_doc_obj,
		'pk_pat': pk_identity,
		'fname': filename
	}
	cmd = """
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
	cmd = "DELETE FROM clin.export_item WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
_html_start = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<link rel="icon" type="image/x-icon" href="gnumed.ico">
<title>%(html_title_header)s %(html_title_patient)s</title>
</head>
<body>

<h1>%(title)s</h1>

<h2>Patient</h2>

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

_html_list_item = """	<li><a href="documents/%s">%s</a></li>
"""

_html_end = """
</ul>

<p>
%(date)s<br>
</p>

<h2>Praxis</h2>

<p>
%(branch)s @ %(praxis)s
%(adr)s
</p>

<p>(<a href="http://www.gnumed.de">GNUmed</a> version %(gm_ver)s)</p>

</body>
</html>
"""


_autorun_inf = (							# needs \r\n for Windows
	'[AutoRun.Amd64]\r\n'					# 64 bit
	'label=%(label)s\r\n'					# patient name/DOB
	'shellexecute=index.html\r\n'
	'action=%(action)s\r\n'				# % _('Browse patient data')
	'%(icon)s\r\n'							# "icon=gnumed.ico" or ""
	'UseAutoPlay=1\r\n'
	'\r\n'
	'[AutoRun]\r\n'						# 32 bit
	'label=%(label)s\r\n'					# patient name/DOB
	'shellexecute=index.html\r\n'
	'action=%(action)s\r\n'				# % _('Browse patient data')
	'%(icon)s\r\n'							# "icon=gnumed.ico" or ""
	'UseAutoPlay=1\r\n'
	'\r\n'
	'[Content]\r\n'
	'PictureFiles=yes\r\n'
	'VideoFiles=yes\r\n'
	'MusicFiles=no\r\n'
	'\r\n'
	'[IgnoreContentPaths]\r\n'
	'\documents\r\n'
	'\r\n'
	'[unused]\r\n'
	'open=requires explicit executable\r\n'
)


_cd_inf = (
'[Patient Info]\r\n'					# needs \r\n for Windows
'PatientName=%s, %s\r\n'
'Gender=%s\r\n'
'BirthDate=%s\r\n'
'CreationDate=%s\r\n'
'PID=%s\r\n'
'EMR=GNUmed\r\n'
'Version=%s\r\n'
'#StudyDate=\r\n'
'#VNRInfo=<body part>\r\n'
'\r\n'
'# name format: lastnames, firstnames\r\n'
'# date format: YYYY-MM-DD (ISO 8601)\r\n'
'# gender format: %s\r\n'
)

_README = """This is a patient data bundle created by the GNUmed Electronic Medical Record.

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
			item['description'] = _('form: %s %s (%s)') % (form.template['name_long'], form.template['external_version'], fname)
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
			description = '%s: %s (%s/)' % (
				gmTools.coalesce(hint, _('file'), '%s'),
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
			doc_tag = _('%s (%s)%s') % (
				doc['l10n_type'],
				gmDateTime.pydt_strftime(doc['clin_when'], '%Y %b %d'),
				gmTools.coalesce(doc['comment'], '', ' "%s"')
			)
			for obj in doc.parts:
				if self.document_part_item_exists(pk_part = obj['pk_obj']):
					continue
				f_ext = ''
				if obj['filename'] is not None:
					f_ext = os.path.splitext(obj['filename'])[1].strip('.').strip()
				if f_ext != '':
					f_ext = ' .' + f_ext.upper()
				obj_tag = _('part %s (%s%s)%s') % (
					obj['seq_idx'],
					gmTools.size2str(obj['size']),
					f_ext,
					gmTools.coalesce(obj['obj_comment'], '', ' "%s"')
				)
				create_export_item (
					description = '%s - %s' % (doc_tag, obj_tag),
					pk_doc_obj = obj['pk_obj']
				)

	#--------------------------------------------------------
	def document_part_item_exists(self, pk_part=None):
		cmd = "SELECT EXISTS (SELECT 1 FROM clin.export_item WHERE fk_doc_obj = %(pk_obj)s)"
		args = {'pk_obj': pk_part}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	#--------------------------------------------------------
	def md5_exists(self, md5=None, include_document_parts=False):
		where_parts = [
			'pk_identity = %(pat)s',
			'md5_sum = %(md5)s'
		]
		args = {
			'pat': self.__pk_identity,
			'md5': md5
		}

		if not include_document_parts:
			where_parts.append('pk_doc_obj IS NULL')

		cmd = _SQL_get_export_items % ' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			return None

		r = rows[0]
		return cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'})

	#--------------------------------------------------------
	def dump_items_to_disk(self, base_dir=None, items=None):
		if items is None:
			items = self.items

		if len(items) == 0:
			return None

		if base_dir is None:
			from Gnumed.business.gmPerson import cPatient
			pat = cPatient(aPK_obj = self.__pk_identity)
			base_dir = gmTools.mk_sandbox_dir(prefix = 'exp-%s-' % pat.subdir_name)
		_log.debug('dumping export items to: %s', base_dir)

		gmTools.mkdir(base_dir)
		for item in items:
			item.save_to_file(directory = base_dir)
		return base_dir

	#--------------------------------------------------------
	def export(self, base_dir=None, items=None, expand_compressed=False):

		if items is None:
			items = self.items

		if len(items) == 0:
			return None

		media_base_dir = base_dir

		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = self.__pk_identity)
		if media_base_dir is None:
			media_base_dir = gmTools.mk_sandbox_dir(prefix = 'exp-%s-' % pat.subdir_name)
		_log.debug('patient media base dir: %s', media_base_dir)

		doc_dir = os.path.join(media_base_dir, r'documents')
		if os.path.isdir(doc_dir):
			index_existing_docs = True
		else:
			index_existing_docs = False
			gmTools.mkdir(doc_dir)

		_html_start_data = {
			'html_title_header': _('Patient data for'),
			'html_title_patient': gmTools.html_escape_string(pat.get_description_gender(with_nickname = False) + ', ' + _('born') + ' ' + pat.get_formatted_dob('%Y %B %d')),
			'title': _('Patient data excerpt'),
			'pat_name': gmTools.html_escape_string(pat.get_description_gender(with_nickname = False)),
			'pat_dob': gmTools.html_escape_string(_('born') + ' ' + pat.get_formatted_dob('%Y %B %d')),
			'mugshot_url': 'documents/no-such-file.png',
			'mugshot_alt': _('no patient photograph available'),
			'mugshot_title': '',
			'docs_title': _('Documents'),
			'browse_root': _('browse storage medium'),
			'browse_docs': _('browse documents area'),
			'browse_dicomdir': '',
			'run_dicom_viewer': ''
		}

		mugshot = pat.document_folder.latest_mugshot
		if mugshot is not None:
			_html_start_data['mugshot_url'] = mugshot.save_to_file(directory = doc_dir, adjust_extension = True)
			_html_start_data['mugshot_alt'] =_('patient photograph from %s') % gmDateTime.pydt_strftime(mugshot['date_generated'], '%B %Y')
			_html_start_data['mugshot_title'] = gmDateTime.pydt_strftime(mugshot['date_generated'], '%B %Y')

		if 'DICOMDIR' in os.listdir(media_base_dir):
			_html_start_data['browse_dicomdir'] = '<li><a href="./DICOMDIR">%s</a></li>' % _('show DICOMDIR file')
			# copy DWV into target dir
			dwv_src_dir = os.path.join(gmTools.gmPaths().local_base_dir, 'resources', 'dwv4export')
			if not os.path.isdir(dwv_src_dir):
				dwv_src_dir = os.path.join(gmTools.gmPaths().system_app_data_dir, 'resources', 'dwv4export')
			if os.path.isdir(dwv_src_dir):
				dwv_target_dir = os.path.join(media_base_dir, 'dwv')
				gmTools.rmdir(dwv_target_dir)
				try:
					shutil.copytree(dwv_src_dir, dwv_target_dir)
					_html_start_data['run_dicom_viewer'] = '<li><a href="./dwv/viewers/mobile-local/index.html">%s</a></li>' % _('run Radiology Images (DICOM) Viewer')
				except (shutil.Error, OSError):
					_log.exception('cannot include DWV, skipping')

		# index.html
		# - header
		idx_fname = os.path.join(media_base_dir, 'index.html')
		idx_file = io.open(idx_fname, mode = 'wt', encoding = 'utf8')
		idx_file.write(_html_start % _html_start_data)
		# - middle (side effect ! -> exports items into files ...)
		existing_docs = os.listdir(doc_dir)		# get them now, or else we will include the to-be-exported items
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
				gmTools.html_escape_string(_('other: %s') % doc_fname)
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
			lines.append('%s: %s' % (
				comm['l10n_comm_type'],
				comm['url']
			))
		adr = ''
		if len(lines) > 0:
			adr = gmTools.html_escape_string('\n'.join(lines), replace_eol = True, keep_visual_eol = True)
		_html_end_data = {
			'branch': gmTools.html_escape_string(prax['branch']),
			'praxis': gmTools.html_escape_string(prax['praxis']),
			'date' : gmTools.html_escape_string(gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y %B %d')),
			'gm_ver': gmTools.html_escape_string(gmTools.coalesce(_cfg.get(option = 'client_version'), 'git HEAD')),
			'adr': adr
		}
		idx_file.write(_html_end % _html_end_data)
		idx_file.close()

		# start.html (just a copy of index.html, really ;-)
		start_fname = os.path.join(media_base_dir, 'start.html')
		try:
			shutil.copy2(idx_fname, start_fname)
		except Exception:
			_log.exception('cannot copy %s to %s', idx_fname, start_fname)

		# autorun.inf
		autorun_dict = {}
		autorun_dict['label'] = self._compute_autorun_inf_label(pat)
		autorun_dict['action'] = _('Browse patient data')
		autorun_dict['icon'] = ''
		media_icon_kwd = '$$gnumed_patient_media_export_icon'
		media_icon_kwd_exp = gmKeywordExpansion.get_expansion (
			keyword = media_icon_kwd,
			textual_only = False,
			binary_only = True
		)
		icon_tmp_file = media_icon_kwd_exp.save_to_file (
			target_mime = 'image/x-icon',
			target_extension = '.ico',
			ignore_conversion_problems = True
		)
		if icon_tmp_file is None:
			_log.debug('cannot retrieve <%s>', media_icon_kwd)
		else:
			media_icon_fname = os.path.join(media_base_dir, 'gnumed.ico')
			try:
				shutil.move(icon_tmp_file, media_icon_fname)
				autorun_dict['icon'] = 'icon=gnumed.ico'
			except Exception:
				_log.exception('cannot move %s to %s', icon_tmp_file, media_icon_fname)
		autorun_fname = os.path.join(media_base_dir, 'AUTORUN.INF')
		autorun_file = io.open(autorun_fname, mode = 'wt', encoding = 'cp1252', errors = 'replace')
		autorun_file.write(_autorun_inf % autorun_dict)
		autorun_file.close()

		# cd.inf
		cd_inf_fname = os.path.join(media_base_dir, 'CD.INF')
		cd_inf_file = io.open(cd_inf_fname, mode = 'wt', encoding = 'utf8')
		cd_inf_file.write(_cd_inf % (
			pat['lastnames'],
			pat['firstnames'],
			gmTools.coalesce(pat['gender'], '?'),
			pat.get_formatted_dob('%Y-%m-%d'),
			gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y-%m-%d'),
			pat.ID,
			_cfg.get(option = 'client_version'),
			' / '.join([ '%s = %s (%s)' % (g['tag'], g['label'], g['l10n_label']) for g in pat.gender_list ])
		))
		cd_inf_file.close()

		# README
		readme_fname = os.path.join(media_base_dir, 'README')
		readme_file = io.open(readme_fname, mode = 'wt', encoding = 'utf8')
		readme_file.write(_README % (
			pat.get_description_gender(with_nickname = False) + ', ' + _('born') + ' ' + pat.get_formatted_dob('%Y %B %d')
		))
		readme_file.close()

		# patient demographics as GDT/XML/VCF/MCF
		pat.export_as_gdt(filename = os.path.join(media_base_dir, 'patient.gdt'))
		pat.export_as_xml_linuxmednews(filename = os.path.join(media_base_dir, 'patient.xml'))
		pat.export_as_vcard(filename = os.path.join(media_base_dir, 'patient.vcf'))
		pat.export_as_mecard(filename = os.path.join(media_base_dir, u'patient.mcf'))

		# praxis VCF/MCF
		shutil.move(prax.vcf, os.path.join(media_base_dir, 'praxis.vcf'))
		prax.export_as_mecard(filename = os.path.join(media_base_dir, u'praxis.mcf'))

		return media_base_dir

	#--------------------------------------------------------
	def _compute_autorun_inf_label(self, patient):
		LABEL_MAX_LEN = 32
		dob = patient.get_formatted_dob(format = ' %Y%m%d', none_string = '', honor_estimation = False)
		if dob == '':
			gender_template = ' (%s)'
		else:
			gender_template = ' %s'
		gender = gmTools.coalesce(patient['gender'], '', gender_template)
		name_max_len = LABEL_MAX_LEN - len(gender) - len(dob)			# they already include appropriate padding
		name = patient.active_name
		last = name['lastnames'].strip()
		first = name['firstnames'].strip()
		len_last = len(last)
		len_first = len(first)
		while (len_last + len_first + 1) > name_max_len:
			if len_first > 6:
				len_first -= 1
				if first[len_first - 1] == ' ':
					len_first -= 1
				continue
			len_last -= 1
			if last[len_last - 1] == ' ':
				len_last -= 1
		last = last[:len_last].strip().upper()
		first = first[:len_first].strip()
		# max 32 chars, supposedly ASCII, but CP1252 likely works pretty well
		label = (('%s %s%s%s' % (last, first, dob,	gender)).strip())[:32]
		return label

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def get_items(self, designation=None, order_by='designation, description'):
		return get_export_items(order_by = order_by, pk_identity = self.__pk_identity, designation = designation)

	items = property(get_items, lambda x:x)
	#--------------------------------------------------------
	def get_printouts(self, order_by='designation, description'):
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
		create_export_item(description = 'description %s' % random.random(), pk_identity = 12, pk_doc_obj = None, filename = 'dummy.dat')
		items = get_export_items()
		for item in items:
			print(item.format())
		item['pk_doc_obj'] = 1
		item.save()
		print(item)

	#---------------------------------------
	def test_export_area():
		exp = cExportArea(12)
		#print exp.export_with_meta_data()
		#print exp.items
		exp.add_file(sys.argv[2])
		prax = gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.cPraxisBranch(1))
		print(prax)
		print(prax.branch)
		print(exp.export())

	#---------------------------------------
	def test_label():

		from Gnumed.business.gmPerson import cPatient
		from Gnumed.business.gmPersonSearch import ask_for_patient

		#while ask_for_patient() is not None:
		pat_min = 1
		pat_max = 100
		try:
			pat_min = int(sys.argv[2])
			pat_max = int(sys.argv[3])
		except:
			pass
		cPatient(aPK_obj = pat_min)
		f = io.open('x-auto_inf_labels.txt', mode = 'w', encoding = 'utf8')
		f.write('--------------------------------\n')
		f.write('12345678901234567890123456789012\n')
		f.write('--------------------------------\n')
		for pat_id in range(pat_min, pat_max):
			try:
				exp_area = cExportArea(pat_id)
				pat = cPatient(aPK_obj = pat_id)
			except:
				continue
			f.write(exp_area._compute_autorun_inf_label(pat) + '\n')
		f.close()
		return

	#---------------------------------------
	#test_export_items()
	test_export_area()
	#test_label()

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
