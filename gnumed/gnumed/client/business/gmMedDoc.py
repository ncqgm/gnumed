"""This module encapsulates a document stored in a GNUmed database.

@copyright: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedDoc.py,v $
# $Id: gmMedDoc.py,v 1.81 2006-10-08 15:07:11 ncq Exp $
__version__ = "$Revision: 1.81 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, tempfile, os, shutil, os.path, types, time
from cStringIO import StringIO

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog, gmExceptions, gmBusinessDBObject, gmPG2

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

MUGSHOT=26
#============================================================
class cDocumentFolder:
	"""Represents a folder with medical documents for a single patient."""

	def __init__(self, aPKey = None):
		"""Fails if

		- patient referenced by aPKey does not exist
		"""
		self.pk_patient = aPKey			# == identity.pk == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with PK [%s] in database." % aPKey

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
#		if not self._register_interests():
#			raise gmExceptions.ConstructorError, "cannot register signal interests"

		_log.Log(gmLog.lData, 'instantiated document folder for patient [%s]' % self.pk_patient)
	#--------------------------------------------------------
	def cleanup(self):
		pass
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		# patient in demographic database ?
		rows, idx = gmPG2.run_ro_queries(queries = [
			{'cmd': u"select exists(select pk from dem.identity where pk = %s)", 'args': [self.pk_patient]}
		])
		if not rows[0][0]:
			_log.Log(gmLog.lErr, "patient [%s] not in demographic database" % self.pk_patient)
			return None
		return True
	#--------------------------------------------------------
	# API
	#--------------------------------------------------------
	def get_latest_mugshot(self):
		cmd = u"select pk_obj from blobs.v_latest_mugshot where pk_patient=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		if len(rows) == 0:
			_log.Log(gmLog.lInfo, 'no mugshots available for patient [%s]' % self.pk_patient)
			return None
		mugshot = cMedDocPart(aPK_obj=rows[0][0])
		return mugshot
	#--------------------------------------------------------
	def get_mugshot_list(self, latest_only=True):
		if latest_only:
			cmd = u"select pk_doc, pk_obj from blobs.v_latest_mugshot where pk_patient=%s"
		else:
			cmd = u"""
				select
					dm.pk as pk_doc,
					dobj.pk as pk_obj
				from
					blobs.doc_med dm
					blobs.doc_obj dobj
				where
					dm.fk_type = (select pk from blobs.doc_type where name='patient photograph') and
					dm.fk_identity=%s and
					and dobj.fk_doc = dm.pk
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
		# FIXME: might have to order by on modified_when, date is a string
		if doc_type is None:
			cmd = u"""select pk from blobs.doc_med where fk_identity=%(ID)s"""
		elif type(doc_type) == types.StringType:
			cmd = u"""
				select dm.pk
				from blobs.doc_med dm
				where
					dm.fk_identity = %(ID)s and
					dm.fk_type = (select pk from blobs.doc_type where name=%(TYP)s)"""
		else:
			cmd = u"""
				select dm.pk
				from blobs.doc_med dm
				where
					dm.fk_identity = %(ID)s and
					dm.fk_type = %(TYP)s"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		doc_ids = []
		for row in rows:
			doc_ids.append(row[0])
		return doc_ids
	#--------------------------------------------------------
	def get_documents(self, doc_type=None):
		"""Return list of documents."""
		doc_ids = self.get_doc_list(doc_type=doc_type)
		docs = []
		for doc_id in doc_ids:
			try:
				docs.append(cMedDoc(aPK_obj=doc_id))
			except gmExceptions.ConstructorError:
				_log.LogException('document error on [%s] for patient [%s]' % (doc_id, self.pk_patient))
				continue
		return docs
	#--------------------------------------------------------
	def add_document(self, document_type=None, encounter=None, episode=None):
		return create_document(patient_id=self.pk_patient, document_type=document_type, encounter=encounter, episode=episode)
#============================================================
class cMedDocPart(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one part of a medical document."""

	_cmd_fetch_payload = u"""select * from blobs.v_obj4doc_no_data where pk_obj=%s"""
	_cmds_store_payload = [
		"""update blobs.doc_obj set
				seq_idx=%(seq_idx)s,
				comment=%(obj_comment)s,
				fk_intended_reviewer=%(pk_intended_reviewer)s
			where
				pk=%(pk_obj)s and
				xmin=%(xmin_doc_obj)s""",
		"""select xmin_doc_obj from blobs.v_obj4doc_no_data where pk_obj = %(pk_obj)s"""
	]
	_updatable_fields = [
		'seq_idx',
		'obj_comment',
		'pk_intended_reviewer'
	]
	#--------------------------------------------------------
	def __del__(self):
		if self.__dict__.has_key('__conn'):
			self.__conn.close()
	#--------------------------------------------------------
	# retrieve data
	#--------------------------------------------------------
	def export_to_file(self, aTempDir = None, aChunkSize = 0):
		"""Export binary object data into file.

			- returns file name or None
		"""
		if self._payload[self._idx['size']] == 0:
			return None
		# if None -> use tempfile module default, else use given
		# path as base directory for temp files
		if aTempDir is not None:
			tempfile.tempdir = aTempDir
		tempfile.template = "gm-doc_obj-"

		fname = tempfile.mktemp()
		aFile = open(fname, 'wb+')

		if self.__export(aFile, aChunkSize):
			aFile.close()
			return fname
		aFile.close()
		return None
	#--------------------------------------------------------
	def export_to_string (self, aChunkSize = 0):
		"""Returns the document as a Python string.

			- WARNING: better have enough RAM for whatever size it is !!
		"""
		if self._payload[self._idx['size']] == 0:
			return None
		aFile = StringIO()
		if self.__export(aFile, aChunkSize):
			r = aFile.getvalue()
			aFile.close()
			return r
		aFile.close()
		return None
	#--------------------------------------------------------
	def __export (self, aFile=None, aChunkSize = 0):
		"""Export binary object data into <aFile>.

			- internal helper
			- writes data to the Python file-like object <aFile>
		"""
		# If the client sets an encoding other than the default we
		# will receive encoding-parsed data which isn't the binary
		# content we want. Hence we need to get our own connection.
		# It must be a read-write one so that we don't affect the
		# encoding for other users of the shared read-only
		# connections.
		# Actually, encodings shouldn't be applied to binary data
		# (eg. bytea types) in the first place but that is only
		# reported to be fixed > v7.4.
		# further tests reveal that at least on PG 8.0 this bug still
		# manifests itself
		conn = gmPG2.get_raw_connection()
		# this shouldn't actually, really be necessary
#		if conn.version > '7.4':
#			print "****************************************************"
#			print "*** if exporting BLOBs suddenly fails and        ***"
#			print "*** you are running PostgreSQL >= 8.1 please     ***"
#			print "*** mail a bug report to Karsten.Hilbert@gmx.net ***"
#			print "****************************************************"

		# Windoze sucks: it can't transfer objects of arbitrary size,
		# or maybe this is due to pyPgSQL ?
		# anyways, we need to split the transfer,
		# however, only possible if postgres >= 7.2
		max_chunk_size = aChunkSize

		# a chunk size of 0 means: all at once
		if ((max_chunk_size == 0) or (self._payload[self._idx['size']] <= max_chunk_size)):
			# retrieve binary field
			cmd = u"SELECT data FROM blobs.doc_obj WHERE pk=%s"
			rows, idx = gmPG2.run_ro_queries(link_obj=conn, queries=[{'cmd': cmd, 'args': [self.pk_obj]}])
			conn.close()
			if len(rows) == 0:
				_log.Log(gmLog.lErr, 'BLOB [%s] does not exist' % self.pk_obj)
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(rows[0][0]))
			return True

		# retrieve chunks
		# does this not carry the danger of cutting up multi-byte escape sequences ?
		# no, since bytea is binary
		needed_chunks, remainder = divmod(self._payload[self._idx['size']], max_chunk_size)
		_log.Log(gmLog.lData, "%s chunks of %s bytes, remainder of %s bytes" % (needed_chunks, max_chunk_size, remainder))
		for chunk_id in range(needed_chunks):
			pos = (chunk_id*max_chunk_size) + 1
			cmd = u"SELECT substring(data from %s for %s) FROM blobs.doc_obj WHERE pk=%%s" % (pos, max_chunk_size)
			try:
				rows, idx = gmPG2.run_ro_queries(link_obj=conn, queries=[{'cmd': cmd, 'args': [self.pk_obj]}])
			except:
				_log.Log(gmLog.lErr, 'cannot retrieve chunk [%s/%s], size [%s], doc part [%s], try decreasing chunk size' % (chunk_id+1, needed_chunks, max_chunk_size, self.pk_obj))
				raise
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(rows[0][0]))

		# retrieve remainder
		if remainder > 0:
			_log.Log(gmLog.lData, "retrieving trailing bytes after chunks")
			pos = (needed_chunks*max_chunk_size) + 1
			cmd = u"SELECT substring(data from %s for %s) FROM blobs.doc_obj WHERE pk=%%s" % (pos, remainder)
			try:
				rows, idx = gmPG2.run_ro_queries(link_obj=conn, queries=[{'cmd': cmd, 'args': [self.pk_obj]}])
			except:
				_log.Log(gmLog.lErr, 'cannot retrieve remaining [%s] bytes from doc part [%s]' % (remainder, self.pk_obj))
				raise
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))

		conn.close()
		return True
	#--------------------------------------------------------
	def get_reviews(self):
		cmd = u"""
select
	reviewer,
	reviewed_when,
	is_technically_abnormal,
	clinically_relevant,
	is_review_by_responsible_reviewer,
	is_your_review,
	coalesce(comment, '')
from blobs.v_reviewed_doc_objects
where pk_doc_obj = %s
order by
	is_your_review desc,
	is_review_by_responsible_reviewer desc,
	reviewed_when desc
"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return data
	#--------------------------------------------------------
	def get_containing_document(self):
		return cMedDoc(aPK_obj = self._payload[self._idx['pk_doc']])
	#--------------------------------------------------------
	# store data
	#--------------------------------------------------------
	def update_data_from_file(self, fname=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.Log(gmLog.lErr, '[%s] is not a readable file' % fname)
			return False

		# read from file and convert (escape)
		aFile = file(fname, "rb")
		byte_str_img_data = aFile.read()
		aFile.close()
		del aFile
		img_obj = buffer(byte_str_img_data)
		del(byte_str_img_data)

		conn = gmPG2.get_raw_connection()

		# insert the data
		cmd = u"UPDATE blobs.doc_obj SET data=%s::bytea WHERE pk=%s"
		gmPG2.run_rw_queries(link_obj=conn, queries = [{'cmd': cmd, 'args': [img_obj, self.pk_obj]}], end_tx=True)
		conn.close()

		# must update XMIN now ...
		self.refetch_payload()
		return True
	#--------------------------------------------------------
	def set_reviewed(self, technically_abnormal=None, clinically_relevant=None):
		# row already there ?
		cmd = u"""
select pk
from blobs.reviewed_doc_objs
where
	fk_reviewed_row = %s and
	fk_reviewer = (select pk from dem.staff where db_user=current_user)"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])

		# INSERT needed
		if len(rows) == 0:
			cols = [
				u"fk_reviewer",
				u"fk_reviewed_row",
				u"is_technically_abnormal",
				u"clinically_relevant"
			]
			vals = [
				u'%(fk_row)s',
				u'%(abnormal)s',
				u'%(relevant)s'
			]
			args = {
				'fk_row': self.pk_obj,
				'abnormal': technically_abnormal,
				'relevant': clinically_relevant
			}
			cmd = u"""
insert into blobs.reviewed_doc_objs (
	%s
) values (
	(select pk from dem.staff where db_user=current_user),
	%s
)""" % (', '.join(cols), ', '.join(vals))

		# UPDATE needed
		if len(rows) == 1:
			pk_row = rows[0][0]
			args = {
				'abnormal': technically_abnormal,
				'relevant': clinically_relevant,
				'pk_row': pk_row
			}
			cmd = u"""
update blobs.reviewed_doc_objs set
	is_technically_abnormal = %(abnormal)s,
	clinically_relevant = %(relevant)s
where
	pk=%(pk_row)s"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

		return True
#============================================================
class cMedDoc(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one medical document."""

	_cmd_fetch_payload = """select *, xmin_doc_med from blobs.v_doc_med where pk_doc=%s"""
	_cmds_store_payload = [
		"""update blobs.doc_med set
				fk_type=%(pk_type)s,
				comment=%(comment)s,
				date=%(date)s,
				ext_ref=%(ext_ref)s,
				fk_episode=%(pk_episode)s
			where
				pk=%(pk_doc)s and
				xmin=%(xmin_doc_med)s""",
		"""select xmin_doc_med from blobs.v_doc_med where pk_doc=%(pk_doc)s"""
		]

	_updatable_fields = [
		'pk_type',
		'comment',
		'date',
		'ext_ref',
		'pk_episode'
	]
	#--------------------------------------------------------
	def get_descriptions(self, max_lng=250):
		"""Get document descriptions.

		- will return a list of strings
		"""
		if max_lng is None:
			cmd = u"SELECT text FROM blobs.doc_desc WHERE fk_doc=%s"
		else:
			cmd = u"SELECT substring(text from 1 for %s) FROM blobs.doc_desc WHERE fk_doc=%%s" % max_lng
		rows = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		if len(rows) == 0:
			return [_('no descriptions available')]
		data = []
		for desc in rows:
			data.extend(desc)
		return data
	#--------------------------------------------------------
	def add_description(self, description):
		cmd = u"insert into blobs.doc_desc (fk_doc, text) values (%s, %s)"
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj, str(description)]}])
		return True
	#--------------------------------------------------------
	def get_parts(self):
		cmd = u"select pk_obj from blobs.v_obj4doc_no_data where pk_doc=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		parts = []
		for row in rows:
			try:
				parts.append(cMedDocPart(aPK_obj=row[0]))
			except ConstructorError, msg:
				_log.LogException(msg)
				continue
		return parts
	#--------------------------------------------------------
	def add_part(self, file=None):
		"""Add a part to the document."""
		# create dummy part
		cmd1 = u"""
			insert into blobs.doc_obj (
				fk_doc, fk_intended_reviewer, data, seq_idx
			) VALUES (
				%(doc_id)s,
				(select pk_staff from dem.v_staff where db_user=CURRENT_USER),
				''::bytea,
				(select coalesce(max(seq_idx)+1, 1) from blobs.doc_obj where fk_doc=%(doc_id)s)
			)"""
		rows, idx = gmPG2.run_rw_queries (
			queries = [
				{'cmd': cmd1, 'args': {'doc_id': self.pk_obj}},
				{'cmd': u"select currval('blobs.doc_obj_pk_seq')"}
			]
		)
		# init document part instance
		pk_part = rows[0][0]
		new_part = cMedDocPart(aPK_obj = pk_part)
		if not new_part.update_data_from_file(fname=file):
			_log.Log(gmLog.lErr, 'cannot import binary data from [%s] into document part' % file)
			gmPG2.run_rw_queries (
				queries = [
					{'cmd': u"delete from blobs.doc_obj where pk = %s", 'args': [pk_part]}
				]
			)
			return None
		return new_part
	#--------------------------------------------------------
	def add_parts_from_files(self, files=None, reviewer=None):

		new_parts = []

		for filename in files:
			new_part = self.add_part(file=filename)
			if new_part is None:
				msg = 'cannot instantiate document part object'
				_log.Log(gmLog.lErr, msg)
				return (False, msg, filename)
			new_parts.append(new_part)

			if reviewer is None:
				continue

			new_part['pk_intended_reviewer'] = reviewer
			success, data = new_part.save_payload()
			if not success:
				msg = 'cannot set reviewer to [%s]' % reviewer
				_log.Log(gmLog.lErr, msg)
				_log.Log(gmLog.lErr, str(data))
				return (False, msg, filename)

		return (True, '', new_parts)
	#--------------------------------------------------------
	def has_unreviewed_parts(self):
		cmd = u"select exists(select 1 from blobs.v_obj4doc_no_data where pk_doc=%s and not reviewed)"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return rows[0][0]
	#--------------------------------------------------------
	def set_reviewed(self, technically_abnormal=None, clinically_relevant=None):
		# FIXME: this is probably inefficient
		for part in self.get_parts():
			if not part.set_reviewed(technically_abnormal, clinically_relevant):
				return False
		return True
	#--------------------------------------------------------
	def set_primary_reviewer(self, reviewer=None):
		for part in self.get_parts():
			part['pk_intended_reviewer'] = reviewer
			success, data = part.save_payload()
			if not success:
				_log.Log(gmLog.lErr, 'cannot set reviewer to [%s]' % reviewer)
				_log.Log(gmLog.lErr, str(data))
				return False
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
	def __setitem__(self, attribute, value):
		if not self._payload[self._idx['is_user']]:
			return
		return gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#--------------------------------------------------------
	def set_translation(self, translation=None):
		if not self._payload[self._idx['is_user']]:
			return False

		rows, idx = gmPG2.run_rw_queries (
			queries = [
				{'cmd': u'select i18n.i18n(%s)', 'args': [self._payload[self._idx['type']]]},
				{'cmd': u'select i18n.upd_tx(%s, %s, (select lang from i18n.curr_lang where user = CURRENT_USER))',
				 'args': [self._payload[self._idx['type']], translation]
				}
			],
			return_data = True
		)
		if not rows[0][0]:
			_log.Log(gmLog.lErr, 'cannot set translation to [%s]' % translation)
			_log.Log(gmLog.lErr, str(data))
			return False

		return self.refetch_payload()		# FIXME: error handling ?
#============================================================
# convenience functions
#============================================================
def create_document(patient_id=None, document_type=None, encounter=None, episode=None):
	"""Returns new document instance or raises an exception.
	"""
	cmd1 = u"""insert into blobs.doc_med (fk_identity, fk_type, fk_encounter, fk_episode) VALUES (%s, %s, %s, %s)"""
	cmd2 = u"""select currval('blobs.doc_med_pk_seq')"""
	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd1, 'args': [patient_id, document_type, encounter, episode]},
			{'cmd': cmd2}
		]
	)
	doc_id = rows[0][0]
	doc = cMedDoc(aPK_obj = doc_id)
	return doc
#------------------------------------------------------------
def search_for_document(patient_id=None, type_id=None):
	"""Searches for documents with the given patient and type ID.

	No type ID returns all documents for the patient.
	"""
	# sanity checks
	if patient_id is None:
		_log.Log(gmLog.lErr, 'need patient id to create document')
		return None

	args = {'pat_id': patient_id, 'type_id': type_id}
	if type_id is None:
		cmd = u"SELECT pk from blobs.doc_med WHERE fk_identity=%(pat_id)s"
	else:
		cmd = u"SELECT pk from blobs.doc_med WHERE fk_identity=%(pat_id)s and fk_type=%(type_id)s"

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	docs = []
	for row in rows:
		docs.append(cMedDoc(row[0]))
	return docs
#------------------------------------------------------------
def get_document_types():
	rows, idx = gmPG2.run_ro_queries (
		queries = [{'cmd': u"SELECT * FROM blobs.v_doc_type"}],
		get_col_idx = True
	)
	doc_types = []
	for row in rows:
		row_def = {
			'pk_field': 'pk_doc_type',
			'idx': idx,
			'data': row
		}
		doc_types.append(cDocumentType(row = row_def))
	return doc_types
#------------------------------------------------------------
def create_document_type(document_type=None):
	# FIXME: handle case where doc type already exists
	cmd = u'select pk from blobs.doc_type where name=%s'
	rows, idx = gmPG2.run_ro_queries (
		queries = [{'cmd': cmd, 'args': [document_type]}]
	)
	if len(rows) == 0:
		cmd1 = u"insert into blobs.doc_type (name) values (%s)"
		cmd2 = u"select currval('blobs.doc_type_pk_seq')"
		rows, idx = gmPG2.run_rw_queries (
			queries = [
				{'cmd': cmd1, 'args': [document_type]},
				{'cmd': cmd2}
			]
		)
	return cDocumentType(aPK_obj = rows[0][0])
#------------------------------------------------------------
def delete_document_type(document_type=None):
	gmPG2.run_rw_queries (
		queries = [{
			'cmd': u'delete from blobs.doc_type where pk=%s and is_user is True',
			'args': [document_type['pk_doc_type']]
		}]
	)
	return True
#------------------------------------------------------------
def get_ext_ref():
	"""This needs *considerably* more smarts."""
	# set up temp file environment for creating unique random directory
	tempfile.template = ''
	# create temp dir name
	dirname = tempfile.mktemp(suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()))
	# extract name for dir
	path, doc_ID = os.path.split(dirname)
	return doc_ID
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	#--------------------------------------------------------
	def test_doc_types():

		print "----------------------"
		print "listing document types"
		print "----------------------"

		for dt in get_document_types():
			print dt

		print "------------------------------"
		print "testing document type handling"
		print "------------------------------"

		dt = create_document_type(document_type = 'dummy doc type for unit test 1')
		print "created:", dt

		dt['type'] = 'dummy doc type for unit test 2'
		dt.save_payload()
		print "changed base name:", dt

		dt.set_translation(translation = 'Dummy-Dokumenten-Typ fuer Unit-Test')
		print "translated:", dt

		print "deleted:", delete_document_type(document_type = dt)

		return
	#--------------------------------------------------------
	def test_adding_doc_part():

		print "-----------------------"
		print "testing document import"
		print "-----------------------"

		docs = search_for_document(patient_id=12)
		doc = docs[0]
		print "adding to doc:", doc

		fname = sys.argv[1]
		print "adding from file:", fname
		part = doc.add_part(file=fname)
		print "new part:", part

		return
	#--------------------------------------------------------
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	_log.SetAllLogLevels(gmLog.lData)

	test_doc_types()
	test_adding_doc_part()

#	print get_ext_ref()

#	doc_folder = cDocumentFolder(aPKey=12)

#	photo = doc_folder.get_latest_mugshot()
#	print type(photo), photo

#	docs = doc_folder.get_documents()
#	for doc in docs:
#		print type(doc), doc

#============================================================
# $Log: gmMedDoc.py,v $
# Revision 1.81  2006-10-08 15:07:11  ncq
# - convert to gmPG2
# - drop blobs.xlnk_identity support
# - use cBusinessDBObject
# - adjust queries to schema
#
# Revision 1.80  2006/09/30 11:38:08  ncq
# - remove support for blobs.xlnk_identity
#
# Revision 1.79  2006/09/28 14:36:10  ncq
# - fix search_for_doc(), it used the row, not the value for document instantiation
#
# Revision 1.78  2006/09/21 19:23:12  ncq
# - cast '' to bytea when adding a dummy document part
#
# Revision 1.77  2006/09/02 21:22:10  ncq
# - return new parts from add_parts_from_files()
# - cMedDoc.update_data() needs fixing
# - forward port test suite improvement and cMedDoc instantiation fix from rel-0-2-patches branch
#
# Revision 1.76  2006/09/01 14:39:19  ncq
# - add FIXME
#
# Revision 1.75  2006/07/10 21:15:07  ncq
# - add cDocumentType
# - get_document_types() now returns instances
# - add delete_document_type()
# - improved testing
#
# Revision 1.74  2006/07/07 12:06:08  ncq
# - return more data from get_document_types()
#
# Revision 1.73  2006/07/04 21:37:43  ncq
# - cleanup
# - add create_document_type()
#
# Revision 1.72  2006/07/01 13:10:13  ncq
# - fix __export() re encoding setting
#
# Revision 1.71  2006/07/01 11:23:35  ncq
# - cleanup
#
# Revision 1.70  2006/06/26 21:37:14  ncq
# - properly use explicit encoding setting in put/get
#   data for document objects
#
# Revision 1.69  2006/06/21 15:51:48  ncq
# - set_intended_reviewer() -> set_primary_reviewer()
#
# Revision 1.68  2006/06/18 22:43:21  ncq
# - missing %
#
# Revision 1.67  2006/06/18 13:19:55  ncq
# - must update XMIN after update_data(_from_file())
# - use run_commit2() instead of run_commit()
#
# Revision 1.66  2006/06/12 20:48:48  ncq
# - add missing cleanup() to folder class
#
# Revision 1.65  2006/06/07 22:07:14  ncq
# - use run_commit2() only to ensure better transaction handling
# - fix one suspicious faulty handling of run_commit2() return values
# - add a "del new_part" just for good measure
#
# Revision 1.64  2006/06/07 20:22:01  ncq
# - must be pk_intended_reviewer
#
# Revision 1.63  2006/06/05 21:52:00  ncq
# - fix one double %
#
# Revision 1.62  2006/05/31 09:45:19  ncq
# - fix doc part saving/locking - reference to PK was wrong, I wonder how it ever worked
# - add get_containing_document() and set_intended_reviewer() to cMedDocPart
# - make pk_episode in cMedDoc editable
# - some more error checking
#
# Revision 1.61  2006/05/28 15:25:50  ncq
# - add "episode" field to doc_part
#
# Revision 1.60  2006/05/25 22:11:36  ncq
# - use blobs.v_obj4doc_no_data
#
# Revision 1.59  2006/05/20 18:29:21  ncq
# - allow setting reviewer in add_parts_from_files()
#
# Revision 1.58  2006/05/16 15:47:19  ncq
# - various small fixes re setting review status
#
# Revision 1.57  2006/05/08 16:33:02  ncq
# - remove useless order by's
# - add cMedDoc.has_unreviewed_parts()
#
# Revision 1.56  2006/05/01 18:43:50  ncq
# - handle encounter/episode in create_document()
#
# Revision 1.55  2006/02/13 08:11:28  ncq
# - doc-wide set_reviewed() must be in cMedDoc, not cDocumentFolder
# - add cMedDocPart.get_reviews()
#
# Revision 1.54  2006/02/05 14:36:01  ncq
# - intended reviewer now must be staff, not identity
#
# Revision 1.53  2006/02/05 14:27:13  ncq
# - add doc-wide set_reviewed() wrapper to cMedDoc
# - handle review-related fields to cMedDocPart
# - add set_reviewed() to cMedDocPart
#
# Revision 1.52  2006/01/27 22:16:14  ncq
# - add reviewed/signed to cMedDocPart
#
# Revision 1.51  2006/01/22 18:07:34  ncq
# - set client encoding to sql_ascii where necessary for blobs handling
#
# Revision 1.50  2006/01/18 23:07:16  ncq
# - cleanup
#
# Revision 1.49  2006/01/17 22:01:35  ncq
# - now really sort by date
#
# Revision 1.48  2006/01/17 20:20:26  ncq
# - implement get_ext_ref()
#
# Revision 1.47  2006/01/16 19:33:46  ncq
# - need to "reset client_encoding" on 8.0, too
#
# Revision 1.46  2006/01/16 19:23:32  ncq
# - use reset_encoding on blobs more generously
#
# Revision 1.45  2006/01/15 16:12:05  ncq
# - explicitely use PgUnQuoteBytea() on the concatenated
#   string when getting Bytea in pieces
#
# Revision 1.44  2006/01/15 15:06:42  ncq
# - return newest-first from get_doc_list()
#
# Revision 1.43  2006/01/15 14:58:59  ncq
# - return translations from get_document_types()
#
# Revision 1.42  2006/01/15 14:41:21  ncq
# - add missing None in call to run_ro_query()
#
# Revision 1.41  2006/01/14 23:24:00  shilbert
# - return doc_type and coresponding primary key not just doc_type string
#
# Revision 1.40  2006/01/13 13:48:15  ncq
# - brush up adding document parts
#
# Revision 1.39  2006/01/11 22:43:36  ncq
# - yet another missed id -> pk
#
# Revision 1.38  2006/01/11 13:13:53  ncq
# - id -> pk
#
# Revision 1.37  2006/01/09 22:06:09  ncq
# - aPKey -> aPK_obj
#
# Revision 1.36  2006/01/09 10:42:21  ncq
# - yet another missed dem schema qualification
#
# Revision 1.35  2006/01/01 17:39:39  ncq
# - require document type in create_document()
#
# Revision 1.34  2006/01/01 16:08:08  ncq
# - proper scoping of functions
#
# Revision 1.33  2006/01/01 15:39:50  ncq
# - some missing blobs.
#
# Revision 1.32  2005/12/14 17:00:01  ncq
# - add add_document() and add_description() to cMedDoc
# - fix missing ''
# - add gmMedDoc.get_ext_ref()
#
# Revision 1.31  2005/12/13 21:46:07  ncq
# - enhance cMedDoc.add_part() so it can load data from a file
# - add cMedDoc.add_parts_from_files()
#
# Revision 1.30  2005/11/27 09:23:07  ncq
# - added get_document_types()
#
# Revision 1.29  2005/11/01 08:50:24  ncq
# - blobs are in blobs. schema now
#
# Revision 1.28  2005/02/12 13:56:49  ncq
# - identity.id -> identity.pk
#
# Revision 1.27  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.26  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.25  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.24  2004/10/11 19:46:52  ncq
# - properly VOify deriving from cBusinessDBObject
# - cMedObj -> cMedDocPart
# - cDocumentFolder.get_documents()
# - cMedDoc.get_descriptions() where max_lng=None will fetch entire description
# - comments, cleanup
#
# Revision 1.23  2004/09/28 12:20:16  ncq
# - cleanup/robustify
# - add get_latest_mugshot()
#
# Revision 1.22  2004/06/01 07:50:01  ncq
# - error checking, optimizing, cleanup
# - adaptation to ClinItem pending
#
# Revision 1.21  2004/03/20 11:16:16  ncq
# - v_18n_doc_type is no more, use _(doc_type.name)
#
# Revision 1.20  2004/03/07 23:49:54  ncq
# - add cDocumentFolder
#
# Revision 1.19  2004/03/04 19:46:53  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.18  2004/03/03 14:41:49  ncq
# - cleanup
# - FIXME: write gmDocumentRecord_SQL
#
# Revision 1.17  2004/03/03 05:24:01  ihaywood
# patient photograph support
#
# Revision 1.16  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.15  2004/01/26 18:19:55  ncq
# - missing :
#
# Revision 1.14  2004/01/18 21:42:17  ncq
# - extra : removed
#
# Revision 1.13  2003/12/29 16:20:28  uid66147
# - use gmPG.run_ro_query/run_commit instead of caching connections ourselves
# - but do establish our own rw connection even for reads since escaping bytea
#   over a client_encoding != C breaks transmitted binaries
# - remove deprecated __get/setitem__ API
# - sane create_document/object helpers
#
# Revision 1.12  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.11  2003/06/27 16:04:13  ncq
# - no ; in SQL
#
# Revision 1.10  2003/06/26 21:26:15  ncq
# - cleanup re (cmd,args) and %s; quoting bug
#
# Revision 1.9  2003/04/20 15:32:15  ncq
# - removed __run_query helper
# - call_viewer_on_file moved to gmMimeLib
#
# Revision 1.8  2003/04/18 22:33:44  ncq
# - load document descriptions from database
#
# Revision 1.7  2003/03/31 01:14:22  ncq
# - fixed KeyError on metadata[]
#
# Revision 1.6  2003/03/30 00:18:32  ncq
# - typo
#
# Revision 1.5  2003/03/25 12:37:20  ncq
# - use gmPG helpers
# - clean up code
# - __update_data/metadata - this worked for moving between databases !
#
# Revision 1.4  2003/02/26 23:22:04  ncq
# - metadata write support
#
