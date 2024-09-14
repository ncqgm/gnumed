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
import platform


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
from Gnumed.pycommon import gmCrypto

from Gnumed.business import gmDocuments
from Gnumed.business import gmKeywordExpansion


_log = logging.getLogger('gm.exp_area')
_cfg = gmCfg2.gmCfgData()

PRINT_JOB_DESIGNATION = 'print'
DOCUMENTS_SUBDIR = 'documents'
DIRENTRY_README_NAME = '.README.GNUmed-DIRENTRY'

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
	def update_data(self, data=None):
		assert (data is not None), '<data> must not be <None>'

		SQL = """
			UPDATE clin.export_item SET
				data = %(data)s::bytea,
				fk_doc_obj = NULL
			WHERE pk = %(pk)s"""
		args = {'pk': self.pk_obj, 'data': data}
		gmPG2.run_rw_queries(queries = [{'cmd': SQL, 'args': args}], return_data = False, get_col_idx = False)
		# must update XMIN now ...
		self.refetch_payload()
		return True

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
	def save_to_file(self, aChunkSize:int=0, filename:str=None, directory:str=None, passphrase:str=None, convert2pdf:bool=False) -> str:
		"""Save this entry to disk.

		Args:
			filename: The filename to save into, unless this is a DIRENTRY.
			directory: The directory to save the DIRENTRY _content into, if this is a DIRENTRY.
			passphrase: Encrypt file(s) with this passphrase, if not _None_.
			convert2pdf: Convert file(s) to PDF on the way out. Before encryption, that is.

		Returns:
			Directory for DIRENTRIES, or filename.
		"""
		if self.is_DIRENTRY and convert2pdf:
			# cannot convert dir entries to PDF
			return None

		# data linked from archive ?
		part_fname = self.__save_doc_obj (
			filename = filename,
			directory = directory,
			passphrase = passphrase,
			convert2pdf = convert2pdf
		)
		if part_fname is False:
			return None

		if part_fname is not None:
			return part_fname

		# valid DIRENTRY ?
		if self.is_valid_DIRENTRY:
			target_dir = self.__save_direntry (
				directory,
				passphrase = passphrase
			)
			if target_dir is False:
				return None

			if target_dir is not None:
				return target_dir

		# but still a DIRENTRY ?
		if self.is_DIRENTRY:
			# yes, but apparently not valid (anymore), say,
			# other machine or dir not found locally
			return None

		# normal item with data in export area table
		return self.__save_normal_item (
			filename = filename,
			directory = directory,
			passphrase = passphrase,
			convert2pdf = convert2pdf
		)

	#--------------------------------------------------------
	def display_via_mime(self, chunksize=0, block=None):

		# document part
		if self._payload[self._idx['pk_doc_obj']] is not None:
			return self.document_part.display_via_mime(chunksize = chunksize, block = block)

		# DIR entry
		if self._payload[self._idx['filename']].startswith('DIR::'):
			# FIXME: error handling with malformed entries
			tag, node, path = self._payload[self._idx['filename']].split('::', 2)
			if node != platform.node():
				msg = _(
					'This item points to a directory on the computer named:\n'
					' %s\n'
					'You are, however, currently using another computer:\n'
					' %s\n'
					'Directory items can only be viewed/saved/exported\n'
					'on the computer they are pointing to.'
				) % (node, platform.node())
				return False, msg
			success, msg = gmMimeLib.call_viewer_on_file(path, block = block)
			return success, msg

		# data -> save
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
	# helpers
	#--------------------------------------------------------
	def __save_normal_item(self, filename:str=None, directory:str=None, passphrase:str=None, convert2pdf:bool=False) -> str:
		if filename is None:
			filename = self.get_useful_filename(directory = directory)
		success = gmPG2.bytea2file (
			data_query = {
				'cmd': 'SELECT substring(data from %(start)s for %(size)s) FROM clin.export_item WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			data_size = self._payload[self._idx['size']]
		)
		if not success:
			return None

		filename = gmMimeLib.adjust_extension_by_mimetype(filename)
		if passphrase is None:
			return filename

		enc_filename = gmCrypto.encrypt_file (
			filename = filename,
			passphrase = passphrase,
			verbose = _cfg.get(option = 'debug'),
			remove_unencrypted = True,
			convert2pdf = convert2pdf
		)
		removed = gmTools.remove_file(filename)
		if enc_filename is None:
			_log.error('cannot encrypt or, possibly, convert')
			return None

		if removed:
			return enc_filename

		_log.error('cannot remove unencrypted file')
		gmTools.remove(enc_filename)
		return None

	#--------------------------------------------------------
	def __save_doc_obj(self, filename=None, directory=None, passphrase=None, convert2pdf:bool=False):
		"""Save doc object part into target.

		None: not a doc obj
		True: success
		False: failure (to save/convert/encrypt/remove unencrypted)
		"""
		if self._payload[self._idx['pk_doc_obj']] is None:
			return None

		part = self.document_part
		if filename is None:
			filename = part.get_useful_filename (
				make_unique = False,
				directory = directory,
				include_gnumed_tag = False,
				date_before_type = True,
				name_first = False
			)
		if convert2pdf:
			target_mime = 'application/pdf'
			target_ext = '.pdf'
		else:
			target_mime = None
			target_ext = None
		part_fname = part.save_to_file (
			filename = filename,
			target_mime = target_mime,
			target_extension = target_ext,
			ignore_conversion_problems = False
		)
		if part_fname is None:
			_log.error('cannot save document part to file')
			return False

		if passphrase is None:
			return part_fname

		enc_filename = gmCrypto.encrypt_file (
			filename = part_fname,
			passphrase = passphrase,
			verbose = _cfg.get(option = 'debug'),
			remove_unencrypted = True
		)
		removed = gmTools.remove_file(part_fname)
		if enc_filename is None:
			_log.error('cannot encrypt')
			return False

		if removed:
			return enc_filename

		_log.error('cannot remove unencrypted file')
		gmTools.remove(enc_filename)
		return False

	#--------------------------------------------------------
	def __save_direntry(self, directory=None, passphrase=None):
		"""Move DIRENTRY source into target.

		None: not a DIRENTRY
		True: success
		False: failure
		"""
		# do not process malformed entries
		try:
			tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		except ValueError:
			_log.exception('malformed DIRENTRY: [%s]', self._payload[self._idx['filename']])
			return False
		# source and target paths must not overlap
		if directory is None:
			directory = gmTools.mk_sandbox_dir(prefix = 'exp-')
		if directory.startswith(local_fs_path):
			_log.error('cannot dump DIRENTRY item [%s]: must not be subdirectory of target dir [%s]', self._payload[self._idx['filename']], directory)
			return False
		if local_fs_path.startswith(directory):
			_log.error('cannot dump DIRENTRY item [%s]: target dir [%s] must not be subdirectory of DIRENTRY', self._payload[self._idx['filename']], directory)
			return False

		_log.debug('dumping DIRENTRY item [%s] into [%s]', self._payload[self._idx['filename']], directory)
		sandbox_dir = gmTools.mk_sandbox_dir()
		_log.debug('sandbox: %s', sandbox_dir)
		tmp = gmTools.copy_tree_content(local_fs_path, sandbox_dir)
		if tmp is None:
			_log.error('cannot dump DIRENTRY item [%s] into [%s]: copy error', self._payload[self._idx['filename']], sandbox_dir)
			return False

		gmTools.remove_file(os.path.join(tmp, DIRENTRY_README_NAME))
		if passphrase is not None:
			_log.debug('encrypting sandbox: %s', sandbox_dir)
			encrypted = gmCrypto.encrypt_directory_content (
				directory = sandbox_dir,
				passphrase = passphrase,
				verbose = _cfg.get(option = 'debug'),
				remove_unencrypted = True
			)
			if not encrypted:
				_log.error('cannot dump DIRENTRY item [%s]: encryption problem in [%s]', self._payload[self._idx['filename']], sandbox_dir)
				return False

		tmp = gmTools.copy_tree_content(sandbox_dir, directory)
		if tmp is None:
			_log.debug('cannot dump DIRENTRY item [%s] into [%s]: copy error', self._payload[self._idx['filename']], directory)
			return False

		return directory

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

	#--------------------------------------------------------
	def _is_DIRENTRY(self):
		"""Check whether this item looks like a DIRENTRY."""
		if self._payload[self._idx['filename']] is None:
			return False
		if not self._payload[self._idx['filename']].startswith('DIR::'):
			return False
		if len(self._payload[self._idx['filename']].split('::', 2)) != 3:
			_log.exception('DIRENTRY [%s]: malformed', self._payload[self._idx['filename']])
			return False
		return True

	is_DIRENTRY = property(_is_DIRENTRY)

	#--------------------------------------------------------
	def _is_local_DIRENTRY(self):
		"""Check whether this item is a _local_ DIRENTRY."""
		if not self.is_DIRENTRY:
			return False

		tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		if node == platform.node():
			return True

		_log.warning('DIRENTRY [%s]: not on this machine (%s)', self._payload[self._idx['filename']], platform.node())
		return False

	is_local_DIRENTRY = property(_is_local_DIRENTRY)

	#--------------------------------------------------------
	def _is_valid_DIRENTRY(self):
		"""Check whether this item is a _valid_ DIRENTRY."""
		if not self.is_local_DIRENTRY:
			return False

		tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		# valid path ?
		if not os.path.isdir(local_fs_path):
			_log.warning('DIRENTRY [%s]: directory not found (old DIRENTRY ?)', self._payload[self._idx['filename']])
			return False
		return True

	is_valid_DIRENTRY = property(_is_valid_DIRENTRY)

	#--------------------------------------------------------
	def _get_DIRENTRY_node(self):
		if not self.is_DIRENTRY:
			return None

		try:
			tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		except ValueError:
			# should not happen because structure already checked in .is_DIRENTRY,
			# better safe than sorry
			_log.exception('DIRENTRY [%s]: malformed', self._payload[self._idx['filename']])
			return None

		return node

	DIRENTRY_node = property(_get_DIRENTRY_node)

	#--------------------------------------------------------
	def _get_DIRENTRY_path(self):
		if not self.is_DIRENTRY:
			return None

		try:
			tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		except ValueError:
			# should not happen because structure already checked in .is_DIRENTRY,
			# better safe than sorry
			_log.exception('DIRENTRY [%s]: malformed', self._payload[self._idx['filename']])
			return None

		return local_fs_path

	DIRENTRY_path = property(_get_DIRENTRY_path)

	#--------------------------------------------------------
	def _is_DICOM_directory(self):
		"""Check whether this item points to a DICOMDIR."""
		if not self.is_valid_DIRENTRY:
			return False

		tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		found_DICOMDIR = False
		for fs_entry in os.listdir(local_fs_path):
			# found a subdir
			if os.path.isdir(os.path.join(local_fs_path, fs_entry)):
				# allow for any number of subdirs
				continue
			# found a file
			if fs_entry != 'DICOMDIR':
				# not named "DICOMDIR" -> not a DICOMDIR DIRENTRY
				return False

			# must be named DICOMDIR -> that's the only file allowed (and required) in ./
			found_DICOMDIR = True
		return found_DICOMDIR

	is_DICOM_directory = property(_is_DICOM_directory)

	#--------------------------------------------------------
	def _has_files_in_root(self):
		"""True if there are files in the root directory."""
		tag, node, local_fs_path = self._payload[self._idx['filename']].split('::', 2)
		for fs_entry in os.listdir(local_fs_path):
			if os.path.isfile(fs_entry):
				_log.debug('has files in top level: %s', local_fs_path)
				return True
		return False

	has_files_in_root = property(_has_files_in_root)

#------------------------------------------------------------
def get_export_items(order_by=None, pk_identity=None, designation=None, return_pks=False):

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
	if return_pks:
		return [ r['pk_export_item'] for r in rows ]
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
_FRONTPAGE_HTML_CONTENT = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
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
(%(date)s)<br>
</p>

<h2><a href="patient.vcf">Patient</a></h2>

<p>
	%(pat_name)s<br>
	%(pat_dob)s
</p>

<p><img src="%(mugshot_url)s" alt="%(mugshot_alt)s" title="%(mugshot_title)s" width="200" border="2"></p>

<h2>%(docs_title)s</h2>

<ul>
	<li><a href="./">%(browse_root)s</a></li>
	<li><a href="%(doc_subdir)s/">%(browse_docs)s</a></li>
	%(browse_dicomdir)s
	%(run_dicom_viewer)s
</ul>

<ul>
%(docs_list)s
</ul>

<h2><a href="praxis.vcf">Praxis</a></h2>

<p>
%(branch)s @ %(praxis)s
%(adr)s
</p>

<p>(<a href="http://www.gnumed.de">GNUmed</a> version %(gm_ver)s)</p>

</body>
</html>
"""

_INDEX_HTML_CONTENT = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<link rel="icon" type="image/x-icon" href="gnumed.ico">
<title>%(html_title_header)s</title>
</head>
<body>

<h1>%(title)s</h1>

<p>
(%(date)s)<br>
</p>

This is an encrypted patient data excerpt created by the GNUmed Electronic Medical Record.

<p>
For decryption you will need to

<ul>
	<li>install decryption software and</li>
	<li>obtain relevant passwords from the creator or holder of this media</li>
</ul>

<h2>Decryption software</h2>

For files ending in

<ul>
	<li>.asc: install <a href="https://gnupg.org">GNU Privacy Guard</a></li>
	<li>.7z: install <a href="https://www.7-zip.org">7-zip</a> or <a href="https://www.winzip.com">WinZip</a></li>
</ul>


<h2>%(docs_title)s</h2>

<ul>
	<li><a href="./frontpage.html">front page (after decryption)</a></li>
	<li><a href="./%(frontpage_fname)s">front page (if decryption from browser is supported)</a></li>

	<li><a href="./">%(browse_root)s</a></li>
	<li><a href="%(doc_subdir)s/">%(browse_docs)s</a></li>
</ul>


<h2><a href="praxis.vcf">Praxis</a></h2>

<p>
%(branch)s @ %(praxis)s
%(adr)s
</p>

<p>(<a href="http://www.gnumed.de">GNUmed</a> version %(gm_ver)s)</p>

</body>
</html>
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
	def add_path(self, path, comment=None):
		"""Add a DIR entry to the export area.

		This sort of entry points to a certain directory on a
		certain machine. The content of the the directory
		will be included in exports, the directory *itself*
		will not. For *that*, use a disposable top-level
		directory into which you put the directory to include
		as a subdirectory.
		"""
		assert (os.path.isdir(path)), '<path> must exist: %s' % path

		path_item_data = 'DIR::%s::%s/' % (platform.node(), path.rstrip('/'))
		_log.debug('attempting to add path item [%s]', path_item_data)
		item = self.path_item_exists(path_item_data)
		if item is not None:
			_log.debug('[%s] already in export area', path)
			return item

		if comment is None:
			comment = _('path [%s/] on computer "%s"') % (
				path.rstrip('/'),
				platform.node()
			)
		else:
			comment += _(' (on "%s")') % platform.node()

		item = create_export_item (
			description = comment,
			pk_identity = self.__pk_identity,
			filename = path_item_data
		)
		try:
			README = open(os.path.join(path, DIRENTRY_README_NAME), mode = 'wt', encoding = 'utf8')
			README.write('GNUmed DIRENTRY information\n')
			README.write('created: %s\n' % gmDateTime.pydt_now_here())
			README.write('machine: %s\n' % platform.node())
			README.write('path: %s\n' % path)
			README.close()
		except OSError:
			_log.exception('READONLY DIRENTRY [%s]', path)

		return item

	#--------------------------------------------------------
	def path_item_exists(self, path_item_data):

		assert (path_item_data.startswith('DIR::')), 'invalid <path_item_data> [%s]' % path_item_data

		where_parts = [
			'pk_identity = %(pat)s',
			'filename = %(fname)s',
			'pk_doc_obj IS NULL'
		]
		args = {
			'pat': self.__pk_identity,
			'fname': path_item_data
		}
		SQL = _SQL_get_export_items % ' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': SQL, 'args': args}], get_col_idx = True)
		if len(rows) == 0:
			return None

		r = rows[0]
		return cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'})

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

		# failed to insert data, hence remove export item entry
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
	def remove_item(self, item):
		if item.is_valid_DIRENTRY:
			gmTools.remove_file(os.path.join(item.DIRENTRY_path, DIRENTRY_README_NAME))
		return delete_export_item(pk_export_item = item['pk_export_item'])

	#--------------------------------------------------------
	def dump_items_to_disk(self, base_dir=None, items=None, passphrase=None, convert2pdf=False):
		if items is None:
			items = self.items
		if len(items) == 0:
			return None

		if base_dir is None:
			from Gnumed.business.gmPerson import cPatient
			pat = cPatient(aPK_obj = self.__pk_identity)
			base_dir = os.path.join(gmTools.mk_sandbox_dir(), pat.subdir_name)
		gmTools.mkdir(base_dir)
		_log.debug('dumping export items to: %s', base_dir)
		for item in items:
			if item.save_to_file(directory = base_dir, passphrase = passphrase, convert2pdf = convert2pdf) is None:
				return None

		return base_dir

	#--------------------------------------------------------
	def dump_items_to_disk_as_zip(self, base_dir=None, items=None, passphrase=None):
		_log.debug('target dir: %s', base_dir)
		dump_dir = self.dump_items_to_disk(base_dir = base_dir, items = items)
		if dump_dir is None:
			_log.error('cannot dump export area items')
			return None
		zip_file = gmTools.create_zip_archive_from_dir (
			dump_dir,
			comment = _('GNUmed Patient Media'),
			overwrite = True,
			passphrase = passphrase,
			verbose = _cfg.get(option = 'debug')
		)
		if zip_file is None:
			_log.error('cannot zip export area items dump')
			return None
		return zip_file

	#--------------------------------------------------------
	def export(self, base_dir=None, items=None, passphrase=None):

		if items is None:
			items = self.items
		if len(items) == 0:
			return None

		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = self.__pk_identity)
		target_base_dir = base_dir
		if target_base_dir is None:
			target_sandbox_dir = gmTools.mk_sandbox_dir()
			target_base_dir = os.path.join(target_sandbox_dir, pat.subdir_name)
		gmTools.mkdir(target_base_dir)
		_log.debug('patient media base dir: %s', target_base_dir)
		if not gmTools.dir_is_empty(target_base_dir):
			_log.error('patient media base dir is not empty')
			return False

		from Gnumed.business.gmPraxis import gmCurrentPraxisBranch
		prax = gmCurrentPraxisBranch()

		html_data = {}

		# 1) assemble everything into a sandbox
		# - setup sandbox
		sandbox_dir = gmTools.mk_sandbox_dir()
		_log.debug('sandbox dir: %s', sandbox_dir)
		doc_dir = os.path.join(sandbox_dir, DOCUMENTS_SUBDIR)
		gmTools.mkdir(doc_dir)
		# - export mugshot
		mugshot = pat.document_folder.latest_mugshot
		if mugshot is not None:
			mugshot_fname = mugshot.save_to_file(directory = doc_dir)
			fname = os.path.split(mugshot_fname)[1]
			html_data['mugshot_url'] = os.path.join(DOCUMENTS_SUBDIR, fname)
			html_data['mugshot_alt'] =_('patient photograph from %s') % gmDateTime.pydt_strftime(mugshot['date_generated'], '%B %Y')
			html_data['mugshot_title'] = gmDateTime.pydt_strftime(mugshot['date_generated'], '%B %Y')
		# - export patient demographics as GDT/XML/VCF/MCF
		pat.export_as_gdt(filename = os.path.join(sandbox_dir, 'patient.gdt'))
		pat.export_as_xml_linuxmednews(filename = os.path.join(sandbox_dir, 'patient.xml'))
		pat.export_as_vcard(filename = os.path.join(sandbox_dir, 'patient.vcf'))
		pat.export_as_mecard(filename = os.path.join(sandbox_dir, 'patient.mcf'))
		# - create CD.INF
		self._create_cd_inf(pat, sandbox_dir)
		# - export items
		docs_list = []
		for item in items:
			# if it is a dicomdir - put it into the root of the target media
			if item.is_DICOM_directory:
				_log.debug('exporting DICOMDIR DIRENTRY')
				# save into base dir
				item_fname = item.save_to_file(directory = sandbox_dir)
				# do not include into ./documents/ listing
				continue
			if item.is_valid_DIRENTRY:
				_log.debug('exporting DIRENTRY')
				# if there are files in the root dir: put it into a
				# subdir of ./documents/ where subdir is the leaf
				# of the the item .filename
				if item.has_files_in_root:
					tag, node, local_fs_path = item['filename'].split('::', 2)
					subdir = local_fs_path.rstrip('/').split('/')[-1]
					subdir = os.path.join(doc_dir, subdir)
					gmTools.mkdir(subdir)
					item_fname = item.save_to_file(directory = subdir)
				# if it is subdirs only - put it into documents/ directly
				else:
					item_fname = item.save_to_file(directory = doc_dir)
				# include into ./documents/ listing
				fname = os.path.split(item_fname)[1]
				docs_list.append([fname, gmTools.html_escape_string(item['description'])])
				continue
			if item.is_DIRENTRY:
				# DIRENTRY but not valid: skip
				continue
			# normal entry, doc obj links or data item
			item_fname = item.save_to_file(directory = doc_dir)
			fname = os.path.split(item_fname)[1]
			# collect items so we can later correlate items and descriptions
			# actually we should link to encrypted items, and to unencrypted ones
			docs_list.append([fname, gmTools.html_escape_string(item['description'])])
		# - link to DICOMDIR if exists
		if 'DICOMDIR' in os.listdir(sandbox_dir):	# in root path
			has_dicomdir = True
			html_data['browse_dicomdir'] = '<li><a href="./DICOMDIR">%s</a></li>' % _('show DICOMDIR file')
		else:
			has_dicomdir = False
		# - include DWV link if there is a DICOMDIR
		if has_dicomdir:
			# do not clone into media base to avoid encryption,
			# DWV will be cloned to there later on
			dwv_sandbox_dir = self._clone_dwv()
			if dwv_sandbox_dir is not None:
				html_data['run_dicom_viewer'] = '<li><a href="./dwv/viewers/mobile-local/index.html">%s</a></li>' % _('run Radiology Images (DICOM) Viewer')
		# - create frontpage.html
		frontpage_fname = self._create_frontpage_html(pat, prax, sandbox_dir, html_data, docs_list)
		# - start.html (just a convenience copy of frontpage.html)
		#   (later overwritten, if encryption is requested)
		start_fname = os.path.join(sandbox_dir, 'start.html')
		try:
			shutil.copy2(frontpage_fname, start_fname)
		except Exception:
			_log.exception('cannot copy %s to %s', frontpage_fname, start_fname)
		# - index.html (just a convenience copy of frontpage.html)
		#   (later overwritten if encryption is requested)
		index_fname = os.path.join(sandbox_dir, 'index.html')
		try:
			shutil.copy2(frontpage_fname, index_fname)
		except Exception:
			_log.exception('cannot copy %s to %s', frontpage_fname, index_fname)

		# 2) encrypt content of sandbox
		if passphrase is not None:
			encrypted = gmCrypto.encrypt_directory_content (
				directory = sandbox_dir,
				receiver_key_ids = None,
				passphrase = passphrase,
				comment = None,
				verbose = _cfg.get(option = 'debug'),
				remove_unencrypted = True
			)
			if not encrypted:
				_log.errror('cannot encrypt data in sandbox dir')
				return False

		# 3) add never-to-be-encrypted data
		# - AUTORUN.INF
		# - README
		if passphrase is None:
			self._create_autorun_inf(pat, sandbox_dir)
			self._create_readme(pat, sandbox_dir)
		else:
			self._create_autorun_inf(None, sandbox_dir)
			self._create_readme(None, sandbox_dir)
		# - praxis VCF/MCF
		shutil.move(prax.vcf, os.path.join(sandbox_dir, 'praxis.vcf'))
		prax.export_as_mecard(filename = os.path.join(sandbox_dir, u'praxis.mcf'))
		# - include DWV code
		if has_dicomdir:
			self._clone_dwv(target_dir = sandbox_dir)
		# - index.html as boilerplate for decryption
		if passphrase is not None:
			index_fname = self._create_index_html(prax, sandbox_dir, html_data)

		# 4) move sandbox to target dir
		target_dir = gmTools.copy_tree_content(sandbox_dir, target_base_dir)
		if target_dir is None:
			_log.error('cannot fill target base dir')
			return False

		return target_dir

	#--------------------------------------------------------
	def export_as_zip(self, base_dir=None, items=None, passphrase=None):
		_log.debug('target dir: %s', base_dir)
		export_dir = self.export(base_dir = base_dir, items = items)
		if export_dir is None:
			_log.debug('cannot export items')
			return None

		if passphrase is None:
			zip_file = gmCrypto.create_zip_archive_from_dir (
				export_dir,
				comment = _('GNUmed Patient Media'),
				overwrite = True,
				verbose = _cfg.get(option = 'debug')
			)
		else:
			zip_file = gmCrypto.create_encrypted_zip_archive_from_dir (
				export_dir,
				comment = _('GNUmed Patient Media'),
				overwrite = True,
				passphrase = passphrase,
				verbose = _cfg.get(option = 'debug')
			)
		if zip_file is None:
			_log.debug('cannot create zip archive')
			return None

		return zip_file

	#--------------------------------------------------------
	def _create_index_html(self, praxis, directory, data):
		# header part
		_HTML_data = {
			'html_title_header': _('Patient data'),
			'title': _('Patient data excerpt'),
			'docs_title': _('Documents'),
			'browse_root': _('browse storage medium'),
			'browse_docs': _('browse documents area'),
			'doc_subdir': DOCUMENTS_SUBDIR,
			'date' : gmTools.html_escape_string(gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y %B %d'))
		}
		frontpage_fname_enc = 'frontpage.html.asc'
		if os.path.isfile(os.path.join(directory, frontpage_fname_enc)):
			_HTML_data['frontpage_fname'] = frontpage_fname_enc
		frontpage_fname_enc = 'frontpage.html.7z'
		if os.path.isfile(os.path.join(directory, frontpage_fname_enc)):
			_HTML_data['frontpage_fname'] = frontpage_fname_enc
		# footer part
		lines = []
		adr = praxis.branch.org_unit.address
		if adr is not None:
			lines.extend(adr.format())
		for comm in praxis.branch.org_unit.comm_channels:
			if comm['is_confidential'] is True:
				continue
			lines.append('%s: %s' % (
				comm['l10n_comm_type'],
				comm['url']
			))
		adr = ''
		if len(lines) > 0:
			adr = gmTools.html_escape_string('\n'.join(lines), replace_eol = True, keep_visual_eol = True)
		_HTML_data['branch'] = gmTools.html_escape_string(praxis['branch'])
		_HTML_data['praxis'] = gmTools.html_escape_string(praxis['praxis'])
		_HTML_data['gm_ver'] = gmTools.html_escape_string(gmTools.coalesce(_cfg.get(option = 'client_version'), 'git HEAD'))
		_HTML_data['adr'] = adr
		# create file
		index_fname = os.path.join(directory, 'index.html')
		index_file = io.open(index_fname, mode = 'wt', encoding = 'utf8')
		index_file.write(_INDEX_HTML_CONTENT % _HTML_data)
		index_file.close()
		return index_fname

	#--------------------------------------------------------
	def _create_frontpage_html(self, patient, praxis, directory, data, docs_list):
		# <li><a href="documents/filename-1.ext">document 1 description</a></li>
		_HTML_LIST_ITEM = '	<li><a href="%s">%s</a></li>'
		# header part
		_HTML_data = {
			'html_title_header': _('Patient data for'),
			'html_title_patient': gmTools.html_escape_string(patient.get_description_gender(with_nickname = False) + ', ' + _('born') + ' ' + patient.get_formatted_dob('%Y %B %d')),
			'title': _('Patient data excerpt'),
			'pat_name': gmTools.html_escape_string(patient.get_description_gender(with_nickname = False)),
			'pat_dob': gmTools.html_escape_string(_('born') + ' ' + patient.get_formatted_dob('%Y %B %d')),
			'mugshot_url': 'documents/no-such-file.png',
			'mugshot_alt': _('no patient photograph available'),
			'mugshot_title': '',
			'docs_title': _('Documents'),
			'browse_root': _('browse storage medium'),
			'browse_docs': _('browse documents area'),
			'doc_subdir': DOCUMENTS_SUBDIR,
			'browse_dicomdir': '',
			'run_dicom_viewer': '',
			'date' : gmTools.html_escape_string(gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y %B %d'))
		}
		for key in data:
			_HTML_data[key] = data[key]

		# documents part
		_HTML_docs_list = []
		for doc in docs_list:
			subdir = os.path.join(directory, DOCUMENTS_SUBDIR, doc[0])
			if os.path.isdir(subdir):
				_HTML_docs_list.append(_HTML_LIST_ITEM % (os.path.join(DOCUMENTS_SUBDIR, doc[0]), _('DIRECTORY: %s/%s/') % (DOCUMENTS_SUBDIR, doc[0])))
				_HTML_docs_list.append('	<ul>')
				for fname in os.listdir(subdir):
					tmp = os.path.join(subdir, fname)
					if os.path.isdir(tmp):
						_HTML_docs_list.append('		<li><a href="%s">%s</a></li>' % (os.path.join(DOCUMENTS_SUBDIR, doc[0], fname), _('DIRECTORY: %s/%s/%s/') % (DOCUMENTS_SUBDIR, doc[0], fname)))
					else:
						_HTML_docs_list.append('		<li><a href="%s">%s</a></li>' % (os.path.join(DOCUMENTS_SUBDIR, doc[0], fname), fname))
				_HTML_docs_list.append('	</ul>')
			else:
				_HTML_docs_list.append(_HTML_LIST_ITEM % (os.path.join(DOCUMENTS_SUBDIR, doc[0]), doc[1]))
		_HTML_data['docs_list'] = u'\n	'.join(_HTML_docs_list)

		# footer part
		lines = []
		adr = praxis.branch.org_unit.address
		if adr is not None:
			lines.extend(adr.format())
		for comm in praxis.branch.org_unit.comm_channels:
			if comm['is_confidential'] is True:
				continue
			lines.append('%s: %s' % (
				comm['l10n_comm_type'],
				comm['url']
			))
		adr = ''
		if len(lines) > 0:
			adr = gmTools.html_escape_string('\n'.join(lines), replace_eol = True, keep_visual_eol = True)
		_HTML_data['branch'] = gmTools.html_escape_string(praxis['branch'])
		_HTML_data['praxis'] = gmTools.html_escape_string(praxis['praxis'])
		_HTML_data['gm_ver'] = gmTools.html_escape_string(gmTools.coalesce(_cfg.get(option = 'client_version'), 'git HEAD'))
		_HTML_data['adr'] = adr
		# create file
		frontpage_fname = os.path.join(directory, 'frontpage.html')
		frontpage_file = io.open(frontpage_fname, mode = 'wt', encoding = 'utf8')
		frontpage_file.write(_FRONTPAGE_HTML_CONTENT % _HTML_data)
		frontpage_file.close()
		return frontpage_fname

	#--------------------------------------------------------
	def _clone_dwv(self, target_dir=None):
		_log.debug('cloning dwv')
		# find DWV
		dwv_src_dir = os.path.join(gmTools.gmPaths().local_base_dir, 'resources', 'dwv4export')
		if not os.path.isdir(dwv_src_dir):
			_log.debug('[%s] not found', dwv_src_dir)
			dwv_src_dir = os.path.join(gmTools.gmPaths().system_app_data_dir, 'resources', 'dwv4export')
		if not os.path.isdir(dwv_src_dir):
			_log.debug('[%s] not found', dwv_src_dir)
			return None
		# clone it
		if target_dir is None:
			target_dir = gmTools.mk_sandbox_dir()
		dwv_target_dir = os.path.join(target_dir, 'dwv')
		gmTools.rmdir(dwv_target_dir)
		try:
			shutil.copytree(dwv_src_dir, dwv_target_dir)
		except (shutil.Error, OSError):
			_log.exception('cannot include DWV, skipping')
			return None

		return dwv_target_dir

	#--------------------------------------------------------
	def _create_readme(self, patient, directory):
		_README_CONTENT = (
			'This is a patient data excerpt created by the GNUmed Electronic Medical Record.\n'
			'\n'
			'Patient: %s\n'
			'\n'
			'Please display <frontpage.html> to browse patient data.\n'
			'\n'
			'Individual documents are stored in the subdirectory\n'
			'\n'
			'	documents/\n'
			'\n'
			'\n'
			'Data may need to be decrypted with either GNU Privacy\n'
			'Guard or 7zip/WinZip.\n'
			'\n'
			'.asc:\n'
			'	https://gnupg.org\n'
			'\n'
			'.7z:\n'
			'	https://www.7-zip.org\n'
			'	https://www.winzip.com\n'
			'\n'
			'To obtain any needed keys you will have to get in touch with\n'
			'the creator or the owner of this patient media excerpt.\n'
		)
		readme_fname = os.path.join(directory, 'README')
		readme_file = io.open(readme_fname, mode = 'wt', encoding = 'utf8')
		if patient is None:
			pat_str = _('<protected>')
		else:
			pat_str = patient.get_description_gender(with_nickname = False) + ', ' + _('born') + ' ' + patient.get_formatted_dob('%Y %B %d')
		readme_file.write(_README_CONTENT % pat_str)
		readme_file.close()
		return readme_fname

	#--------------------------------------------------------
	def _create_cd_inf(self, patient, directory):
		_CD_INF_CONTENT = (
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
		fname = os.path.join(directory, 'CD.INF')
		cd_inf = io.open(fname, mode = 'wt', encoding = 'utf8')
		cd_inf.write(_CD_INF_CONTENT % (
			patient['lastnames'],
			patient['firstnames'],
			gmTools.coalesce(patient['gender'], '?'),
			patient.get_formatted_dob('%Y-%m-%d'),
			gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), format = '%Y-%m-%d'),
			patient.ID,
			_cfg.get(option = 'client_version'),
			' / '.join([ '%s = %s (%s)' % (g['tag'], g['label'], g['l10n_label']) for g in patient.gender_list ])
		))
		cd_inf.close()
		return fname

	#--------------------------------------------------------
	def _create_autorun_inf(self, patient, directory):
		_AUTORUN_INF_CONTENT = (							# needs \r\n for Windows
			'[AutoRun.Amd64]\r\n'					# 64 bit
			'label=%(label)s\r\n'					# patient name/DOB
			'shellexecute=index.html\r\n'
			'action=%(action)s\r\n'					# % _('Browse patient data')
			'%(icon)s\r\n'							# "icon=gnumed.ico" or ""
			'UseAutoPlay=1\r\n'
			'\r\n'
			'[AutoRun]\r\n'							# 32 bit
			'label=%(label)s\r\n'					# patient name/DOB
			'shellexecute=index.html\r\n'
			'action=%(action)s\r\n'					# % _('Browse patient data')
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
		autorun_dict = {
			'label': self._compute_autorun_inf_label(patient),
			'action': _('Browse patient data'),
			'icon': ''
		}
		media_icon_kwd = '$$gnumed_patient_media_export_icon'
		media_icon_kwd_exp = gmKeywordExpansion.get_expansion (
			keyword = media_icon_kwd,
			textual_only = False,
			binary_only = True
		)
		icon_tmp_fname = media_icon_kwd_exp.save_to_file (
			target_mime = 'image/x-icon',
			target_extension = '.ico',
			ignore_conversion_problems = True
		)
		if icon_tmp_fname is None:
			_log.error('cannot retrieve <%s>', media_icon_kwd)
		else:
			media_icon_fname = os.path.join(directory, 'gnumed.ico')
			try:
				shutil.copy2(icon_tmp_fname, media_icon_fname)
				autorun_dict['icon'] = 'icon=gnumed.ico'
			except Exception:
				_log.exception('cannot move %s to %s', icon_tmp_fname, media_icon_fname)
		autorun_fname = os.path.join(directory, 'AUTORUN.INF')
		autorun_file = io.open(autorun_fname, mode = 'wt', encoding = 'cp1252', errors = 'replace')
		autorun_file.write(_AUTORUN_INF_CONTENT % autorun_dict)
		autorun_file.close()
		return autorun_fname

	#--------------------------------------------------------
	def _compute_autorun_inf_label(self, patient):
		if patient is None:
			# if no patient provided - assume the target media
			# is to be encrypted and thusly do not expose patient data,
			# AUTORUN.INF itself will not be encrypted because
			# Windows must be able to parse it
			return _('GNUmed patient data excerpt')[:32]

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
		#exp.add_file(sys.argv[2])
		prax = gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.cPraxisBranch(1))
		print(prax)
		#print(prax.branch)
		try:
			pwd = sys.argv[2]
		except IndexError:
			pwd = None
		print(exp.export(passphrase = pwd))

	#---------------------------------------
	def test_label():

		from Gnumed.business.gmPerson import cPatient
		#from Gnumed.business.gmPersonSearch import ask_for_patient

		#while ask_for_patient() is not None:
		pat_min = 1
		pat_max = 100
		try:
			pat_min = int(sys.argv[2])
			pat_max = int(sys.argv[3])
		except Exception:
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
			except Exception:
				continue
			f.write(exp_area._compute_autorun_inf_label(pat) + '\n')
		f.close()
		return

	#---------------------------------------
	#test_export_items()
	#test_export_area()

	gmPG2.request_login_params(setup_pool = True)
	test_label()

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
