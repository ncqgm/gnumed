"""This module encapsulates a document stored in a GNUmed database."""
#============================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import os
import time
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmWorkerThread

from Gnumed.business import gmOrganization


_log = logging.getLogger('gm.docs')

MUGSHOT=26
DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE = 'visual progress note'
DOCUMENT_TYPE_PRESCRIPTION = 'prescription'

#============================================================
class cDocumentFolder:
	"""Represents a folder with medical documents for a single patient."""

	def __init__(self, aPKey = None):
		"""Fails if

		- patient referenced by aPKey does not exist
		"""
		self.pk_patient = aPKey			# == identity.pk == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError("No patient with PK [%s] in database." % aPKey)

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
#		if not self._register_interests():
#			raise gmExceptions.ConstructorError, "cannot register signal interests"

		_log.debug('instantiated document folder for patient [%s]' % self.pk_patient)
	#--------------------------------------------------------
	def cleanup(self):
		pass
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key (= patient) exist ?

		- true/false/None
		"""
		# patient in demographic database ?
		rows, idx = gmPG2.run_ro_queries(queries = [
			{'cmd': "select exists(select pk from dem.identity where pk = %s)", 'args': [self.pk_patient]}
		])
		if not rows[0][0]:
			_log.error("patient [%s] not in demographic database" % self.pk_patient)
			return None
		return True
	#--------------------------------------------------------
	# API
	#--------------------------------------------------------
	def get_latest_freediams_prescription(self):
		cmd = """
			SELECT pk_doc
			FROM blobs.v_doc_med
			WHERE
				pk_patient = %(pat)s
					AND
				type = %(typ)s
					AND
				ext_ref = %(ref)s
			ORDER BY
				clin_when DESC
			LIMIT 1
		"""
		args = {
			'pat': self.pk_patient,
			'typ': DOCUMENT_TYPE_PRESCRIPTION,
			'ref': 'FreeDiams'
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if len(rows) == 0:
			_log.info('no FreeDiams prescription available for patient [%s]' % self.pk_patient)
			return None
		prescription = cDocument(aPK_obj = rows[0][0])
		return prescription

	#--------------------------------------------------------
	def get_latest_mugshot(self):
		cmd = "SELECT pk_obj FROM blobs.v_latest_mugshot WHERE pk_patient = %s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		if len(rows) == 0:
			_log.info('no mugshots available for patient [%s]' % self.pk_patient)
			return None
		return cDocumentPart(aPK_obj = rows[0][0])

	latest_mugshot = property(get_latest_mugshot)

	#--------------------------------------------------------
	def get_mugshot_list(self, latest_only=True):
		if latest_only:
			cmd = "select pk_doc, pk_obj from blobs.v_latest_mugshot where pk_patient=%s"
		else:
			cmd = """
				select
					vdm.pk_doc as pk_doc,
					dobj.pk as pk_obj
				from
					blobs.v_doc_med vdm
					blobs.doc_obj dobj
				where
					vdm.pk_type = (select pk from blobs.doc_type where name = 'patient photograph')
					and vdm.pk_patient = %s
					and dobj.fk_doc = vdm.pk_doc
			"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		return rows

	#--------------------------------------------------------
	def get_doc_list(self, doc_type=None):
		"""return flat list of document IDs"""

		args = {
			'ID': self.pk_patient,
			'TYP': doc_type
		}

		cmd = """
			select vdm.pk_doc
			from blobs.v_doc_med vdm
			where
				vdm.pk_patient = %%(ID)s
				%s
			order by vdm.clin_when"""

		if doc_type is None:
			cmd = cmd % ''
		else:
			try:
				int(doc_type)
				cmd = cmd % 'and vdm.pk_type = %(TYP)s'
			except (TypeError, ValueError):
				cmd = cmd % 'and vdm.pk_type = (select pk from blobs.doc_type where name = %(TYP)s)'

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		doc_ids = []
		for row in rows:
			doc_ids.append(row[0])
		return doc_ids

	#--------------------------------------------------------
	def get_visual_progress_notes(self, episodes=None, encounter=None):
		return self.get_documents (
			doc_type = DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE,
			pk_episodes = episodes,
			encounter = encounter
		)

	#--------------------------------------------------------
	def get_unsigned_documents(self):
		args = {'pat': self.pk_patient}
		cmd = _SQL_get_document_fields % """
			pk_doc = ANY (
				SELECT DISTINCT ON (b_vo.pk_doc) b_vo.pk_doc
				FROM blobs.v_obj4doc_no_data b_vo
				WHERE
					pk_patient = %(pat)s
						AND
					reviewed IS FALSE
			)
			ORDER BY clin_when DESC"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cDocument(row = {'pk_field': 'pk_doc', 'idx': idx, 'data': r}) for r in rows ]

	#--------------------------------------------------------
	def get_documents(self, doc_type=None, pk_episodes=None, encounter=None, order_by=None, exclude_unsigned=False, pk_types=None):
		"""Return list of documents."""
		args = {
			'pat': self.pk_patient,
			'type': doc_type,
			'enc': encounter
		}
		where_parts = ['pk_patient = %(pat)s']
		if doc_type is not None:
			try:
				int(doc_type)
				where_parts.append('pk_type = %(type)s')
			except (TypeError, ValueError):
				where_parts.append('pk_type = (SELECT pk FROM blobs.doc_type WHERE name = %(type)s)')
		if pk_types:
			where_parts.append('pk_type = ANY(%(pk_types)s)')
			args['pk_types'] = pk_types
		if pk_episodes:
			where_parts.append('pk_episode = ANY(%(epis)s)')
			args['epis'] = pk_episodes
		if encounter is not None:
			where_parts.append('pk_encounter = %(enc)s')
		if exclude_unsigned:
			where_parts.append('pk_doc = ANY(SELECT b_vo.pk_doc FROM blobs.v_obj4doc_no_data b_vo WHERE b_vo.pk_patient = %(pat)s AND b_vo.reviewed IS TRUE)')
		if order_by is None:
			order_by = 'ORDER BY clin_when'
		cmd = "%s\n%s" % (_SQL_get_document_fields % ' AND '.join(where_parts), order_by)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cDocument(row = {'pk_field': 'pk_doc', 'idx': idx, 'data': r}) for r in rows ]

	documents = property(get_documents)

	#--------------------------------------------------------
	def add_document(self, document_type=None, encounter=None, episode=None, link_obj=None):
		return create_document(link_obj = link_obj, document_type = document_type, encounter = encounter, episode = episode)

	#--------------------------------------------------------
	def add_prescription(self, encounter=None, episode=None, link_obj=None):
		return self.add_document (
			link_obj = link_obj,
			document_type = create_document_type (
				document_type = DOCUMENT_TYPE_PRESCRIPTION
			)['pk_doc_type'],
			encounter = encounter,
			episode = episode
		)

	#--------------------------------------------------------
	def _get_all_document_org_units(self):
		cmd = gmOrganization._SQL_get_org_unit % (
			'pk_org_unit IN (SELECT DISTINCT ON (pk_org_unit) pk_org_unit FROM blobs.v_doc_med WHERE pk_patient = %(pat)s)'
		)
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmOrganization.cOrgUnit(row = {'data': r, 'idx': idx, 'pk_field': 'pk_org_unit'}) for r in rows ]

	all_document_org_units = property(_get_all_document_org_units)

#============================================================
_SQL_get_document_part_fields = "select * from blobs.v_obj4doc_no_data where %s"

class cDocumentPart(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one part of a medical document."""

	_cmd_fetch_payload = _SQL_get_document_part_fields % "pk_obj = %s"
	_cmds_store_payload = [
		"""UPDATE blobs.doc_obj SET
				seq_idx = %(seq_idx)s,
				comment = gm.nullify_empty_string(%(obj_comment)s),
				filename = gm.nullify_empty_string(%(filename)s),
				fk_intended_reviewer = %(pk_intended_reviewer)s
			WHERE
				pk = %(pk_obj)s
					AND
				xmin = %(xmin_doc_obj)s
			RETURNING
				xmin AS xmin_doc_obj"""
	]
	_updatable_fields = [
		'seq_idx',
		'obj_comment',
		'pk_intended_reviewer',
		'filename'
	]
	#--------------------------------------------------------
	# retrieve data
	#--------------------------------------------------------
	def save_to_file(self, aChunkSize=0, filename=None, target_mime=None, target_extension=None, ignore_conversion_problems=False, directory=None, conn=None):
		if filename is None:
			filename = self.get_useful_filename(make_unique = True, directory = directory)
		dl_fname = self.__download_to_file(filename = filename)
		if dl_fname is None:
			return None

		if target_mime is None:
			return gmMimeLib.adjust_extension_by_mimetype(dl_fname)

		converted_fname = self.__convert_file_to (
			filename = dl_fname,
			target_mime = target_mime,
			target_extension = target_extension
		)
		if converted_fname is None:
			if ignore_conversion_problems:
				return dl_fname
			return None

		gmTools.remove_file(dl_fname)
		return converted_fname

	#--------------------------------------------------------
	def get_reviews(self):
		cmd = """
SELECT
	reviewer,
	reviewed_when,
	is_technically_abnormal,
	clinically_relevant,
	is_review_by_responsible_reviewer,
	is_your_review,
	coalesce(comment, '')
FROM blobs.v_reviewed_doc_objects
WHERE pk_doc_obj = %s
ORDER BY
	is_your_review desc,
	is_review_by_responsible_reviewer desc,
	reviewed_when desc
"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return rows

	#--------------------------------------------------------
	def __get_containing_document(self):
		return cDocument(aPK_obj = self._payload[self._idx['pk_doc']])

	containing_document = property(__get_containing_document)

	#--------------------------------------------------------
	# store data
	#--------------------------------------------------------
	def update_data_from_file(self, fname=None, link_obj=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.error('[%s] is not a readable file' % fname)
			return False

		cmd = "UPDATE blobs.doc_obj SET data = %(data)s::BYTEA WHERE pk = %(pk)s RETURNING md5(data) AS md5"
		args = {'pk': self.pk_obj}
		md5 = gmTools.file2md5(filename = fname, return_hex = True)
		if not gmPG2.file2bytea(conn = link_obj, query = cmd, filename = fname, args = args, file_md5 = md5):
			return False

		# must update XMIN now ...
		self.refetch_payload(link_obj = link_obj)
		return True

	#--------------------------------------------------------
	def set_reviewed(self, technically_abnormal=None, clinically_relevant=None):
		# row already there ?
		cmd = """
select pk
from blobs.reviewed_doc_objs
where
	fk_reviewed_row = %s and
	fk_reviewer = (select pk from dem.staff where db_user = current_user)"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])

		# INSERT needed
		if len(rows) == 0:
			cols = [
				"fk_reviewer",
				"fk_reviewed_row",
				"is_technically_abnormal",
				"clinically_relevant"
			]
			vals = [
				'%(fk_row)s',
				'%(abnormal)s',
				'%(relevant)s'
			]
			args = {
				'fk_row': self.pk_obj,
				'abnormal': technically_abnormal,
				'relevant': clinically_relevant
			}
			cmd = """
insert into blobs.reviewed_doc_objs (
	%s
) values (
	(select pk from dem.staff where db_user=current_user),
	%s
)""" % (', '.join(cols), ', '.join(vals))

		# UPDATE needed
		if len(rows) == 1:
			pk_review = rows[0][0]
			args = {
				'abnormal': technically_abnormal,
				'relevant': clinically_relevant,
				'pk_review': pk_review
			}
			cmd = """
				UPDATE blobs.reviewed_doc_objs SET
					is_technically_abnormal = %(abnormal)s,
					clinically_relevant = %(relevant)s
				WHERE
					pk = %(pk_review)s
			"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

		return True

	#--------------------------------------------------------
	def set_as_active_photograph(self):
		if self._payload[self._idx['type']] != 'patient photograph':
			return False
		# set seq_idx to current max + 1
		cmd = 'SELECT coalesce(max(seq_idx)+1, 1) FROM blobs.doc_obj WHERE fk_doc = %(doc_id)s'
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': {'doc_id': self._payload[self._idx['pk_doc']]}
			}]
		)
		self._payload[self._idx['seq_idx']] = rows[0][0]
		self._is_modified = True
		return self.save_payload()

	#--------------------------------------------------------
	def reattach(self, pk_doc=None):
		if pk_doc == self._payload[self._idx['pk_doc']]:
			return True

		cmd = """
			UPDATE blobs.doc_obj SET
				fk_doc = %(pk_doc_target)s,
				-- coalesce needed for no-parts target docs
				seq_idx = (SELECT coalesce(max(seq_idx) + 1, 1) FROM blobs.doc_obj WHERE fk_doc = %(pk_doc_target)s)
			WHERE
				EXISTS(SELECT 1 FROM blobs.doc_med WHERE pk = %(pk_doc_target)s)
					AND
				pk = %(pk_obj)s
					AND
				xmin = %(xmin_doc_obj)s
			RETURNING fk_doc
		"""
		args = {
			'pk_doc_target': pk_doc,
			'pk_obj': self.pk_obj,
			'xmin_doc_obj': self._payload[self._idx['xmin_doc_obj']]
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
		if len(rows) == 0:
			return False
		# The following should never hold true because the target
		# fk_doc is returned from the query and it is checked for
		# equality before the UPDATE already. Assuming the update
		# failed to update a row because the target fk_doc did
		# not exist we would not get *any* rows in return - for
		# which condition we also already checked
		if rows[0]['fk_doc'] == self._payload[self._idx['pk_doc']]:
			return False

		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def display_via_mime(self, chunksize=0, block=None):

		fname = self.save_to_file(aChunkSize = chunksize)
		if fname is None:
			return False, ''

		success, msg = gmMimeLib.call_viewer_on_file(fname, block = block)
		if not success:
			return False, msg

		return True, ''

	#--------------------------------------------------------
	def format_single_line(self):
		f_ext = ''
		if self._payload[self._idx['filename']] is not None:
			f_ext = os.path.splitext(self._payload[self._idx['filename']])[1].strip('.').strip()
		if f_ext != '':
			f_ext = ' .' + f_ext.upper()
		txt = _('part %s, %s%s%s of document %s from %s%s') % (
			self._payload[self._idx['seq_idx']],
			gmTools.size2str(self._payload[self._idx['size']]),
			f_ext,
			gmTools.coalesce(self._payload[self._idx['obj_comment']], '', ' ("%s")'),
			self._payload[self._idx['l10n_type']],
			gmDateTime.pydt_strftime(self._payload[self._idx['date_generated']], '%Y %b %d'),
			gmTools.coalesce(self._payload[self._idx['doc_comment']], '', ' ("%s")')
		)
		return txt

	#--------------------------------------------------------
	def format(self, single_line=False):
		if single_line:
			return self.format_single_line()

		txt = _('%s document part                 [#%s]\n') % (
			gmTools.bool2str (
				boolean = self._payload[self._idx['reviewed']],
				true_str = _('Reviewed'),
				false_str = _('Unreviewed')
			),
			self._payload[self._idx['pk_obj']]
		)
		f_ext = ''
		if self._payload[self._idx['filename']] is not None:
			f_ext = os.path.splitext(self._payload[self._idx['filename']])[1].strip('.').strip()
		if f_ext != '':
			f_ext = '.' + f_ext.upper() + ' '
		txt += _(' Part %s: %s %s(%s Bytes)\n') % (
			self._payload[self._idx['seq_idx']],
			gmTools.size2str(self._payload[self._idx['size']]),
			f_ext,
			self._payload[self._idx['size']]
		)
		if self._payload[self._idx['filename']] is not None:
			path, fname = os.path.split(self._payload[self._idx['filename']])
			if not path.endswith(os.path.sep):
				if path != '':
					path += os.path.sep
			if path != '':
				path = ' (%s)' % path
			txt += _(' Filename: %s%s\n') % (fname, path)
		if self._payload[self._idx['obj_comment']] is not None:
			txt += '\n%s\n' % self._payload[self._idx['obj_comment']]
		return txt

	#--------------------------------------------------------
	def format_metainfo(self, callback=None):
		"""If <callback> is not None it will receive a tuple (status, description, pk_obj)."""
		if callback is None:
			return self.__run_metainfo_formatter()

		gmWorkerThread.execute_in_worker_thread (
			payload_function = self.__run_metainfo_formatter,
			completion_callback = callback,
			worker_name = 'doc_part-metainfo_formatter-'
		)

	#--------------------------------------------------------
	def get_useful_filename(self, patient=None, make_unique=False, directory=None, include_gnumed_tag=True, date_before_type=False, name_first=True):
		patient_part = ''
		if patient is not None:
			if name_first:
				patient_part = '%s-' % patient.subdir_name
			else:
				patient_part = '-%s' % patient.subdir_name

		# preserve original filename extension if available
		suffix = '.dat'
		if self._payload[self._idx['filename']] is not None:
			tmp, suffix = os.path.splitext (
				gmTools.fname_sanitize(self._payload[self._idx['filename']]).casefold()
			)
			if suffix == '':
				suffix = '.dat'

		if include_gnumed_tag:
			fname_template = 'gm_doc-part_%s-%%s' % self._payload[self._idx['seq_idx']]
		else:
			fname_template = '%%s-part_%s' % self._payload[self._idx['seq_idx']]

		if date_before_type:
			date_type_part = '%s-%s' % (
				gmDateTime.pydt_strftime(self._payload[self._idx['date_generated']], '%Y-%m-%d', 'utf-8', gmDateTime.acc_days),
				self._payload[self._idx['l10n_type']].replace(' ', '_').replace('-', '_'),
			)
		else:
			date_type_part = '%s-%s' % (
				self._payload[self._idx['l10n_type']].replace(' ', '_').replace('-', '_'),
				gmDateTime.pydt_strftime(self._payload[self._idx['date_generated']], '%Y-%m-%d', 'utf-8', gmDateTime.acc_days)
			)

		if name_first:
			date_type_name_part = patient_part + date_type_part
		else:
			date_type_name_part = date_type_part + patient_part

		fname = fname_template % date_type_name_part

		if make_unique:
			fname = gmTools.get_unique_filename (
				prefix = '%s-' % gmTools.fname_sanitize(fname),
				suffix = suffix,
				tmp_dir = directory
			)
		else:
			fname = gmTools.fname_sanitize(os.path.join(gmTools.coalesce(directory, gmTools.gmPaths().tmp_dir), fname + suffix))

		return fname

	useful_filename = property(get_useful_filename)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __download_to_file(self, filename=None, aChunkSize=0, conn=None):
		if self._payload[self._idx['size']] == 0:
			_log.debug('part size 0, nothing to download')
			return None

		if filename is None:
			filename = gmTools.get_unique_filename()
		success = gmPG2.bytea2file (
			data_query = {
				'cmd': 'SELECT substring(data from %(start)s for %(size)s) FROM blobs.doc_obj WHERE pk=%(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['size']],
			conn = conn
		)
		if not success:
			return None

		return filename

	#--------------------------------------------------------
	def __convert_file_to(self, filename=None, target_mime=None, target_extension=None):
		assert (filename is not None), '<filename> must not be None'
		assert (target_mime is not None), '<target_mime> must not be None'

		if target_extension is None:
			target_extension = gmMimeLib.guess_ext_by_mimetype(mimetype = target_mime)
		src_path, src_name = os.path.split(filename)
		src_stem, src_ext = os.path.splitext(src_name)
		conversion_tmp_name = gmTools.get_unique_filename (
			prefix = '%s.conv2.' % src_stem,
			suffix = target_extension
		)
		_log.debug('attempting conversion: [%s] -> [<%s>:%s]', filename, target_mime, conversion_tmp_name)
		converted_fname = gmMimeLib.convert_file (
			filename = filename,
			target_mime = target_mime,
			target_filename = conversion_tmp_name
		)
		if converted_fname is None:
			_log.warning('conversion failed')
			return None

		tmp_path, conv_name = os.path.split(converted_fname)
		conv_name_in_src_path = os.path.join(src_path, conv_name)
		try:
			os.replace(converted_fname, conv_name_in_src_path)
		except OSError:
			_log.exception('cannot os.replace(%s, %s)', converted_fname, conv_name_in_src_path)
			return None

		return gmMimeLib.adjust_extension_by_mimetype(conv_name_in_src_path)

	#--------------------------------------------------------
	def __run_metainfo_formatter(self):
		filename = self.__download_to_file()
		if filename is None:
			_log.error('problem downloading part')
			return (False, _('problem downloading document part'))

		status, desc = gmMimeLib.describe_file(filename)
		return (status, desc, self.pk_obj)

#------------------------------------------------------------
def delete_document_part(part_pk=None, encounter_pk=None):
	cmd = """
		SELECT blobs.delete_document_part(%(pk)s, %(enc)s)
		WHERE NOT EXISTS
			(SELECT 1 FROM clin.export_item where fk_doc_obj = %(pk)s)
	"""
	args = {'pk': part_pk, 'enc': encounter_pk}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return

#============================================================
_SQL_get_document_fields = "SELECT * FROM blobs.v_doc_med b_vdm WHERE %s"

class cDocument(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one medical document."""

	_cmd_fetch_payload = _SQL_get_document_fields % "pk_doc = %s"
	_cmds_store_payload = [
		"""UPDATE blobs.doc_med SET
				fk_type = %(pk_type)s,
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s,
				fk_org_unit = %(pk_org_unit)s,
				unit_is_receiver = %(unit_is_receiver)s,
				clin_when = %(clin_when)s,
				comment = gm.nullify_empty_string(%(comment)s),
				ext_ref = gm.nullify_empty_string(%(ext_ref)s),
				fk_hospital_stay = %(pk_hospital_stay)s
			WHERE
				pk = %(pk_doc)s and
				xmin = %(xmin_doc_med)s
			RETURNING
				xmin AS xmin_doc_med"""
	]
	_updatable_fields = [
		'pk_type',
		'comment',
		'clin_when',
		'ext_ref',
		'pk_episode',
		'pk_encounter',			# mainly useful when moving visual progress notes to their respective encounters
		'pk_org_unit',
		'unit_is_receiver',
		'pk_hospital_stay'
	]

	#--------------------------------------------------------
	def refetch_payload(self, ignore_changes=False, link_obj=None):
		try: del self.__has_unreviewed_parts
		except AttributeError: pass

		return super().refetch_payload(ignore_changes = ignore_changes, link_obj = link_obj)

	#--------------------------------------------------------
	def get_descriptions(self, max_lng=250):
		"""Get document descriptions.

		- will return a list of rows
		"""
		if max_lng is None:
			cmd = "SELECT pk, text FROM blobs.doc_desc WHERE fk_doc = %s"
		else:
			cmd = "SELECT pk, substring(text from 1 for %s) FROM blobs.doc_desc WHERE fk_doc=%%s" % max_lng
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return rows

	#--------------------------------------------------------
	def add_description(self, description=None):
		cmd = "insert into blobs.doc_desc (fk_doc, text) values (%s, %s)"
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj, description]}])
		return True

	#--------------------------------------------------------
	def update_description(self, pk=None, description=None):
		cmd = "update blobs.doc_desc set text = %(desc)s where fk_doc = %(doc)s and pk = %(pk_desc)s"
		gmPG2.run_rw_queries(queries = [
			{'cmd': cmd, 'args': {'doc': self.pk_obj, 'pk_desc': pk, 'desc': description}}
		])
		return True

	#--------------------------------------------------------
	def delete_description(self, pk=None):
		cmd = "delete from blobs.doc_desc where fk_doc = %(doc)s and pk = %(desc)s"
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'doc': self.pk_obj, 'desc': pk}}])
		return True

	#--------------------------------------------------------
	def _get_parts(self):
		cmd = _SQL_get_document_part_fields % "pk_doc = %s ORDER BY seq_idx"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}], get_col_idx = True)
		return [ cDocumentPart(row = {'pk_field': 'pk_obj', 'idx': idx, 'data': r}) for r in rows ]

	parts = property(_get_parts)

	#--------------------------------------------------------
	def add_part(self, file=None, link_obj=None):
		"""Add a part to the document."""
		# create dummy part
		cmd = """
			INSERT INTO blobs.doc_obj (
				fk_doc, data, seq_idx
			) VALUES (
				%(doc_id)s,
				''::bytea,
				(SELECT coalesce(max(seq_idx)+1, 1) FROM blobs.doc_obj WHERE fk_doc = %(doc_id)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries (
			link_obj = link_obj,
			queries = [{'cmd': cmd, 'args': {'doc_id': self.pk_obj}}],
			return_data = True
		)
		# init document part instance
		pk_part = rows[0][0]
		new_part = cDocumentPart(aPK_obj = pk_part, link_obj = link_obj)
		if not new_part.update_data_from_file(link_obj = link_obj, fname = file):
			_log.error('cannot import binary data from [%s] into document part' % file)
			gmPG2.run_rw_queries (
				link_obj = link_obj,
				queries = [{'cmd': "DELETE FROM blobs.doc_obj WHERE pk = %s", 'args': [pk_part]}]
			)
			return None
		new_part['filename'] = file
		new_part.save_payload(conn = link_obj)

		return new_part

	#--------------------------------------------------------
	def add_parts_from_files(self, files=None, reviewer=None):

		new_parts = []

		for filename in files:
			new_part = self.add_part(file = filename)
			if new_part is None:
				msg = 'cannot instantiate document part object from [%s]' % filename
				_log.error(msg)
				return (False, msg, filename)
			new_parts.append(new_part)

			if reviewer is not None:
				new_part['pk_intended_reviewer'] = reviewer			# None == Null
				success, data = new_part.save_payload()
				if not success:
					msg = 'cannot set reviewer to [%s] on [%s]' % (reviewer, filename)
					_log.error(msg)
					_log.error(str(data))
					return (False, msg, filename)

		return (True, '', new_parts)

	#--------------------------------------------------------
	def save_parts_to_files(self, export_dir=None, chunksize=0, conn=None):
		fnames = []
		for part in self.parts:
			fname = part.save_to_file(aChunkSize = chunksize, directory = export_dir, conn = conn)
			if fname is None:
				_log.error('cannot export document part [%s]', part)
				continue
			fnames.append(fname)
		return fnames

	#--------------------------------------------------------
	def _get_has_unreviewed_parts(self):
		try:
			return self.__has_unreviewed_parts			# pylint: disable=access-member-before-definition

		except AttributeError:
			pass

		cmd = "SELECT EXISTS(SELECT 1 FROM blobs.v_obj4doc_no_data WHERE pk_doc = %(pk)s AND reviewed IS FALSE)"
		args = {'pk': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		self.__has_unreviewed_parts = rows[0][0]
		return self.__has_unreviewed_parts

	has_unreviewed_parts = property(_get_has_unreviewed_parts)

	#--------------------------------------------------------
	def set_reviewed(self, technically_abnormal=None, clinically_relevant=None):
		# FIXME: this is probably inefficient
		for part in self.parts:
			if not part.set_reviewed(technically_abnormal, clinically_relevant):
				return False
		return True

	#--------------------------------------------------------
	def set_primary_reviewer(self, reviewer=None):
		for part in self.parts:
			part['pk_intended_reviewer'] = reviewer
			success, data = part.save_payload()
			if not success:
				_log.error('cannot set reviewer to [%s]' % reviewer)
				_log.error(str(data))
				return False
		return True

	#--------------------------------------------------------
	def format_single_line(self):

		part_count = len(self._payload[self._idx['seq_idx_list']])
		if part_count == 0:
			parts = _('no parts')
		elif part_count == 1:
			parts = _('1 part')
		else:
			parts = _('%s parts') % part_count

		detail = ''
		if self._payload[self._idx['ext_ref']] is not None:
			detail = self._payload[self._idx['ext_ref']]
		if self._payload[self._idx['unit']] is not None:
			template = _('%s of %s')
			if detail == '':
				detail = _('%s of %s') % (
					self._payload[self._idx['unit']],
					self._payload[self._idx['organization']]
				)
			else:
				detail += (' @ ' + template % (
					self._payload[self._idx['unit']],
					self._payload[self._idx['organization']]
				))
		if detail != '':
			detail = ' (%s)' % detail

		return '%s %s (%s):%s%s' % (
			gmDateTime.pydt_strftime(self._payload[self._idx['clin_when']], '%Y %b %d', accuracy = gmDateTime.acc_days),
			self._payload[self._idx['l10n_type']],
			parts,
			gmTools.coalesce(self._payload[self._idx['comment']], '', ' "%s"'),
			detail
		)

	#--------------------------------------------------------
	def format(self, single_line=False):
		if single_line:
			return self.format_single_line()

		part_count = len(self._payload[self._idx['seq_idx_list']])
		if part_count == 0:
			parts = _('no parts')
		elif part_count == 1:
			parts = _('1 part')
		else:
			parts = _('%s parts') % part_count
		org = ''
		if self._payload[self._idx['unit']] is not None:
			if self._payload[self._idx['unit_is_receiver']]:
				org = _(' Receiver: %s @ %s\n') % (
					self._payload[self._idx['unit']],
					self._payload[self._idx['organization']]
				)
			else:
				org = _(' Sender: %s @ %s\n') % (
					self._payload[self._idx['unit']],
					self._payload[self._idx['organization']]
				)
		stay = ''
		if self._payload[self._idx['pk_hospital_stay']] is not None:
			stay = _('Hospital stay') + ': %s\n' % self.hospital_stay.format (
				left_margin = 0,
				include_procedures = False,
				include_docs = False,
				include_episode = False
			)

		txt = _(
			'%s (%s)   #%s\n'
			' Created: %s\n'
			' Episode: %s\n'
			'%s'
			'%s'
			'%s'
			'%s'
			'%s'
		) % (
			self._payload[self._idx['l10n_type']],
			parts,
			self._payload[self._idx['pk_doc']],
			gmDateTime.pydt_strftime(self._payload[self._idx['clin_when']], format = '%Y %b %d', accuracy = gmDateTime.acc_days),
			self._payload[self._idx['episode']],
			gmTools.coalesce(self._payload[self._idx['health_issue']], '', _(' Health issue: %s\n')),
			gmTools.coalesce(self._payload[self._idx['ext_ref']], '', _(' External reference: %s\n')),
			org,
			stay,
			gmTools.coalesce(self._payload[self._idx['comment']], '', ' %s')
		)

		return txt

	#--------------------------------------------------------
	def _get_hospital_stay(self):
		if self._payload[self._idx['pk_hospital_stay']] is None:
			return None
		from Gnumed.business import gmEMRStructItems
		return gmEMRStructItems.cHospitalStay(self._payload[self._idx['pk_hospital_stay']])

	hospital_stay = property(_get_hospital_stay)

	#--------------------------------------------------------
	def _get_org_unit(self):
		if self._payload[self._idx['pk_org_unit']] is None:
			return None
		return gmOrganization.cOrgUnit(self._payload[self._idx['pk_org_unit']])

	org_unit = property(_get_org_unit)

	#--------------------------------------------------------
	def _get_procedures(self):
		from Gnumed.business.gmEMRStructItems import get_procedures4document
		return get_procedures4document(pk_document = self.pk_obj)

	procedures = property(_get_procedures)

	#--------------------------------------------------------
	def _get_bills(self):
		from Gnumed.business.gmBilling import get_bills4document
		return get_bills4document(pk_document = self.pk_obj)

	bills = property(_get_bills)

#------------------------------------------------------------
def create_document(document_type=None, encounter=None, episode=None, link_obj=None):
	"""Returns new document instance or raises an exception."""
	try:
		int(document_type)
		cmd = """INSERT INTO blobs.doc_med (fk_type, fk_encounter, fk_episode) VALUES (%(type)s, %(enc)s, %(epi)s) RETURNING pk"""
	except ValueError:
		create_document_type(document_type = document_type)
		cmd = """
			INSERT INTO blobs.doc_med (
				fk_type,
				fk_encounter,
				fk_episode
			) VALUES (
				coalesce (
					(SELECT pk from blobs.doc_type bdt where bdt.name = %(type)s),
					(SELECT pk from blobs.doc_type bdt where _(bdt.name) = %(type)s)
				),
				%(enc)s,
				%(epi)s
			) RETURNING pk"""
	args = {'type': document_type, 'enc': encounter, 'epi': episode}
	rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], return_data = True)
	doc = cDocument(aPK_obj = rows[0][0], link_obj = link_obj)
	return doc

#------------------------------------------------------------
def search_for_documents(patient_id=None, type_id=None, external_reference=None, pk_episode=None, pk_types=None):
	"""Searches for documents with the given patient and type ID."""

	if (patient_id is None) and (pk_episode is None):
		raise ValueError('need patient_id or pk_episode to search for document')

	where_parts = []
	args = {
		'pat_id': patient_id,
		'type_id': type_id,
		'ref': external_reference,
		'pk_epi': pk_episode
	}

	if patient_id is not None:
		where_parts.append('pk_patient = %(pat_id)s')

	if type_id is not None:
		where_parts.append('pk_type = %(type_id)s')

	if external_reference is not None:
		where_parts.append('ext_ref = %(ref)s')

	if pk_episode is not None:
		where_parts.append('pk_episode = %(pk_epi)s')

	if pk_types is not None:
		where_parts.append('pk_type = ANY(%(pk_types)s)')
		args['pk_types'] = pk_types

	cmd = _SQL_get_document_fields % ' AND '.join(where_parts)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	return [ cDocument(row = {'data': r, 'idx': idx, 'pk_field': 'pk_doc'}) for r in rows ]

#------------------------------------------------------------
def delete_document(document_id=None, encounter_id=None):
	# cascades to doc_obj and doc_desc but not bill.bill
	cmd = "SELECT blobs.delete_document(%(pk)s, %(enc)s)"
	args = {'pk': document_id, 'enc': encounter_id}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	if not rows[0][0]:
		_log.error('cannot delete document [%s]', document_id)
		return False
	return True

#------------------------------------------------------------
def reclassify_documents_by_type(original_type=None, target_type=None):

	_log.debug('reclassifying documents by type')
	_log.debug('original: %s', original_type)
	_log.debug('target: %s', target_type)

	if target_type['pk_doc_type'] == original_type['pk_doc_type']:
		return True

	cmd = """
update blobs.doc_med set
	fk_type = %(new_type)s
where
	fk_type = %(old_type)s
"""
	args = {'new_type': target_type['pk_doc_type'], 'old_type': original_type['pk_doc_type']}

	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	return True

#============================================================
class cDocumentType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a document type."""
	_cmd_fetch_payload = """select * from blobs.v_doc_type where pk_doc_type=%s"""
	_cmds_store_payload = [
		"""update blobs.doc_type set
				name = %(type)s
			where
				pk=%(pk_obj)s and
				xmin=%(xmin_doc_type)s""",
		"""select xmin_doc_type from blobs.v_doc_type where pk_doc_type = %(pk_obj)s"""
	]
	_updatable_fields = ['type']
	#--------------------------------------------------------
	def set_translation(self, translation=None):

		if translation.strip() == '':
			return False

		if translation.strip() == self._payload[self._idx['l10n_type']].strip():
			return True

		rows, idx = gmPG2.run_rw_queries (
			queries = [
				{'cmd': 'select i18n.i18n(%s)', 'args': [self._payload[self._idx['type']]]},
				{'cmd': 'select i18n.upd_tx((select i18n.get_curr_lang()), %(orig)s, %(tx)s)',
				 'args': {
				 	'orig': self._payload[self._idx['type']],
					'tx': translation
					}
				}
			],
			return_data = True
		)
		if not rows[0][0]:
			_log.error('cannot set translation to [%s]' % translation)
			return False

		return self.refetch_payload()

#------------------------------------------------------------
def get_document_types():
	rows, idx = gmPG2.run_ro_queries (
		queries = [{'cmd': "SELECT * FROM blobs.v_doc_type"}],
		get_col_idx = True
	)
	doc_types = []
	for row in rows:
		row_def = {'pk_field': 'pk_doc_type', 'idx': idx, 'data': row}
		doc_types.append(cDocumentType(row = row_def))
	return doc_types

#------------------------------------------------------------
def get_document_type_pk(document_type=None):
	args = {'typ': document_type.strip()}

	cmd = 'SELECT pk FROM blobs.doc_type WHERE name = %(typ)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	if len(rows) == 0:
		cmd = 'SELECT pk FROM blobs.doc_type WHERE _(name) = %(typ)s'
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	if len(rows) == 0:
		return None

	return rows[0]['pk']

#------------------------------------------------------------
def map_types2pk(document_types=None):
	args = {'types': document_types}
	cmd = 'SELECT pk_doc_type, coalesce(l10n_type, type) as desc FROM blobs.v_doc_type WHERE l10n_type = ANY(%(types)s) OR type = ANY(%(types)s)'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	return rows

#------------------------------------------------------------
def create_document_type(document_type=None):
	# check for potential dupes:
	cmd = 'SELECT pk FROM blobs.doc_type WHERE name = %s'
	rows, idx = gmPG2.run_ro_queries (
		queries = [{'cmd': cmd, 'args': [document_type]}]
	)
	if len(rows) == 0:
		_log.debug('creating document type [%s]', document_type)
		cmd1 = "INSERT INTO blobs.doc_type (name) VALUES (%s) RETURNING pk"
		rows, idx = gmPG2.run_rw_queries (
			queries = [{'cmd': cmd1, 'args': [document_type]}],
			return_data = True
		)
	return cDocumentType(aPK_obj = rows[0][0])

#------------------------------------------------------------
def delete_document_type(document_type=None):
	if document_type['is_in_use']:
		return False

	gmPG2.run_rw_queries (
		queries = [{
			'cmd': 'delete from blobs.doc_type where pk=%s',
			'args': [document_type['pk_doc_type']]
		}]
	)
	return True

#------------------------------------------------------------
def get_ext_ref():
	"""This needs *considerably* more smarts."""
	dirname = gmTools.get_unique_filename (
		prefix = '',
		suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime())
	)
	# extract name for dir
	path, doc_ID = os.path.split(dirname)
	return doc_ID

#============================================================
def check_mimetypes_in_archive():
	mimetypes = {}
	cmd = 'SELECT pk FROM blobs.doc_med'
	doc_pks, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	print('Detecting mimetypes in document archive ...')
	doc_idx = 0
	part_count = 0
	for pk_row in doc_pks:
		doc_idx += 1
		print('\n#%s - document %s of %s: ' % (pk_row['pk'], doc_idx, len(doc_pks)), end = '')
		doc = cDocument(aPK_obj = pk_row['pk'])
		for part in doc.parts:
			part_count += 1
			print('#%s:%s bytes, ' % (part['pk_obj'], part['size']), end = '')
			part_fname = part.save_to_file()
			mimetype = gmMimeLib.guess_mimetype(part_fname)
			try:
				mimetypes[mimetype]['count'] += 1
			except KeyError:
				mimetypes[mimetype] = {
					'count': 1,
					'viewer': gmMimeLib.get_viewer_cmd(mimetype),
					'editor': gmMimeLib.get_editor_cmd(mimetype),
					'extension': gmMimeLib.guess_ext_by_mimetype(mimetype)
				}
	print('')
	print('')
	print('Number of documents :', len(doc_pks))
	print('Number of parts     :', part_count)
	print('Number of mime types:', len(mimetypes))
	for mimetype in mimetypes:
		print('')
		print('<%s>' % mimetype)
		print(' Extension:', mimetypes[mimetype]['extension'])
		print(' Use count:', mimetypes[mimetype]['count'])
		print('    Viewer:', mimetypes[mimetype]['viewer'])
		print('    Editor:', mimetypes[mimetype]['editor'])
	return 0

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------
	def test_doc_types():

		print("----------------------")
		print("listing document types")
		print("----------------------")

		for dt in get_document_types():
			print(dt)

		print("------------------------------")
		print("testing document type handling")
		print("------------------------------")

		dt = create_document_type(document_type = 'dummy doc type for unit test 1')
		print("created:", dt)

		dt['type'] = 'dummy doc type for unit test 2'
		dt.save_payload()
		print("changed base name:", dt)

		dt.set_translation(translation = 'Dummy-Dokumenten-Typ fuer Unit-Test')
		print("translated:", dt)

		print("deleted:", delete_document_type(document_type = dt))

		return
	#--------------------------------------------------------
	def test_adding_doc_part():

		print("-----------------------")
		print("testing document import")
		print("-----------------------")

		docs = search_for_documents(patient_id=12)
		doc = docs[0]
		print("adding to doc:", doc)

		fname = sys.argv[1]
		print("adding from file:", fname)
		part = doc.add_part(file=fname)
		print("new part:", part)

		return
	#--------------------------------------------------------
	def test_get_documents():

		doc_folder = cDocumentFolder(aPKey=12)

		#photo = doc_folder.get_latest_mugshot()
		#print type(photo), photo

		docs = doc_folder.get_documents(pk_types = [16])
		for doc in docs:
			#print type(doc), doc
			#print doc.parts
			#print doc.format_single_line()
			print('--------------------------')
			#print(doc.format(single_line = True))
			print(doc.format())
			#print(doc['pk_type'])

	#--------------------------------------------------------
	def test_save_to_file():
		doc_folder = cDocumentFolder(aPKey=12)
		docs = doc_folder.get_documents()
		for doc in docs:
			for part in doc.parts:
				print(part.save_to_file(target_mime = 'application/pdf', ignore_conversion_problems = True))

	#--------------------------------------------------------
	def test_get_useful_filename():
		pk = 12
		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(pk)
		doc_folder = cDocumentFolder(aPKey = pk)
		for doc in doc_folder.documents:
			for part in doc.parts:
				print(part.get_useful_filename (
					patient = pat,
					make_unique = True,
					directory = None,
					include_gnumed_tag = False,
					date_before_type = True,
					name_first = False
				))
	#--------------------------------------------------------
	def test_check_mimetypes_in_archive():
		check_mimetypes_in_archive()

	#--------------------------------------------------------
	def test_part_metainfo_formatter():

		#--------------------------------
		def desc_printer(worker_result):
			status, desc = worker_result
			print('printer callback:')
			print(status)
			print(desc)
			print('<hit key> for next')
			return
		#--------------------------------

		pk = 12
#		from Gnumed.business.gmPerson import cPatient
#		pat = cPatient(pk)
		doc_folder = cDocumentFolder(aPKey = pk)
		for doc in doc_folder.documents:
			for part in doc.parts:
				part.format_metainfo(callback = desc_printer)
				input('waiting ...')
#				success, desc = part.format_metainfo()
#				print(success)
#				print(desc)
#				input('next')

#				print(part.get_useful_filename (
#					patient = pat,
#					make_unique = True,
#					directory = None,
#					include_gnumed_tag = False,
#					date_before_type = True,
#					name_first = False
#				))

	#--------------------------------------------------------
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	gmPG2.request_login_params(setup_pool = True)

	#test_doc_types()
	#test_adding_doc_part()
	#test_get_documents()
	#test_get_useful_filename()
	#test_part_metainfo_formatter()
	#test_check_mimetypes_in_archive()
	test_save_to_file()

#	print get_ext_ref()
