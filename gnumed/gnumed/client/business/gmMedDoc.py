"""This module encapsulates document level operations.

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
 >- 'date'			""		(time stamp)
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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedDoc.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#=======================================================================================
import sys, tempfile, os, shutil

import gmLog
_log = gmLog.gmDefLog

import gmPG
from gmExceptions import ConstructorError
#============================================================
def __run_query(aCursor = None, aCmd = None):
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to run query')
		return None
	if aQuery is None:
		_log.Log(gmLog.lErr, 'need query to run it')
		return None
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
			raise gmExceptions.ConstructorError, "No document with ID [%s] in database." % aPKey

		self.filename = None
		self.metadata = {}
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self.__defconn.cursor()
		cmd = "select exists(select id from doc_obj where id = %s);"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info(), fatal=0)
			return None
		res = curs.fetchone()[0]
		curs.close()
		return res
	#--------------------------------------------------------
	def __del__(self):
		self.__backend.ReleaseConnection('blobs')
	#--------------------------------------------------------
	# attribute handler
	#--------------------------------------------------------
	def __getitem__(self, item):
		if item == 'filename':
			return self.filename
		if item == 'metadata':
			self.__get_metadata()
			return self.metadata
	#--------------------------------------------------------
	def __get_metadata(self):
		"""Document meta data loader for GnuMed compatible database."""
		# FIXME: dynamic updates !

		# sanity checks
		if len(self.metadata) != 0:
			return 1

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__defconn.cursor()

		# get document level metadata
		cmd = "SELECT doc_id, seq_idx, comment, octet_length(data) FROM doc_obj WHERE id = %s;"
		try:
			cursor.execute(cmd, self.ID)
		except:
			cursor.close()
			_log.LogException('Cannot load object [%s] metadata.' % self.ID, sys.exc_info())
			return None
		result = cursor.fetchone()

		self.metadata = {}
		self.metadata['id'] = self.ID
		self.metadata['document id'] = result[0]
		self.metadata['sequence index'] = result[1]
		self.metadata['comment'] = result[2]
		self.metadata['size'] = result[3]

		cursor.close()

		return 1
	#--------------------------------------------------------
	def __setitem__(self, item=None, value=None):
		if self.__rwconn is None:
			self.__rwconn = self.__backend.GetConnection('blobs', readonly=0)
		if item == 'metadata':
			self.__update_metadata(value)
			return
		if item == 'data':
			self.__update_data(value)
			return
	#--------------------------------------------------------
	def __update_data(self, fname):
		if not os.path.exists(fname):
			raise ValueError, "[%s] does not exist" % fname
		aFile = open(fname, "rb")
		img_data = str(aFile.read())
		aFile.close()

		from pyPgSQL.PgSQL import PgBytea
		img_obj = PgBytea(img_data)

		# finally insert the data
		cmd = "UPDATE doc_obj SET data=%s WHERE id=%s;"
		curs = self.__rwconn.cursor()
		try:
			curs.execute(cmd, img_obj, self.ID)
		except:
			_log.LogException('cannot update data', sys.exc_info())
			curs.close()
			raise ValueError, 'cannot update data'
		self.__rwconn.commit()
		curs.close()
		self.filename = fname
		_log.Log(gmLog.lData, 'successfully imported data [%s] into object [%s]' % (self.filename, self.ID))
	#--------------------------------------------------------
	def __update_metadata(self, data = None):
		self.metadata['document id'] = data['document id']
		self.metadata['sequence index'] = data['sequence index']
		self.metadata['comment'] = data['comment']
		cmd =  "UPDATE doc_obj SET doc_id='%s', seq_idx='%s', comment='%s' WHERE id='%s';" % \
				(self.metadata['document id'], self.metadata['sequence index'], self.metadata['comment'], self.ID)
		curs = self.__rwconn.cursor()
		if not gmPG.run_query(curs, cmd):
			_log.Log(gmLog.lErr, 'cannot update metadata')
			curs.close()
			raise ValueError
		self.__rwconn.commit()
		curs.close()
	#--------------------------------------------------------
	def export_to_file(self, aTempDir = None, aChunkSize = 0):
		if not self.__get_metadata:
			_log.Log(gmLog.lErr, 'Cannot load metadata.')
			return None

		# if None -> use tempfile module default, else use that path as base directory for temp files
		tempfile.tempdir = aTempDir
		tempfile.template = "gm-doc_obj-"

		# cDocument.metadata->objects->file name
		self.filename = tempfile.mktemp()
		aFile = open(self.filename, 'wb+')

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
			cmd = "SELECT data FROM doc_obj WHERE id=%s;"
			try:
				cursor.execute(cmd, self.ID)
			except:
				_log.LogException("cannot SELECT doc_obj", sys.exc_info())
				return None
			# it would be a fatal error to see more than one result as ids are supposed to be unique
			aFile.write(str(cursor.fetchone()[0]))
		else:
			needed_chunks, remainder = divmod(self.metadata['size'], max_chunk_size)
			_log.Log(gmLog.lData, "need %s chunks" % needed_chunks)

			# retrieve chunks
			for chunk_id in range(needed_chunks):
				_log.Log(gmLog.lData, "retrieving chunk %s" % (chunk_id+1))
				pos = (chunk_id*max_chunk_size) + 1
				cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE id=%s;"
				try:
					cursor.execute(cmd, (pos, max_chunk_size, self.ID))
				except:
					_log.LogException("cannot SELECT doc_obj chunk, try decreasing chunk size", sys.exc_info())
					return None
				# it would be a fatal error to see more than one result as ids are supposed to be unique
				aFile.write(str(cursor.fetchone()[0]))
			_log.Log(gmLog.lData, "retrieving trailing bytes after chunks")

			# retrieve remainder
			if remainder > 0:
				pos = (needed_chunks*max_chunk_size) + 1
				cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE id=%s;"
				try:
					cursor.execute(cmd, (pos, remainder, self.ID))
				except:
					_log.LogException("cannot SELECT doc_obj remainder", sys.exc_info())
					return None
				# it would be a fatal error to see more than one result as ids are supposed to be unique
				aFile.write(str(cursor.fetchone()[0]))

		aFile.close()
		cursor.close()

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
		self.metadata['id'] = self.ID
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self.__defconn.cursor()
		cmd = "select exists(select id from doc_med where id = %s);"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info(), fatal=0)
			return None
		res = curs.fetchone()[0]
		curs.close()
		return res
	#--------------------------------------------------------
	def __del__(self):
		self.__backend.ReleaseConnection('blobs')
	#--------------------------------------------------------
	def __getitem__(self, item):
		if item == 'metadata':
			return self.__get_metadata()
	#--------------------------------------------------------
	def __get_metadata(self):
		"""Document meta data loader for GnuMed compatible database."""
		# FIXME: error handling !

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__defconn.cursor()

		# get document level metadata
		cmd = "SELECT patient_id, type, comment, date, ext_ref FROM doc_med WHERE id = %s;"
		try:
			cursor.execute(cmd, self.ID)
		except:
			cursor.close()
			_log.LogException('Cannot load document [%s] metadata.' % self.ID, sys.exc_info())
			return None
		result = cursor.fetchone()
		self.metadata['patient id'] = result[0]
		self.metadata['type ID'] = result[1]
		self.metadata['comment'] = result[2]
		self.metadata['date'] = result[3]
		self.metadata['reference'] = result[4]
		# translate type ID to localized verbose name
		cmd = "select name from v_i18n_doc_type where id = %s;"
		try:
			cursor.execute(cmd, self.metadata['type ID'])
			result = cursor.fetchone()
			self.metadata['type'] = result[0]
		except:
			_log.LogException('Cannot load document [%s] metadata.' % self.ID, sys.exc_info())
			self.metadata['type'] = _('unknown doc type')

		# get object level metadata for all objects of this document
		cmd = "SELECT id, comment, seq_idx, octet_length(data) FROM doc_obj WHERE doc_id = %s;"
		try:
			cursor.execute(cmd, self.metadata['id'])
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
		cmd =  "UPDATE doc_med SET patient_id='%s', type='%s', comment='%s', date='%s', ext_ref='%s' WHERE id='%s';" % \
				(self.metadata['patient id'], self.metadata['type ID'], self.metadata['comment'], self.metadata['date'], self.metadata['reference'], self.ID)
		curs = self.__rwconn.cursor()
		if not gmPG.run_query(curs, cmd):
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
		cmd = "INSERT INTO doc_med (patient_id) VALUES ('%s');" % data['patient id']
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
	cmd = "SELECT last_value FROM doc_med_id_seq;"
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
		cmd = "INSERT INTO doc_obj (doc_id) VALUES ('%s');" % data['document id']
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
		_log.Log(gmLog.lErr, 'Cannot insert object.')
		_log.Log(gmLog.lErr, data)
		cursor.close()
		conn.close()
		return None

	# get new patient's ID
	cmd = "SELECT last_value FROM doc_obj_id_seq;"
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
def call_viewer_on_file(aFile = None):
	"""Try to find an appropriate viewer with all tricks and call it."""

	_log.Log(gmLog.lInfo, "Calling viewer on [%s]." % aFile)

	if aFile is None:
		msg = "No need to call viewer without file name."
		_log.Log(gmLog.lErr, msg)
		return None, msg

	# does this file exist, actually ?
	if not os.path.exists(aFile):
		msg = _('File [%s] does not exist !') % aFile
		_log.Log(gmLog.lErr, msg)
		return None, msg

	# sigh ! let's be off to work
	try:
		import gmMimeLib
	except ImportError:
		msg = _("Cannot import gmMimeLib.py !")
		_log.LogException(msg, sys.exc_info(), fatal=0)
		return None, msg

	mime_type = gmMimeLib.guess_mimetype(aFile)
	_log.Log(gmLog.lData, "mime type : %s" % mime_type)
	viewer_cmd = gmMimeLib.get_viewer_cmd(mime_type, aFile)
	_log.Log(gmLog.lData, "viewer cmd: '%s'" % viewer_cmd)

	if viewer_cmd != None:
		os.system(viewer_cmd)
		return 1, ""

	_log.Log(gmLog.lErr, "Cannot determine viewer via standard mailcap mechanism.")
	if os.name == "posix":
		_log.Log(gmLog.lErr, "You should add a viewer for this mime type to your mailcap file.")
		msg = _("Unable to start viewer on file\[%s]\nYou need to update your mailcap file.") % aFile
		return None, msg
	else:
		_log.Log(gmLog.lWarn, "Let's see what the OS can do about that.")
		# does the file already have an extension ?
		(path_name, f_ext) = os.path.splitext(aFile)
		# no
		if f_ext == "":
			# try to guess one
			f_ext = gmMimeLib.guess_ext_by_mimetype(mime_type)
			if f_ext is None:
				_log.Log(gmLog.lErr, "Unable to guess file extension from mime type. Trying sheer luck.")
				file_to_display = aFile
				f_ext = ""
			else:
				file_to_display = aFile + f_ext
				shutil.copyfile(aFile, file_to_display)
		# yes
		else:
			file_to_display = aFile

		_log.Log(gmLog.lData, "%s <%s> (%s) -> %s" % (aFile, mime_type, f_ext, file_to_display))
		try:
			os.startfile(file_to_display)
		except:
			msg = _("Unable to start viewer on file [%s].") % file_to_display		
			_log.LogException(msg, sys.exc_info(), fatal=0)
			return None, msg

	# clean up if necessary
	# don't kill the file from under the (async) viewer
#	if file_to_display != aFile:
#		os.remove(file_to_display)

	return 1, ""
#============================================================
