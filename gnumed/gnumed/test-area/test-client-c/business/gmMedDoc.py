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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/business/Attic/gmMedDoc.py,v $
# $Id: gmMedDoc.py,v 1.1 2003-10-23 06:02:38 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, tempfile, os, shutil, os.path

if __name__ == '__main__':
	sys.path.append(os.path.join('..', 'python-common'))

import gmLog
_log = gmLog.gmDefLog

import gmPG
from gmExceptions import ConstructorError
#============================================================
class gmMedObj:
	def __init__(self, aPKey):
		"""Fails if

		- no connection to database possible
		- document referenced by aPKey does not exist.
		"""
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('blobs')
		self.__rwconn = None

		self.ID = aPKey			# == identity.id == primary key
		if not self.__pkey_exists():
			raise gmExceptions.ConstructorError

		self.filename = None
		self.metadata = {}
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self.__defconn.cursor()
		cmd = "select exists(select id from doc_obj where id = %s )"
		if not gmPG.run_query(curs, cmd, self.ID):
			curs.close()
			return None

		res = curs.fetchone()[0]
		curs.close()
		if not res:
			_log.Log(gmLog.lErr, "No document with ID [%s] in database." % self.ID)
		return res
	#--------------------------------------------------------
	def __del__(self):
		self.__backend.ReleaseConnection('blobs')
		if self.__rwconn is not None:
			self.__rwconn.close()
	#--------------------------------------------------------
	# retrieve data
	#--------------------------------------------------------
	def __getitem__(self, item):
		if item == 'filename':
			return self.filename
		if item == 'metadata':
			self.__fetch_metadata()
			return self.metadata
	#--------------------------------------------------------
	def __fetch_metadata(self):
		"""Document meta data loader for GnuMed compatible database."""

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__defconn.cursor()

		# get document level metadata
		cmd = "SELECT doc_id, seq_idx, comment, octet_length(data) FROM doc_obj WHERE id = %s "
		if not gmPG.run_query(cursor, cmd, self.ID):
			cursor.close()
			_log.Log(gmLog.lErr, 'Cannot load object [%s] metadata.' % self.ID)
			return None
		result = cursor.fetchone()

		self.metadata = {
			'id': self.ID,
			'document id': result[0],
			'sequence index': result[1],
			'comment': result[2],
			'size': result[3]
		}

		cursor.close()
		return 1
	#--------------------------------------------------------
	# store data
	#--------------------------------------------------------
	def __setitem__(self, item=None, value=None):
		if self.__rwconn is None:
			self.__rwconn = self.__backend.GetConnection('blobs', readonly=0)
		if item == 'metadata':
			self.__update_metadata(value)
			return
		if item == 'data from file':
			self.__update_data_from_file(value)
			return
		if item == 'data':
			self.__update_data(value)
			return
		_log.Log(gmLog.lWarn, "don't know how to set item [%s]" % item)
		raise KeyError, "don't know how to set item [%s]" % item
	#--------------------------------------------------------
	def __update_data_from_file(self, fname):
		# read from file and convert (escape)
		if not os.path.exists(fname):
			raise ValueError, "[%s] does not exist" % fname
		aFile = open(fname, "rb")
		img_data = str(aFile.read())
		aFile.close()

		from pyPgSQL.PgSQL import PgBytea
		img_obj = PgBytea(img_data)

		# insert the data
		cmd = "UPDATE doc_obj SET data=%s WHERE id=%s "
		curs = self.__rwconn.cursor()
		try:
			curs.execute(cmd, img_obj, self.ID)
		except:
			_log.LogException('cannot update data from [%s]' % fname, sys.exc_info())
			curs.close()
			raise ValueError
		self.__rwconn.commit()
		curs.close()

		self.filename = fname
		_log.Log(gmLog.lData, 'successfully imported %s bytes from [%s] into object [%s]' % (len(img_data), self.filename, self.ID))
	#--------------------------------------------------------
	def __update_data(self, data):
		# convert (escape)
		from pyPgSQL.PgSQL import PgBytea
		img_obj = PgBytea(data)

		# insert the data
		cmd = "UPDATE doc_obj SET data=%s WHERE id=%s "
		curs = self.__rwconn.cursor()
		try:
			curs.execute(cmd, img_obj, self.ID)
		except:
			_log.LogException('cannot update data', sys.exc_info())
			curs.close()
			raise ValueError
		self.__rwconn.commit()
		curs.close()

		_log.Log(gmLog.lData, 'successfully imported %s bytes into object [%s]' % (len(data), self.ID))
	#--------------------------------------------------------
	def __update_metadata(self, data = None):
		# make SET clause
		sets = []
		try:
			sets.append("doc_id='%s'" % data['document id'])
		except KeyError: pass

		try:
			sets.append("seq_idx='%s'" % data['sequence index'])
		except KeyError: pass

		try:
			sets.append("comment='%s'" % data['comment'])
		except KeyError: pass

		set_clause = ', '.join(sets)

		# actually set it in the DB
		cmd =  "UPDATE doc_obj SET %s WHERE id='%s'" % (set_clause, self.ID)
		curs = self.__rwconn.cursor()
		if not gmPG.run_query(curs, cmd):
			_log.Log(gmLog.lErr, 'cannot update metadata')
			curs.close()
			raise ValueError
		self.__rwconn.commit()
		curs.close()

		# and remember it
#		try:
#			self.metadata['document id'] = data['document id']
#		except KeyError: pass

#		try:
#			self.metadata['sequence index'] = data['sequence index']
#		except KeyError: pass

#		try:
#			self.metadata['comment'] = data['comment']
#		except KeyError: pass
	#--------------------------------------------------------
	def export_to_file(self, aTempDir = None, aChunkSize = 0):
		if not self.__fetch_metadata:
			_log.Log(gmLog.lErr, 'Cannot load metadata.')
			return None

		# if None -> use tempfile module default, else use that path as base directory for temp files
		if not aTempDir is None:
			tempfile.tempdir = aTempDir
		tempfile.template = "gm-doc_obj-"

		# cDocument.metadata->objects->file name
		fname = tempfile.mktemp()
		aFile = open(fname, 'wb+')

		# Windoze sucks: it can't transfer objects of arbitrary size,
		# or maybe this is due to pyPgSQL,
		# anyways, we need to split the transfer,
		# only possible if postgres >= 7.2
		if self.__defconn.version < "7.2":
			max_chunk_size = 0
			_log.Log(gmLog.lWarn, 'PostgreSQL < 7.2 does not support substring() on bytea.')
		else:
			max_chunk_size = aChunkSize
		_log.Log(gmLog.lData, "export chunk size is %s" % max_chunk_size)

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__defconn.cursor()

		# a chunk size of 0 means: all at once
		if ((max_chunk_size == 0) or (self.metadata['size'] <= max_chunk_size)):
			_log.Log(gmLog.lInfo, "retrieving entire object at once")
			# retrieve object
			cmd = "SELECT data FROM doc_obj WHERE id=%s "
			try:
				cursor.execute(cmd, self.ID)
			except:
				_log.LogException("cannot SELECT doc_obj", sys.exc_info())
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(cursor.fetchone()[0]))
		else:
			needed_chunks, remainder = divmod(self.metadata['size'], max_chunk_size)
			_log.Log(gmLog.lData, "need %s chunks with a remainder of %s bytes" % (needed_chunks, remainder))

			# retrieve chunks
			for chunk_id in range(needed_chunks):
				_log.Log(gmLog.lData, "retrieving chunk %s" % (chunk_id+1))
				pos = (chunk_id*max_chunk_size) + 1
				cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE id=%s "
				try:
					cursor.execute(cmd, (pos, max_chunk_size, self.ID))
				except:
					_log.LogException("cannot SELECT doc_obj chunk, try decreasing chunk size", sys.exc_info())
					return None
				# it would be a fatal error to see more than one result as ids are supposed to be unique
				aFile.write(str(cursor.fetchone()[0]))

			# retrieve remainder
			if remainder > 0:
				_log.Log(gmLog.lData, "retrieving trailing bytes after chunks")
				pos = (needed_chunks*max_chunk_size) + 1
				cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE id=%s "
				try:
					cursor.execute(cmd, (pos, remainder, self.ID))
				except:
					_log.LogException("cannot SELECT doc_obj remainder", sys.exc_info())
					return None
				# it would be a fatal error to see more than one result as ids are supposed to be unique
				aFile.write(str(cursor.fetchone()[0]))

		aFile.close()
		cursor.close()
		self.filename = fname

		return 1
#============================================================
class gmMedDoc:

	def __init__(self, aPKey):
		"""Fails if

		- no connection to database possible
		- document referenced by aPKey does not exist.
		"""
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('blobs')
		self.__rwconn = None

		self.ID = aPKey			# == identity.id == primary key
		if not self.__pkey_exists():
			raise gmExceptions.ConstructorError, "No document with ID [%s] in database." % aPKey

		self.metadata = {}
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self.__defconn.cursor()
		cmd = "select exists(select id from doc_med where id = %s)"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info())
			return None
		res = curs.fetchone()[0]
		curs.close()
		return res
	#--------------------------------------------------------
	def __del__(self):
		self.__backend.ReleaseConnection('blobs')
		if self.__rwconn is not None:
			self.__rwconn.close()
	#--------------------------------------------------------
	def __getitem__(self, item):
		if item == 'metadata':
			return self.__fetch_metadata()
		if item == 'descriptions':
			return self.__fetch_descriptions()
	#--------------------------------------------------------
	def __fetch_descriptions(self):
		"""Get document descriptions.

		- will return a list of strings
		"""
		cursor = self.__defconn.cursor()
		cmd = "SELECT substring(text from 1 for 50) FROM doc_desc WHERE doc_id= %s "
		if not gmPG.run_query(cursor, cmd, self.ID):
			cursor.close()
			_log.Log(gmLog.lErr, 'Cannot load document [%s] descriptions.' % self.ID)
			return None
		result = cursor.fetchall()
		cursor.close()
		if len(result) == 0:
			return None
		data = []
		for desc in result:
			data.extend(desc)
		return data
	#--------------------------------------------------------
	def __fetch_metadata(self):
		"""Document meta data loader for GnuMed compatible database."""
		# FIXME: error handling !

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__defconn.cursor()

		# get document level metadata
		cmd = "SELECT patient_id, type, comment, date, ext_ref FROM doc_med WHERE id =  %s "
		if not gmPG.run_query(cursor, cmd, self.ID):
			cursor.close()
			_log.Log(gmLog.lErr, 'cannot load document [%s] metadata' % self.ID)
			return None
		result = cursor.fetchone()
		self.metadata['patient id'] = result[0]
		self.metadata['type ID'] = result[1]
		self.metadata['comment'] = result[2]
		self.metadata['date'] = result[3]
		self.metadata['reference'] = result[4]

		# translate type ID to localized verbose name
		cmd = "select name from v_i18n_doc_type where id=  %s "
		if not gmPG.run_query(cursor, cmd, self.metadata['type ID']):
			_log.Log(gmLog.lWarn, 'cannot find name for document type [%s]' % self.metadata['type ID'])
			self.metadata['type'] = _('unknown doc type')
		else:
			result = cursor.fetchone()
			self.metadata['type'] = result[0]

		# get object level metadata for all objects of this document
		cmd = "SELECT id, comment, seq_idx, octet_length(data) FROM doc_obj WHERE doc_id = %s "
		try:
			cursor.execute(cmd, self.ID)
		except:
			cursor.close()
			_log.LogException('Cannot load document [%s] metadata.' % self.ID, sys.exc_info())
			return None
		matching_rows = cursor.fetchall()
		self.metadata['objects'] = {}
		for row in matching_rows:
			obj_id = row[0]
			# cDocument.metadata->objects->id->comment/index
			tmp = {'comment': row[1], 'index': row[2], 'size': int(row[3])}
			self.metadata['objects'][obj_id] = tmp

		cursor.close()
		_log.Log(gmLog.lData, 'Meta data: %s' % self.metadata)

		return self.metadata
	#--------------------------------------------------------
	# storing data
	#--------------------------------------------------------
	def __setitem__(self, item=None, value=None):
		if self.__rwconn is None:
			self.__rwconn = self.__backend.GetConnection('blobs', readonly=0)
		if item == 'metadata':
			self.__update_metadata(value)
	#--------------------------------------------------------
	def __update_metadata(self, data = None):
		self.metadata['patient id'] = data['patient id']
		self.metadata['type ID'] = data['type ID']
		self.metadata['comment'] = data['comment']
		self.metadata['date'] = data['date']
		self.metadata['reference'] = data['reference']
		curs = self.__rwconn.cursor()
		cmd =  "UPDATE doc_med SET patient_id= %s , type= %s , comment= %s , date= %s , ext_ref= %s WHERE id= %s "
		if not gmPG.run_query(curs, cmd, self.metadata['patient id'], self.metadata['type ID'], self.metadata['comment'], self.metadata['date'], self.metadata['reference'], self.ID):
			_log.Log(gmLog.lErr, 'cannot update metadata')
			curs.close()
			raise ValueError
		self.__rwconn.commit()
		curs.close()
#============================================================
def create_document(data):
	"""
	None - failed
	not None - new document ID
	"""
	try:
		cmd = "INSERT INTO doc_med (patient_id) VALUES ('%s')" % data['patient id']
	except KeyError:
		_log.Log(gmLog.lErr, data)
		_log.LogException('invalid argument data structure', sys.exc_info())
		return None

	# get connection
	backend = gmPG.ConnectionPool()
	conn = backend.GetConnection('blobs', readonly = 0)
	# start our transaction (done implicitely by defining a cursor)
	cursor = conn.cursor()

	if not gmPG.run_query(cursor, cmd):
		_log.Log(gmLog.lErr, 'Cannot insert document.')
		_log.Log(gmLog.lErr, data)
		cursor.close()
		conn.close()
		return None

	# get new patient's ID
	cmd = "SELECT last_value FROM doc_med_id_seq"
	if not gmPG.run_query(cursor, cmd):
		cursor.close()
		conn.close()
		return None
	doc_id = cursor.fetchone()[0]
	_log.Log(gmLog.lData, 'new document ID: %s' % doc_id)

	# close connection
	conn.commit()
	cursor.close()
	conn.close()

	# and init new document object
	try:
		doc = gmMedDoc(aPKey = doc_id)
	except:
		_log.LogException('cannot init document with ID [%s]' % doc_id, sys.exc_info())
		return None

	return doc
#============================================================
def create_object(data):
	"""
	None - failed
	not None - new document ID
	"""
	try:
		data['document id']
	except KeyError:
		_log.Log(gmLog.lErr, data)
		_log.LogException('invalid argument data structure', sys.exc_info())
		return None

	# get connection
	backend = gmPG.ConnectionPool()
	conn = backend.GetConnection('blobs', readonly = 0)
	# start our transaction (done implicitely by defining a cursor)
	cursor = conn.cursor()

	cmd = "INSERT INTO doc_obj (doc_id) VALUES ( %s )"
	if not gmPG.run_query(cursor, cmd, data['document id']):
		_log.Log(gmLog.lErr, 'Cannot insert object.')
		_log.Log(gmLog.lErr, data)
		cursor.close()
		conn.close()
		return None

	# get new patient's ID
	cmd = "SELECT last_value FROM doc_obj_id_seq"
	if not gmPG.run_query(cursor, cmd):
		cursor.close()
		conn.close()
		return None
	obj_id = cursor.fetchone()[0]
	_log.Log(gmLog.lData, 'new object ID: %s' % obj_id)

	# close connection
	conn.commit()
	cursor.close()
	conn.close()

	# and init new object
	try:
		obj = gmMedObj(aPKey = obj_id)
	except:
		_log.LogException('cannot init object with ID [%s]' % obj_id, sys.exc_info())
		return None

	return obj
#============================================================
# $Log: gmMedDoc.py,v $
# Revision 1.1  2003-10-23 06:02:38  sjtan
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
