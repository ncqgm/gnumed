"""This module encapsulates a document stored in a GnuMed database.

metadata layout:

self.__metadata		{}
 |
 >- 'id'			""
 |
 >- 'type ID'		""
 |
 >- 'type'			""
 |
 >- 'comment'		""
 |
 >- 'date'			mxDateTime
 |
 >- 'reference'		""
 |
 >- 'description'	""
 |
 >- 'patient id'	""
 |
 `- 'objects'		{}
  |
  `- id				{}
   |
   >- 'file name'	""		(on the local disc, fully qualified)
   |
   >- 'index'		""		(... into page sequence)
   |
   >- 'size'		""		(in bytes)
   |
   `- 'comment' 	""

@copyright: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedDoc.py,v $
# $Id: gmMedDoc.py,v 1.20 2004-03-07 23:49:54 ncq Exp $
__version__ = "$Revision: 1.20 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, tempfile, os, shutil, os.path, types
from cStringIO import StringIO

from Gnumed.pycommon import gmLog, gmPG, gmExceptions

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
#============================================================
class cDocumentFolder:

	def __init__(self, aPKey = None):
		"""Fails if

		- patient referenced by aPKey does not exist
		"""
		self.id_patient = aPKey			# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database." % aPKey

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
#		if not self._register_interests():
#			raise gmExceptions.ConstructorError, "cannot register signal interests"

		_log.Log(gmLog.lData, 'Instantiated document folder for patient [%s].' % self.id_patient)
	#--------------------------------------------------------
	def __del__(self):
		pass
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		# patient in demographic database ?
		cmd = "select exists(select id from identity where id = %s)"
		result = gmPG.run_ro_query('personalia', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in demographic database' % self.id_patient)
			return None
		if len(result) == 0:
			_log.Log(gmLog.lErr, "no patient [%s] in demographic database" % self.id_patient)
			return None
		# patient linked in our local documents database ?
		cmd = "select exists(select pk from xlnk_identity where xfk_identity = %s)"
		result = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in documents database' % self.id_patient)
			return None
		if not result[0][0]:
			_log.Log(gmLog.lInfo, "no patient [%s] in documents database" % self.id_patient)
			cmd1 = "insert into xlnk_identity (xfk_identity, pupic) values (%s, %s)"
			cmd2 = "select currval('xlnk_identity_pk_seq')"
			status = gmPG.run_commit('blobs', [
				(cmd1, [self.id_patient, self.id_patient]),
				(cmd2, [])
			])
			if status is None:
				_log.Log(gmLog.lErr, 'cannot insert patient [%s] into documents database' % self.id_patient)
				return None
			if status != 1:
				_log.Log(gmLog.lData, 'inserted patient [%s] into documents database with local id [%s]' % (self.id_patient, status[0][0]))
		return (1==1)
	#--------------------------------------------------------
	# API
	#--------------------------------------------------------
	def get_mugshot_list(self, latest_only=1):
		if latest_only:
			cmd = "select pk_doc, pk_obj from v_latest_mugshot where pk_patient=%s"
		else:
			cmd = """
				select dm.id, dobj.id
				from
					doc_med dm
					doc_obj dobj
				where
					dm.type = (select id from doc_type where name='patient photograph') and
					dm.patient_id=%s and
					and dobj.doc_id = dm.id
			"""
		rows = gmPG.run_ro_query('blobs', cmd, None, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load mugshot list for patient [%s]' % self.id_patient)
			return None
		return rows
	#--------------------------------------------------------
	def get_doc_list(self, doc_type = None):
		if doc_type is None:
			cmd = "select id from doc_med where patient_id=%(ID)s"
			args = {'ID': self.id_patient}
		elif type(doc_type) == types.StringType:
			cmd = """
				select id
				from doc_med
				where
					patient_id=%(ID)s and
					type=(select id from doc_type where name=%(TYP)s)
				"""
			args = {'ID': self.id_patient, 'TYP': doc_type}
		else:
			cmd = """
				select id
				from doc_med
				where
					patient_id=%(ID)s and
					type=%(TYP)s
				"""
			args = {'ID': self.id_patient, 'TYP': doc_type}
		docs = gmPG.run_ro_query('blobs', cmd, None, args)
		if docs is None:
			_log.Log(gmLog.lErr, 'cannot load document list for patient [%s]' % self.id_patient)
			return None
		return docs
#============================================================
class gmMedObj:
	def __init__(self, aPKey):
		"""Fails if

		- no connection to database possible
		- document referenced by aPKey does not exist.
		"""
		# if the client sets an encoding other than the default we
		# will receive encoding-parsed data which isn't the binary
		# content we want, hence we need to get our own hard connection
		backend = gmPG.ConnectionPool()
		self.__rwconn = backend.GetConnection('blobs', readonly = 0)
		if self.__rwconn is None:
			raise gmExceptions.ConstructorError, 'cannot get r/w connection to service [blobs]'
		cmd = 'reset client_encoding'
		result = gmPG.run_ro_query(self.__rwconn, cmd)
		if result is None:
			_log.Log(gmLog.lErr, 'cannot reset client_encoding, BLOB download may fail')

		self.ID = aPKey			# == doc_obj.id == primary key
		if not self.__pkey_exists():
			raise gmExceptions.ConstructorError

		self.metadata = {}
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		cmd = "select exists(select id from doc_obj where id = %s )"
		result = gmPG.run_ro_query('blobs', cmd, None, self.ID)
		if result is None:
			_log.Log(gmLog.lErr, 'cannot verify that object [%s] exists' % self.ID)
			return None
		if not result[0][0]:
			_log.Log(gmLog.lErr, "no object with ID [%s] in database" % self.ID)
		return result[0][0]
	#--------------------------------------------------------
	def __del__(self):
		if self.__dict__.has_key('__rwconn'):
			self.__rwconn.close()
	#--------------------------------------------------------
	# retrieve data
	#--------------------------------------------------------
	def get_metadata(self):
		"""Get object level metadata."""
		cmd = "SELECT doc_id, seq_idx, comment, octet_length(data) FROM doc_obj WHERE id=%s"
		result = gmPG.run_ro_query('blobs', cmd, 0, self.ID) 
		if result is None:
			_log.Log(gmLog.lErr, 'cannot load object [%s] metadata' % self.ID)
			return None
		if len(result) is None:
			_log.Log(gmLog.lErr, 'no metadata available for object [%s]' % self.ID)
			return None
		self.metadata = {
			'id': self.ID,
			'document id': result[0][0],
			'sequence index': result[0][1],
			'comment': result[0][2],
			'size': result[0][3]
		}
		return self.metadata
	#--------------------------------------------------------
	def export_to_file(self, aTempDir = None, aChunkSize = 0):
		if self.get_metadata is None:
			_log.Log(gmLog.lErr, 'cannot load metadata')
			return None

		# if None -> use tempfile module default, else use given
		# path as base directory for temp files
		if not aTempDir is None:
			tempfile.tempdir = aTempDir
		tempfile.template = "gm-doc_obj-"

		# cDocument.metadata->objects->file name
		fname = tempfile.mktemp()
		aFile = open(fname, 'wb+')

		if self.__export (aFile, aChunkSize):
			aFile.close ()
			return fname
		else:
			aFile.close ()
			return None

	def export_to_string (self, aChunkSize = 0):
		"""
		Returns the document as a Python string
		WARNING: better have enough RAM for whatever it is!!!!
		"""
		aFile = StringIO ()
		if self.__export (aFile, aChunkSize):
			r = aFile.getvalue ()
			aFile.close ()
			return r
		else:
			aFile.close ()
			return None
	

	def __export (self, aFile, aChunkSize = 0):
		"""
		Internal helper, grabs data and writes it to
		the Python file object provided
		"""
		# Windoze sucks: it can't transfer objects of arbitrary size,
		# or maybe this is due to pyPgSQL ?
		# anyways, we need to split the transfer,
		# only possible if postgres >= 7.2
		if self.__rwconn.version < "7.2":
			max_chunk_size = 0
			_log.Log(gmLog.lWarn, 'PostgreSQL < 7.2 does not support substring() on bytea')
		else:
			max_chunk_size = aChunkSize
		_log.Log(gmLog.lData, "export chunk size is %s" % max_chunk_size)

		# a chunk size of 0 means: all at once
		if ((max_chunk_size == 0) or (self.metadata['size'] <= max_chunk_size)):
			_log.Log(gmLog.lInfo, "retrieving entire object at once")
			# retrieve object
			cmd = "SELECT data FROM doc_obj WHERE id=%s"
			data = gmPG.run_ro_query(self.__rwconn, cmd, None, self.ID)
			if data is None:
				_log.Log(gmLog.lErr, 'cannot retrieve BLOB [%s]' % self.ID)
				return None
			if len(data) == 0:
				_log.Log(gmLog.lErr, 'BLOB [%s] does not exist' % self.ID)
				return None
			if data[0][0] is None:
				_log.Log (gmLog.lErr, 'BLOB [%s] is NULL' % self.ID)
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))
			return 1

		# retrieve chunks
		needed_chunks, remainder = divmod(self.metadata['size'], max_chunk_size)
		_log.Log(gmLog.lData, "need %s chunks with a remainder of %s bytes" % (needed_chunks, remainder))
		for chunk_id in range(needed_chunks):
			_log.Log(gmLog.lData, "retrieving chunk %s" % (chunk_id+1))
			pos = (chunk_id*max_chunk_size) + 1
			cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE id=%s"
			data = gmPG.run_ro_query(self.__rwconn, cmd, None, pos, max_chunk_size, self.ID)
			if data is None:
				_log.Log(gmLog.lErr, 'cannot retrieve chunk [%s] of size [%s] from object [%s], try decreasing chunk size' % (chunk_id+1, max_chunk_size, self.ID))
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))

		# retrieve remainder
		if remainder > 0:
			_log.Log(gmLog.lData, "retrieving trailing bytes after chunks")
			pos = (needed_chunks*max_chunk_size) + 1
			cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE id=%s "
			data = gmPG.run_ro_query(self.__rwconn, cmd, pos, remainder, self.ID)
			if data is None:
				_log.Log(gmLog.lErr, 'cannot retrieve remaining [%s] bytes from object [%s]' % (remainder, self.ID), sys.exc_info())
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(data[0][0]))
		return 1
	#--------------------------------------------------------
	# store data
	#--------------------------------------------------------
	def update_data_from_file(self, fname):
		try:
			from pyPgSQL.PgSQL import PgBytea
		except ImportError:
			# FIXME
			_log.Log(gmLog.lPanic, 'need pyPgSQL')
			return None

		# read from file and convert (escape)
		if not os.path.exists(fname):
			_log.Log(gmLog.lErr, "[%s] does not exist" % fname)
			return None
		aFile = open(fname, "rb")
		img_data = str(aFile.read())
		aFile.close()
		img_obj = PgBytea(img_data)

		# insert the data
		cmd = "UPDATE doc_obj SET data=%s WHERE id=%s"
		result = gmPG.run_commit(self.__rwconn, [
			(cmd, [img_obj, self.ID])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot update object [%s] from file [%s]' (self.ID, fname))
			return None
		return 1
	#--------------------------------------------------------
	def update_data(self, data):
		try:
			from pyPgSQL.PgSQL import PgBytea
		except ImportError:
			# FIXME
			_log.Log(gmLog.lPanic, 'need pyPgSQL')
			return None
		# convert (escape)
		img_obj = PgBytea(data)

		# insert the data
		cmd = "UPDATE doc_obj SET data=%s WHERE id=%s"
		result = gmPG.run_commit(self.__rwconn, [
			(cmd, [img_obj, self.ID])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot update object [%s] from data' % self.ID)
			return None
		return 1
	#--------------------------------------------------------
	def update_metadata(self, data = None):
		if data is None:
			return None

		# make SET clause
		sets = []
		try:
			data['document id']
			sets.append("doc_id=%(document id)s")
		except KeyError: pass
		try:
			data['sequence index']
			sets.append("seq_idx=%(sequence index)s")
		except KeyError: pass
		try:
			data['comment']
			sets.append("comment=%(comment)s")
		except KeyError: pass

		set_clause = ', '.join(sets)

		# actually set it in the DB
		cmd =  "UPDATE doc_obj SET %s WHERE id=%(obj id)s" % set_clause
		data['obj id'] = self.ID
		result = gmPG.run_commit(self.__rwconn, [
			(cmd, [data])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot update metadata')
			return None
		return 1
#============================================================
class gmMedDoc:

	def __init__(self, aPKey, presume_exists=0):
		"""Fails if

		- no connection to database possible
		- document referenced by aPKey does not exist.
		"""
		self.ID = aPKey			# == doc_med.id == primary key
		if not presume_exists and not self.__pkey_exists():
			raise gmExceptions.ConstructorError, "No document with ID [%s] in database." % aPKey

		self.metadata = {}
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		cmd = "select exists(select id from doc_med where id=%s)"
		result = gmPG.run_ro_query('blobs', cmd, None, self.ID)
		if result is None:
			return None
		return result[0][0]
	#--------------------------------------------------------
	def __del__(self):
		pass
	#--------------------------------------------------------
	def get_descriptions(self, max_lng=250):
		"""Get document descriptions.

		- will return a list of strings
		"""
		cmd = "SELECT substring(text from 1 for %s) FROM doc_desc WHERE doc_id=%%s" % max_lng
		rows = gmPG.run_ro_query('blobs', cmd, None, self.ID)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load document [%s] descriptions' % self.ID)
			return [_('cannot load descriptions')]
		if len(rows) == 0:
			return [_('no descriptions available')]
		data = []
		for desc in rows:
			data.extend(desc)
		return data
	#--------------------------------------------------------
	def get_metadata(self):
		"""Document meta data loader for GnuMed compatible database."""
		cmd = """
SELECT
	dm.patient_id,
	dm.type,
	dm.comment,
	dm.date,
	dm.ext_ref,
	vdt.name
FROM
	doc_med dm,
	v_i18n_doc_type vdt
WHERE
	dm.id=%s and
	vdt.id = dm.type
"""
		rows = gmPG.run_ro_query('blobs', cmd, None, self.ID)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load document [%s] metadata' % self.ID)
			return None
		self.metadata['patient id'] = rows[0][0]
		self.metadata['type ID'] = rows[0][1]
		self.metadata['comment'] = rows[0][2]
		self.metadata['date'] = rows[0][3]
		self.metadata['reference'] = rows[0][4]
		self.metadata['type'] = rows[0][5]

		# get object level metadata for all objects of this document
		cmd = "SELECT id, comment, seq_idx, octet_length(data) FROM doc_obj WHERE doc_id=%s"
		rows = gmPG.run_ro_query('blobs', cmd, None, self.ID)
		if rows is None:
			_log.LogException('cannot load document [%s] metadata' % self.ID, sys.exc_info())
			return None
		self.metadata['objects'] = {}
		for row in rows:
			obj_id = row[0]
			# cDocument.metadata->objects->id->comment/index/size
			tmp = {'comment': row[1], 'index': row[2], 'size': row[3]}
			self.metadata['objects'][obj_id] = tmp

		return self.metadata
	#--------------------------------------------------------
	# storing data
	#--------------------------------------------------------
	def update_metadata(self, data = None):
		sets = []
		try:
			self.metadata['patient id'] = data['patient id']
			sets.append('patient_id=%(patient id)s')
		except KeyError: pass
		try:
			self.metadata['type ID'] = data['type ID']
			sets.append('type=%(type ID)s')
		except KeyError: pass
		try:
			self.metadata['comment'] = data['comment']
			sets.append('comment=%(comment)s')
		except KeyError: pass
		try:
			self.metadata['date'] = data['date']
			sets.append('date=%(date)s')
		except KeyError: pass
		try:
			self.metadata['reference'] = data['reference']
			sets.append('ext_ref=%(reference)s')
		except KeyError: pass

		set_clause = ', '.join(sets)
		cmd =  "UPDATE doc_med SET %s WHERE id=%%(obj id)s" % set_clause

		data['obj id'] = self.ID
		result =  gmPG.run_commit('blobs', [
			(cmd, [data])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot update metadata')
			return None
		return 1
#============================================================
def create_document(patient_id=None):
	"""
	None - failed
	not None - new document object
	"""
	# sanity checks
	if patient_id is None:
		_log.Log(gmLog.lErr, 'need patient id to create document')
		return None
	# insert document
	cmd1 = "INSERT INTO doc_med (patient_id) VALUES (%s)"
	cmd2 = "select currval('doc_med_id_seq')"
	result = gmPG.run_commit('blobs', [
		(cmd1, [patient_id]),
		(cmd2, [])
	])
	if result is None:
		_log.Log(gmLog.lErr, 'cannot create document for patient [%s]' % patient_id)
		return None
	doc_id = result[0][0]
	# and init new document object
	doc = gmMedDoc(aPKey = doc_id)
	return doc
#------------------------------------------------------------
def search_for_document (patient_id=None, type_id=None):
	"""Searches for documents with the given patient and type ID.

	No type ID returns all documents for the patient.
	"""
	# sanity checks
	if patient_id is None:
		_log.Log(gmLog.lErr, 'need patient id to create document')
		return None

	if type_id is None:
		cmd = "SELECT id from doc_med WHERE patient_id=%s"
		doc_ids = gmPG.run_ro_query('blobs', cmd, None, patient_id)
	else:
		cmd = "SELECT id from doc_med WHERE patient_id=%s and type=%s"
		doc_ids = gmPG.run_ro_query ('blobs', cmd, None, patient_id, type_id)
		
	if doc_ids is None:
		return []
	if len(doc_ids) == 0:
		_log.Log(gmLog.lInfo, "No documents found for person (ID [%s])." % patient_id)
		return []
	docs = []
	for doc_id in doc_ids:
		docs.append(gmMedDoc(doc_id, presume_exists=1)) # suppress pointless checking of primary key

	return docs
#------------------------------------------------------------
# define some document types that are programmatically useful
MUGSHOT=26
#============================================================
def create_object(doc_id):
	"""
	None - failed
	not None - new document object
	"""
	# sanity checks
	if doc_id is None:
		_log.Log(gmLog.lErr, 'need document id to create object')
		return None
	if isinstance (doc_id, gmMedDoc):
		doc_id = doc_id.ID
	# insert document
	cmd1 = "INSERT INTO doc_obj (doc_id) VALUES (%s)"
	cmd2 = "select currval('doc_obj_id_seq')"
	result = gmPG.run_commit('blobs', [
		(cmd1, [doc_id]),
		(cmd2, [])
	])
	if result is None:
		_log.Log(gmLog.lErr, 'cannot create object for document [%s]' % doc_id)
		return None
	obj_id = result[0][0]
	# and init new document object
	obj = gmMedObj(aPKey = obj_id)
	return obj
#============================================================
# $Log: gmMedDoc.py,v $
# Revision 1.20  2004-03-07 23:49:54  ncq
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
