"""This module encapsulates a document stored in a GnuMed database.

@copyright: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedDoc.py,v $
# $Id: gmMedDoc.py,v 1.58 2006-05-16 15:47:19 ncq Exp $
__version__ = "$Revision: 1.58 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, tempfile, os, shutil, os.path, types, time
from cStringIO import StringIO

from Gnumed.pycommon import gmLog, gmPG, gmExceptions, gmBusinessDBObject

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
		self.id_patient = aPKey			# == identity.pk == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with PK [%s] in database." % aPKey

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
#		if not self._register_interests():
#			raise gmExceptions.ConstructorError, "cannot register signal interests"

		_log.Log(gmLog.lData, 'instantiated document folder for patient [%s]' % self.id_patient)
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		# patient in demographic database ?
		cmd = "select exists(select pk from dem.identity where pk = %s)"
		result = gmPG.run_ro_query('personalia', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in demographic database' % self.id_patient)
			return None
		if len(result) == 0:
			_log.Log(gmLog.lErr, "no patient [%s] in demographic database" % self.id_patient)
			return None
		# patient linked in our local documents database ?
		cmd = "select exists(select pk from blobs.xlnk_identity where xfk_identity = %s)"
		result = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in documents database' % self.id_patient)
			return None
		if not result[0][0]:
			_log.Log(gmLog.lInfo, "no patient [%s] in documents database" % self.id_patient)
			cmd1 = "insert into blobs.xlnk_identity (xfk_identity, pupic) values (%s, %s)"
			cmd2 = "select currval('blobs.xlnk_identity_pk_seq')"
			status = gmPG.run_commit('blobs', [
				(cmd1, [self.id_patient, self.id_patient]),
				(cmd2, [])
			])
			if status is None:
				_log.Log(gmLog.lErr, 'cannot insert patient [%s] into documents database' % self.id_patient)
				return None
			if status != 1:
				_log.Log(gmLog.lData, 'inserted patient [%s] into documents database with local id [%s]' % (self.id_patient, status[0][0]))
		return True
	#--------------------------------------------------------
	# API
	#--------------------------------------------------------
	def get_latest_mugshot(self):
		cmd = "select pk_obj from blobs.v_latest_mugshot where pk_patient=%s"
		rows = gmPG.run_ro_query('blobs', cmd, None, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'error load latest mugshot for patient [%s]' % self.id_patient)
			return None
		if len(rows) == 0:
			_log.Log(gmLog.lInfo, 'no mugshots available for patient [%s]' % self.id_patient)
			return None
		try:
			mugshot = cMedDocPart(aPK_obj=rows[0][0])
		except gmExceptions.ConstructorError, err:
			_log.LogException(err, sys.exc_info(), verbose=0)
			return None
		return mugshot
	#--------------------------------------------------------
	def get_mugshot_list(self, latest_only=1):
		if latest_only:
			cmd = "select pk_doc, pk_obj from blobs.v_latest_mugshot where pk_patient=%s"
		else:
			cmd = """
				select dm.pk, dobj.pk
				from
					blobs.doc_med dm
					blobs.doc_obj dobj
				where
					dm.type = (select pk from blobs.doc_type where name='patient photograph') and
					dm.patient_id=%s and
					and dobj.doc_id = dm.pk
				limit 1
			"""
		rows = gmPG.run_ro_query('blobs', cmd, None, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load mugshot list for patient [%s]' % self.id_patient)
			return None
		return rows
	#--------------------------------------------------------
	def get_doc_list(self, doc_type=None):
		"""return flat list of document IDs"""
		args = {
			'ID': self.id_patient,
			'TYP': doc_type
		}
		# FIXME: might have to order by on modified_when, date is a string
		if doc_type is None:
			cmd = """select pk from blobs.doc_med where patient_id=%(ID)s"""
		elif type(doc_type) == types.StringType:
			cmd = """
select dm.pk
from blobs.doc_med dm
where
	dm.patient_id = %(ID)s and
	dm.type = (select pk from blobs.doc_type where name=%(TYP)s)"""
		else:
			cmd = """
select dm.pk
from blobs.doc_med dm
where
	dm.patient_id = %(ID)s and
	dm.type = %(TYP)s"""
		rows = gmPG.run_ro_query('blobs', cmd, None, args)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load document list for patient [%s]' % self.id_patient)
			return None
		if len(rows) == 0:
			return []
		doc_ids = []
		for row in rows:
			doc_ids.append(row[0])
		return doc_ids
	#--------------------------------------------------------
	def get_documents(self, doc_type=None):
		"""Return list of documents."""
		doc_ids = self.get_doc_list(doc_type=doc_type)
		if doc_ids is None:
			return None
		docs = []
		for doc_id in doc_ids:
			try:
				docs.append(cMedDoc(aPK_obj=doc_id))
			except gmExceptions.ConstructorError:
				_log.LogException('document error on [%s] for patient [%s]' % (doc_id, self.id_patient), sys.exc_info())
				continue
		return docs
	#--------------------------------------------------------
	def add_document(self, document_type=None, encounter=None, episode=None):
		return create_document(patient_id=self.id_patient, document_type=document_type, encounter=encounter, episode=episode)
#============================================================
class cMedDocPart(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one part of a medical document."""

	_service = 'blobs'

	_cmd_fetch_payload = """
		select
			pk_patient,
			pk_obj,
			seq_idx,
			date_generated,
			type,
			l10n_type,
			size,
			ext_ref,
			doc_comment,
			obj_comment,
			reviewed,
			reviewed_by_you,
			reviewed_by_intended_reviewer,
			pk_doc,
			pk_type,
			pk_intended_reviewer,
			xmin_doc_obj
		from blobs.v_obj4doc
		where pk_obj=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from blobs.doc_obj where pk=%(pk_obj)s and xmin=%(xmin_doc_obj)s for update"""
	]
	_cmds_store_payload = [
		"""update blobs.doc_obj set
				seq_idx=%(seq_idx)s,
				comment=%(obj_comment)s,
				fk_intended_reviewer=%(pk_intended_reviewer)s
			where pk=%(pk_doc)s""",
		"""select xmin_doc_obj from blobs.v_obj4doc where pk_obj = %(pk_doc)s"""
	]
	_updatable_fields = [
		'seq_idx',
		'obj_comment',
		'fk_reviewer'
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
		backend = gmPG.ConnectionPool()
		self.__conn = backend.GetConnection('blobs', readonly = 0)
		if self.__conn is None:
			_log.Log(gmLog.lErr, 'cannot get r/w connection to service [blobs]')
			return None
		# this shouldn't actually, really be necessary
		if self.__conn.version < '8.1':
			cmd = 'set client_encoding to "sql_ascii"'
			result = gmPG.run_ro_query(self.__conn, cmd)
		else:
			print "****************************************************"
			print "*** if exporting BLOBs suddenly fails and        ***"
			print "*** you are running PostgreSQL >= 8.1 please     ***"
			print "*** mail a bug report to Karsten.Hilbert@gmx.net ***"
			print "****************************************************"

		# Windoze sucks: it can't transfer objects of arbitrary size,
		# or maybe this is due to pyPgSQL ?
		# anyways, we need to split the transfer,
		# however, only possible if postgres >= 7.2
		if self.__conn.version < '7.2':
			max_chunk_size = 0
			_log.Log(gmLog.lWarn, 'PostgreSQL < 7.2 does not support substring() on bytea')
		else:
			max_chunk_size = aChunkSize

		# a chunk size of 0 means: all at once
		if ((max_chunk_size == 0) or (self._payload[self._idx['size']] <= max_chunk_size)):
			# retrieve binary field
			cmd = "SELECT data FROM blobs.doc_obj WHERE pk=%s"
			data = gmPG.run_ro_query(self.__conn, cmd, None, self.pk_obj)
			if data is None:
				_log.Log(gmLog.lErr, 'cannot retrieve BLOB [%s]' % self.pk_obj)
				return None
			if len(data) == 0:
				_log.Log(gmLog.lErr, 'BLOB [%s] does not exist' % self.pk_obj)
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))
			return True

		# retrieve chunks
		# FIXME: does this not have the danger of cutting up multi-byte escape sequences ?
		needed_chunks, remainder = divmod(self._payload[self._idx['size']], max_chunk_size)
		_log.Log(gmLog.lData, "%s chunks of %s bytes, remainder of %s bytes" % (needed_chunks, max_chunk_size, remainder))
		for chunk_id in range(needed_chunks):
			pos = (chunk_id*max_chunk_size) + 1
			cmd = "SELECT substring(data from %s for %s) FROM blobs.doc_obj WHERE pk=%s"
			data = gmPG.run_ro_query(self.__conn, cmd, None, pos, max_chunk_size, self.pk_obj)
			if data is None:
				_log.Log(gmLog.lErr, 'cannot retrieve chunk [%s/%s], size [%s], doc part [%s], try decreasing chunk size' % (chunk_id+1, needed_chunks, max_chunk_size, self.pk_obj))
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))

		# retrieve remainder
		if remainder > 0:
			_log.Log(gmLog.lData, "retrieving trailing bytes after chunks")
			pos = (needed_chunks*max_chunk_size) + 1
			cmd = "SELECT substring(data from %s for %s) FROM blobs.doc_obj WHERE pk=%s "
			data = gmPG.run_ro_query(self.__conn, cmd, None, pos, remainder, self.pk_obj)
			if data is None:
				_log.Log(gmLog.lErr, 'cannot retrieve remaining [%s] bytes from doc part [%s]' % (remainder, self.pk_obj), sys.exc_info())
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))

		return 1
	#--------------------------------------------------------
	def get_reviews(self):
		cmd = """
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
;"""
		data = gmPG.run_ro_query('blobs', cmd, None, self.pk_obj)
		if data is None:
			_log.Log(gmLog.lErr, 'cannot retrieve reviews for doc object [%s]' %  self.pk_obj)
			return None
		return data
	#--------------------------------------------------------
	# store data
	#--------------------------------------------------------
	def update_data_from_file(self, fname=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.Log(gmLog.lErr, '[%s] is not a readable file' % fname)
			return False

		from pyPgSQL.PgSQL import PgBytea

		# read from file and convert (escape)
		aFile = open(fname, "rb")
		img_data = str(aFile.read())
		aFile.close()
		img_obj = PgBytea(img_data)
		del(img_data)

		# insert the data
		cmd1 = 'set client_encoding to "sql_ascii"'			# actually shouldn't be necessary > 7.3
		cmd2 = "UPDATE blobs.doc_obj SET data=%s WHERE pk=%s"
		result = gmPG.run_commit2 (
			link_obj = 'blobs',
			queries = [
				(cmd1, []),
				(cmd2, [img_obj, self.pk_obj])
			]
		)
		if result is None:
			_log.Log(gmLog.lErr, 'cannot update doc part [%s] from file [%s]' (self.pk_obj, fname))
			return False
		return True
	#--------------------------------------------------------
	def update_data(self, data):
		from pyPgSQL.PgSQL import PgBytea

		# convert (escape)
		img_obj = PgBytea(data)

		# insert the data
		cmd1 = 'set client_encoding to "sql_ascii"'			# actually shouldn't be necessary > 7.3
		cmd2 = "UPDATE blobs.doc_obj SET data=%s WHERE pk=%s"
		result = gmPG.run_commit('blobs', [
			(cmd1, []),
			(cmd2, [img_obj, self.pk_obj])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot update doc part [%s] from data' % self.pk_obj)
			return False
		return True
	#--------------------------------------------------------
	def set_reviewed(self, technically_abnormal=None, clinically_relevant=None):
		# row already there ?
		cmd = """
select pk
from blobs.reviewed_doc_objs
where
	fk_reviewed_row = %s and
	fk_reviewer = (select pk from dem.staff where db_user=current_user)"""
		rows = gmPG.run_ro_query('blobs', cmd, None, self.pk_obj)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get reviewed status on doc part [%s]' % self.pk_obj);
			return False

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
			pk_row = rows[0][0]
			args = {
				'abnormal': technically_abnormal,
				'relevant': clinically_relevant,
				'pk_row': pk_row
			}
			cmd = """
update blobs.reviewed_doc_objs set
	is_technically_abnormal = %(abnormal)s,
	clinically_relevant = %(relevant)s
where
	pk=%%(pk_row)s
"""
		success, data = gmPG.run_commit2 (
			link_obj = 'blobs',
			queries = [(cmd, [args])]
		)
		if not success:
			_log.Log(gmLog.lErr, 'cannot set reviewed status on doc part [%s]' % self.pk_obj)
			return False

		return True
#============================================================
class cMedDoc(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one medical document."""

	_service = 'blobs'

	_cmd_fetch_payload = """select *, xmin_doc_med from blobs.v_doc_med where pk_doc=%s"""

	_cmds_lock_rows_for_update = [
		"""select 1 from blobs.doc_med where pk=%(pk_doc)s and xmin=%(xmin_doc_med)s for update"""
	]

	_cmds_store_payload = [
		"""update blobs.doc_med set
				type=%(pk_type)s,
				comment=%(comment)s,
				date=%(date)s,
				ext_ref=%(ext_ref)s
			where pk=%(pk_doc)s""",
		"""select xmin_doc_med from blobs.v_doc_med where pk_doc=%(pk_doc)s"""
		]

	_updatable_fields = [
		'pk_type',
		'comment',
		'date',
		'ext_ref'
	]
	#--------------------------------------------------------
	def get_descriptions(self, max_lng=250):
		"""Get document descriptions.

		- will return a list of strings
		"""
		if max_lng is None:
			cmd = "SELECT text FROM blobs.doc_desc WHERE doc_id=%s"
		else:
			cmd = "SELECT substring(text from 1 for %s) FROM blobs.doc_desc WHERE doc_id=%%s" % max_lng
		rows = gmPG.run_ro_query('blobs', cmd, None, self.pk_obj)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load document [%s] descriptions' % self.pk_obj)
			return [_('cannot load descriptions')]
		if len(rows) == 0:
			return [_('no descriptions available')]
		data = []
		for desc in rows:
			data.extend(desc)
		return data
	#--------------------------------------------------------
	def add_description(self, description):
		cmd = "insert into blobs.doc_desc (doc_id, text) values (%s, %s)"
		return gmPG.run_commit2 (
			link_obj = 'blobs',
			queries = [(cmd, [self.pk_obj, str(description)])]
		)
	#--------------------------------------------------------
	def get_parts(self):
		cmd = "select pk_obj from blobs.v_obj4doc where pk_doc=%s"
		rows = gmPG.run_ro_query('blobs', cmd, None, self.pk_obj)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get parts belonging to document [%s]' % self.pk_obj)
			return None
		parts = []
		for row in rows:
			try:
				parts.append(cMedDocPart(aPK_obj=row[0]))
			except ConstructorError, msg:
				_log.LogException(msg, sys.exc_info())
				continue
		return parts
	#--------------------------------------------------------
	def add_part(self, file=None):
		# create dummy part
		cmd1 = """
insert into blobs.doc_obj (doc_id, fk_intended_reviewer, data, seq_idx)
VALUES (
	%(doc_id)s,
	(select pk_staff from dem.v_staff where db_user=CURRENT_USER),
	'',
	(select coalesce(max(seq_idx)+1, 1) from blobs.doc_obj where doc_id=%(doc_id)s)
)"""
		cmd2 = "select currval('blobs.doc_obj_pk_seq')"
		result = gmPG.run_commit('blobs', [
			(cmd1, [{'doc_id': self.pk_obj}]),
			(cmd2, [])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot create part for document [%s]' % self.pk_obj)
			return None
		# init document part instance
		part_pk = result[0][0]
		new_part = cMedDocPart(aPK_obj = part_pk)
		if not new_part.update_data_from_file(fname=file):
			_log.Log(gmLog.lErr, 'cannot import binary data from [%s] into document part' % file)
			cmd = "delete from blobs.doc_obj where pk = %s"
			result = gmPG.run_commit('blobs', [
				(cmd, [part_pk])
			])
			if result is None:
				_log.Log(gmLog.lErr, 'cannot delete dummy part [%s] of medical document [%s]' % (part_pk, self.pk_obj))
			return None
		return new_part
	#--------------------------------------------------------
	def add_parts_from_files(self, files=None):
		for filename in files:
			new_part = self.add_part(file=filename)
			if new_part is None:
				msg = 'cannot instantiate document part object'
				_log.Log(gmLog.lErr, msg)
				return (False, msg, filename)
		return (True, '', '')
	#--------------------------------------------------------
	def has_unreviewed_parts(self):
		cmd = "select exists(select 1 from blobs.v_obj4doc_no_data where pk_doc=%s and not reviewed)"
		rows = gmPG.run_ro_query('blobs', cmd, None, self.pk_obj)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot check document [%s] for unreviewed parts' % self.pk_obj)
			return None
		# FIXME: this does not detect the document having disappeared which would also return False
		return rows[0][0]
	#--------------------------------------------------------
	def set_reviewed(self, technically_abnormal=None, clinically_relevant=None):
		# FIXME: this is probably inefficient
		for part in self.get_parts():
			if not part.set_reviewed(technically_abnormal, clinically_relevant):
				return False
		return True
#============================================================
# convenience functions
#============================================================
def create_document(patient_id=None, document_type=None, encounter=None, episode=None):
	"""
	None - failed
	not None - new document class instance
	"""
	# insert document
	cmd1 = """insert into blobs.doc_med (patient_id, type, fk_encounter, fk_episode) VALUES (%s, %s, %s, %s)"""
	cmd2 = """select currval('blobs.doc_med_pk_seq')"""
	result = gmPG.run_commit('blobs', [
		(cmd1, [patient_id, document_type, encounter, episode]),
		(cmd2, [])
	])
	if result is None:
		_log.Log(gmLog.lErr, 'cannot create document for patient [%s]' % patient_id)
		return None
	doc_id = result[0][0]
	# and init new document instance
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

	if type_id is None:
		cmd = "SELECT pk from blobs.doc_med WHERE patient_id=%s"
		doc_ids = gmPG.run_ro_query('blobs', cmd, None, patient_id)
	else:
		cmd = "SELECT pk from blobs.doc_med WHERE patient_id=%s and type=%s"
		doc_ids = gmPG.run_ro_query ('blobs', cmd, None, patient_id, type_id)
		
	if doc_ids is None:
		return []
	if len(doc_ids) == 0:
		_log.Log(gmLog.lInfo, "No documents found for person (ID [%s])." % patient_id)
		return []
	docs = []
	for doc_id in doc_ids:
		docs.append(cMedDoc(doc_id, presume_exists=1)) # suppress pointless checking of primary key

	return docs
#------------------------------------------------------------
def get_document_types():
    cmd = "SELECT pk_doc_type, l10n_type FROM blobs.v_doc_type"
    rows = gmPG.run_ro_query('blobs', cmd)
    if rows is None:
        _log.Log(gmLog.lErr, 'cannot retrieve document types')
        return []
    return rows
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
	_log.SetAllLogLevels(gmLog.lData)

	print get_ext_ref()

	print get_document_types()

	doc_folder = cDocumentFolder(aPKey=12)

	photo = doc_folder.get_latest_mugshot()
	print type(photo), photo

	docs = doc_folder.get_documents()
	for doc in docs:
		print type(doc), doc

#============================================================
# $Log: gmMedDoc.py,v $
# Revision 1.58  2006-05-16 15:47:19  ncq
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
