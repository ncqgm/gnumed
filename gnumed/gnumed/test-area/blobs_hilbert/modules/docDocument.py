#!/usr/bin/python

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
  `- oid			{}
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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/modules/Attic/docDocument.py,v $
__version__ = "$Revision: 1.31 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#=======================================================================================
import os.path, fileinput, string, types, sys, tempfile, os, shutil

from pyPgSQL import PgSQL

import gmLog
_log = gmLog.gmDefLog

import gmExceptions
#=======================================================================================
class cDocument:

	def __init__(self, aCfg = None):
		# sanity checks
		if aCfg is None:
			_log.Log(gmLog.lErr, "Parameter aCfg must point to a config parser object.")
			raise ConstructorError, "Need valid config parser pointer."
		self.cfg = aCfg

		_log.Log(gmLog.lData, "Instantiated.")
		self.__metadata = {}
	#-----------------------------------
	def loadMetaDataFromXML(self, aBaseDir = None, aSection = None):
		"""Load document metadata from XML file."""
		# sanity checks
		if not type(aSection) == type('a string'):
			_log.Log(gmLog.lErr, "Parameter aSection must be a string.")
			return None

		if not os.path.exists (aBaseDir):
			_log.Log(gmLog.lErr, "The directory '" + str(aBaseDir) + "' does not exist !")
			return None
		else:
			_log.Log(gmLog.lData, "working from directory '" + str(aBaseDir) + "'")

		# check for Befund description file
		desc_file_name = self.cfg.get(aSection, "description")
		if not os.path.exists (os.path.join(aBaseDir, desc_file_name)):
			_log.Log (gmLog.lErr, "skipping " + aBaseDir + "- no description file (" + desc_file_name + ") found")
			return None
		else:
			DescFile = os.path.join(aBaseDir, desc_file_name)

		self.__metadata = {}

		# document type
		tmp = self.__get_from_xml(aTag = self.cfg.get(aSection, "type_tag"), anXMLfile = DescFile)
		if tmp == None:
			_log.Log(gmLog.lErr, "Cannot load document type.")
			return None
		else:
			self.__metadata['type'] = string.join(tmp)
			_log.Log(gmLog.lData, "Document type: " + str(self.__metadata['type']))

		# document comment
		tmp = self.__get_from_xml(aTag = self.cfg.get(aSection, "comment_tag"), anXMLfile = DescFile)
		if tmp == None:
			_log.Log(gmLog.lErr, "Cannot load document comment.")
			return None
		else:
			self.__metadata['comment'] = string.join(tmp)
			_log.Log(gmLog.lData, "Document comment: " + str(self.__metadata['comment']))

		# document reference date
		tmp = self.__get_from_xml(aTag = self.cfg.get(aSection, "date_tag"), anXMLfile = DescFile)
		if tmp == None:
			_log.Log(gmLog.lErr, "Cannot load document reference date.")
			return None
		else:
			self.__metadata['date'] = string.join(tmp)
			_log.Log(gmLog.lData, "document reference date: " + str(self.__metadata['date']))

		# external reference string
		tmp = self.__get_from_xml(aTag = self.cfg.get(aSection, "ref_tag"), anXMLfile = DescFile)
		if tmp == None:
			_log.Log(gmLog.lErr, "Cannot load document reference string.")
			return None
		else:
			self.__metadata['reference'] = string.join(tmp)
			_log.Log(gmLog.lData, "document reference string: " + str(self.__metadata['reference']))

		# document description
		tmp = self.__get_from_xml(aTag = self.cfg.get(aSection, "aux_comment_tag"), anXMLfile = DescFile)
		if tmp == None:
			_log.Log(gmLog.lErr, "Cannot load long document description.")
		else:
			self.__metadata['description'] = string.join(tmp)
			_log.Log(gmLog.lData, "long document description: " + str(self.__metadata['description']))

		# list of data files
		if not self.__read_img_list(DescFile, aBaseDir, aSection):
			_log.Log(gmLog.lErr, "Cannot retrieve list of document data files.")
			return None

		return 1
	#-----------------------------------
	def loadImgListFromXML(self, aDescFile = None, aBaseDir = None, aSection = None):
		# FIXME: sanity checks
		# list of data files
		if not self.__read_img_list(aDescFile, aBaseDir, aSection):
			_log.Log(gmLog.lErr, "Cannot retrieve list of document data files.")
			return None
		else:
			return 1
	#-----------------------------------
	def loadMetaDataFromGNUmed(self, aConn = None, aDocumentID = None):
		"""Document meta data loader for GnuMed compatible database."""
		# FIXME: error handling !

		_log.Log(gmLog.lInfo, 'loading stage 1 (document) metadata from GnuMed compatible database')

		# sanity checks
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot load metadata without database connection.')
			return (1==0)

		if aDocumentID == None:
			_log.Log(gmLog.lErr, 'Cannot load document metadata without a document ID.')
			return (1==0)

		self.__metadata = {}
		self.__metadata['id'] = aDocumentID

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		# get document level metadata
		cmd = "SELECT patient_id, type, comment, date, ext_ref FROM doc_med WHERE id='%s'" % (self.__metadata['id'])
		cursor.execute(cmd)
		result = cursor.fetchone()
		self.__metadata['patient id'] = result[0]
		self.__metadata['type ID'] = result[1]
		self.__metadata['comment'] = result[2]
		self.__metadata['date'] = result[3]
		self.__metadata['reference'] = result[4]
		# translate type ID to localized verbose name
		cmd = "select name from v_i18n_doc_type where id = '%s';" % self.__metadata['type ID']
		cursor.execute(cmd)
		result = cursor.fetchone()
		self.__metadata['type'] = result[0]

		# get object level metadata for all objects of this document
		cmd = "SELECT oid, comment, seq_idx, octet_length(data) FROM doc_obj WHERE doc_id='%s'" % (self.__metadata['id'])
		cursor.execute(cmd)
		matching_rows = cursor.fetchall()
		self.__metadata['objects'] = {}
		for row in matching_rows:
			oid = row[0]
			# cDocument.metadata->objects->oid->comment/index
			tmp = {'comment': row[1], 'index': row[2], 'size': row[3]}
			self.__metadata['objects'][oid] = tmp

		cursor.close()
		_log.Log(gmLog.lData, 'Meta data: %s' % self.__metadata)

		return (1==1)
	#-----------------------------------
	def getMetaData(self):
		"""Return meta data no matter where we got it from."""
		return self.__metadata
	#-----------------------------------
	def importIntoGNUmed(self, aConn = None, aPatient = None):
		_log.Log(gmLog.lInfo, 'importing document into GnuMed compatible database')

		# sanity checks
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot import document without database connection.')
			return None

		import docPatient
		if not isinstance(aPatient, docPatient.cPatient):
			_log.Log (gmLog.lErr, "The object '" + str(aPatient) + "' is not a cPatient instance !")
			return None
		del docPatient

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		try:
			# translate document type
			cmd = "SELECT count(id) FROM v_i18n_doc_type WHERE name='%s'" % (self.__metadata['type'])
			cursor.execute(cmd)
			result = cursor.fetchone()
			if result[0] != 1:
				_log.Log(gmLog.lErr, 'Document type "%s" is not valid for this database !' % (self.__metadata['type']))
				cursor.close()
				return None
			cmd = "SELECT id FROM v_i18n_doc_type WHERE name='%s'" % (self.__metadata['type'])
			cursor.execute(cmd)
			type_id = cursor.fetchone()[0]

			# insert main document record
			cmd = "INSERT INTO doc_med (patient_id, type, comment, date, ext_ref) VALUES ('%s', '%s', '%s', '%s', '%s')" % (aPatient.ID, type_id, self.__metadata['comment'], self.__metadata['date'], self.__metadata['reference'])
			cursor.execute(cmd)

			# insert the document data objects
			for oid in self.__metadata['objects'].keys():
				obj = self.__metadata['objects'][oid]
				aHandle = open(obj['file name'], "rb")
				img_data = str(aHandle.read())
				aHandle.close()
				# tag images so they are self-identifying
				#  FIXME:
				#  (actually we should write into official comment fields
				#   and only append stuff if we don't see any other chance)
				img_data = img_data + "\ncharset:DIN_66003\n"
				img_data = img_data + "last name:%s\n" % aPatient.lastnames
				img_data = img_data + "first name:%s\n" % aPatient.firstnames
				img_data = img_data + "date of birth:%s\n" % str(aPatient.dob)
				img_data = img_data + "reference date:%s\n" % str(self.__metadata['date'])
				img_data = img_data + "external reference:%s\n" % str(self.__metadata['reference'])

				img_obj = PgSQL.PgBytea(img_data)
				# finally insert the data
				cmd = "INSERT INTO doc_obj (doc_id, seq_idx, data) VALUES (currval('doc_med_id_seq'), %s, %s)"
				cursor.execute(cmd, obj['index'], img_obj)

			# insert long document description if available
			if self.__metadata.has_key('description'):
				cmd = "INSERT INTO doc_desc (doc_id, text) VALUES (currval('doc_med_id_seq'), '%s')" % self.__metadata['description']
				cursor.execute(cmd)

			# make permanent what we got so far
			aConn.commit()
			cursor.close()
			_log.Log(gmLog.lInfo, "document successfully imported")
			return (1==1)

		except:
			aConn.rollback()
			cursor.close()
			_log.LogException ("Exception: Cannot import document. Rolling back transactions.", sys.exc_info())
			return (1==0)
	#-----------------------------------
	def exportDocFromGNUmed(self, aConn = None, aTempDir = None):
		"""Export all objects of this document into local files.

		Once we call upon this method we let go of all hope of previously
		exported files. It is in the responsibility of the caller to do
		with them as she pleases.

		- self.__metadata['objects'] must hold a (potentieally empty)
		  list of object IDs
		- this will usually be accomplished by a previous call to loadMetaDataFromGNUmed()
		"""
		_log.Log(gmLog.lInfo, 'exporting document from GnuMed compatible database')

		# sanity checks
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot export document without database connection.')
			return (1==0)

		if not self.__metadata.has_key('objects'):
			_log.Log(gmLog.lErr, 'Cannot export document without object IDs')
			return (1==0)

		# if None -> use tempfile module default, else use that path as base directory for temp files
		tempfile.tempdir = aTempDir
		tempfile.template = "obj-"

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()
		# retrieve objects one by one
		for oid in self.__metadata['objects'].keys():
			cmd = "SELECT data FROM doc_obj WHERE oid='%s'" % (oid)
			cursor.execute(cmd)
			# cDocument.metadata->objects->file name
			obj = self.__metadata['objects'][oid]
			obj['file name'] = tempfile.mktemp()
			aFile = open(obj['file name'], 'wb+')
			# it would be a fatal error to see more than one result as oids are supposed to be unique
			img_data = cursor.fetchone()[0]
			# FIXME: PyGreSQL on Windows delivers PgByteA instance which is auto-unescaped
			# FIXME: pgdb, however, delivers type string which needs unescaping
			# FIXME: a temporary workaround is to convert things to string and unescape anyways
			# FIXME: this is, however, inefficient
			#aFile.write(self.__unescapeByteA(str(img_data)))
			aFile.write(str(img_data))
			aFile.close()

		cursor.close()

		_log.Log(gmLog.lData, 'Meta data: %s' % self.__metadata)
		return (1==1)
	#-----------------------------------
	def exportObjFromGNUmed(self, aConn = None, aTempDir = None, anObjID = None):
		"""Export object into local file.

		- self.__metadata['objects'] must hold a (potentially empty)
		  list of object IDs
		- this will usually be accomplished by a previous call to loadMetaDataFromGNUmed()
		"""
		_log.Log(gmLog.lInfo, 'exporting object from GnuMed compatible database')

		# sanity checks
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot export object without database connection.')
			return None

		if anObjID == None:
			_log.Log(gmLog.lErr, 'Cannot export object without an object ID.')
			return None

		if not self.__metadata.has_key('objects'):
			_log.Log(gmLog.lErr, 'Cannot export object without object ID list.')
			return None

		if not self.__metadata['objects'].has_key(anObjID):
			_log.Log(gmLog.lErr, 'Cannot export object (%s). It does not seem to belong to this document (%d).' % (anObjID, self.__metadata['id']))
			return None

		# if None -> use tempfile module default, else use that path as base directory for temp files
		tempfile.tempdir = aTempDir
		tempfile.template = "obj-"

		# now get the object
		obj = self.__metadata['objects'][anObjID]

		# Windoze sucks: it can't transfer objects of arbitrary size,
		# or maybe this is due to pyPgSQL,
		# anyways, we need to split the transfer,
		# only possible if postgres >= 7.2
		if aConn.version < "7.2":
			max_chunk_size = 0
			_log.Log(gmLog.lWarn, 'PostgreSQL < 7.2 does not support substring() on bytea.')
		else:
			max_chunk_size = self.cfg.get("viewer", "export chunk size")
			if max_chunk_size is None:
				max_chunk_size = 0
		_log.Log(gmLog.lData, "export chunk size is %s" % max_chunk_size)

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		# cDocument.metadata->objects->file name
		obj['file name'] = tempfile.mktemp()
		aFile = open(obj['file name'], 'wb+')

		# a chunk size of 0 means: all at once
		if (max_chunk_size == 0) or (obj['size'] < max_chunk_size):
			_log.Log(gmLog.lInfo, "export chunk size is 0 or object size is less then chunk size")
			# retrieve object
			cmd = "SELECT data FROM doc_obj WHERE oid='%s'" % (anObjID)
			try:
				cursor.execute(cmd)
			except:
				_log.LogException("cannot SELECT doc_obj", sys.exc_info())
				return None
			# it would be a fatal error to see more than one result as oids are supposed to be unique
			aFile.write(str(cursor.fetchone()[0]))
		else:
			needed_chunks, remainder = divmod(obj[size], max_chunk_size)
			_log.Log(gmLog.lData, "need %s chunks" % needed_chunks)
			# retrieve chunks
			for chunk_id in range(needed_chunks):
				_log.Log(gmLog.lData, "retrieving chunk %s" % chunk_id+1)
				pos = (chunk_id*max_chunk_size) + 1
				cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE oid='%s'" % (pos, max_chunk_size, anObjID)
				try:
					cursor.execute(cmd)
				except:
					_log.LogException("cannot SELECT doc_obj chunk, try decreasing chunk size", sys.exc_info())
					return None
				# it would be a fatal error to see more than one result as oids are supposed to be unique
				aFile.write(str(cursor.fetchone()[0]))
			_log.Log(gmLog.lData, "retrieving trailing bytes after chunks")
			if remainder > 0:
				pos = (needed_chunks*max_chunk_size) + 1
				cmd = "SELECT substring(data from %s for %s) FROM doc_obj WHERE oid='%s'" % (pos, remainder, anObjID)
				try:
					cursor.execute(cmd)
				except:
					_log.LogException("cannot SELECT doc_obj remainder", sys.exc_info())
					return None
				# it would be a fatal error to see more than one result as oids are supposed to be unique
				aFile.write(str(cursor.fetchone()[0]))

		aFile.close()
		# close our connection
		cursor.close()

		_log.Log(gmLog.lData, 'Meta data: %s' % self.__metadata)
		return (1==1)
	#-----------------------------------
	def removeObject(self, anOID = None):
		"""Remove an object from the metadata tree based on its object ID.

		FIXME: this does not remove objects from the database
		"""
		try:
			del self.__metadata['objects'][anOID]
		except KeyError:
			exc = sys.exc_info()
			_log.LogException("Cannot remove object with oid=[%s]" % anOID, exc, fatal=0)
			return None
		return 1
	#-----------------------------------
	# internal methods
	#-----------------------------------
	def __read_img_list(self, aDescFile = None, aBaseDir = None, aSection = None):
		"""Read list of image files from XML metadata file.

		We assume the order of file names to correspond to the sequence of pages.
		"""
		# sanity check
		if aBaseDir == None:
			aBaseDir = ""

		self.__metadata['objects'] = {}

		i = 1
		tag_name = self.cfg.get(aSection, "obj_tag")
		# now read the xml file
		for line in fileinput.input(aDescFile):
			# is this a line we want ?
			start_pos = string.find(line,'<%s' % tag_name)
			if start_pos == -1:
				continue

			# yes, so check for closing tag
			end_pos = string.find(line,'</%s>' % tag_name)
			if end_pos == -1:
				# but we don't do multiline tags
				_log.Log (gmLog.lErr, "Incomplete <%s></%s> line. We don't do multiline tags. Sorry."  % (tag_name, tag_name))
				return None

			# extract filename
			# FIXME: this is probably the place to add object level comments ?
			start_pos = string.find(line,'>', start_pos, end_pos) + 1
			file = line[start_pos:end_pos]
			tmp = {}
			tmp['file name'] = os.path.abspath(os.path.join(aBaseDir, file))
			# this 'index' defines the order of objects in the document
			tmp['index'] = i
			# we must use imaginary oid's since we are reading from a file,
			# this OID defines the object ID in the data store, this
			# has nothing to do with the semantic order of objects
			self.__metadata['objects'][i] = tmp
			i += 1

		# cleanup
		fileinput.close()

		if len(self.__metadata['objects'].keys()) == 0:
			_log.Log (gmLog.lErr, "no files found for import")
			return None

		_log.Log(gmLog.lData, "document data files to be processed: " + str(self.__metadata['objects']))

		return 1
	#-----------------------------------
	def __get_from_xml(self, aTag = None, anXMLfile = None):
		# sanity
		if type(aTag) != types.StringType:
			_log.Log(gmLog.lErr, "Argument aTag (" + str(aTag) + ") is not a string.")
			return None

		TagStart = "<" + aTag + ">"
		TagEnd = "</" + aTag + ">"

		_log.Log(gmLog.lInfo, "Retrieving " + TagStart + "content" + TagEnd + ".")

		inTag = 0
		content = []

		for line in fileinput.input(anXMLfile):
			tmp = line

			# this line starts a description
			if string.find(tmp, TagStart) != -1:
				inTag = 1
				# strip junk left of <tag>
				(junk, good_stuff) = string.split (tmp, TagStart, 1)
				_log.Log(gmLog.lData, "Found tag start in line: junk='%s' content='%s'" % (junk, good_stuff))
				tmp = good_stuff

			# this line ends a description
			if string.find(tmp, TagEnd) != -1:
				# only if tag start has been found already
				if inTag == 1:
					# strip junk right of </tag>
					(good_stuff, junk) = string.split (tmp, TagEnd, 1)
					_log.Log(gmLog.lData, "Found tag end in line: junk='%s' content='%s'" % (junk, good_stuff))
					content.append(good_stuff)
					# shortcut out of for loop
					break

			# might be in-tag data line or line with start tag only
			if inTag == 1:
				content.append(tmp)

		# cleanup
		fileinput.close()

		# looped over all lines
		if len(content) > 0:
			_log.Log (gmLog.lData, "%s tag content successfully read: %s" % (TagStart, str(content)))
			return content
		else:
			return None
	#-----------------------------------
	def __escapeByteA(self, aString):
		"""Make binary data palatable to PostgreSQL

		ASCII 0 ==>	\\000
		ASCII 39 ==>	\'  or  \\047
		ASCII 92 ==>	\\\\    or  \\134
		"""
		_log.Log(gmLog.lInfo, "starting")
		tmp = ""
		c = 0
		for aChar in aString:
			# 0-31, 127-255
			#if ord(aChar) not in range(32,127):
				#tmp = tmp + "\\\\%03d" % ord(aChar)
				#c += 1
			# NUL
			if ord(aChar) == 0:
				tmp = tmp + "\\\\000"
				c += 1
			# '
			elif ord(aChar) == 39:
				tmp = tmp +  "\\\\047"
				c += 1
			# "\"
			elif ord(aChar) == 92:
				tmp = tmp + "\\\\134"
				c += 1
			else:
				tmp = tmp + aChar

		_log.Log(gmLog.lData, "done: %d total, %d escaped" % (len(aString), c))
		return tmp
	#-----------------------------------
	def __unescapeByteA(self, aByteA):
		_log.Log(gmLog.lInfo, "starting")
		c = 0
		tmp = str(aByteA)
		# first replace all """\ooo""""
		# this will not catch any """\\"""
		for i in range(256):
			esc_code = "\\" + "%03o" % i
			real_char = chr(i)
			if string.count(tmp, esc_code) > 0:
				c += string.count(tmp, esc_code)
			tmp = string.replace(tmp, esc_code, real_char)

		# now replace all """\\"""
		tmp1 = ""
		lng = len(tmp)
		self.__i = 0
		while self.__i < lng:
			# do this char
			if tmp[self.__i] == "\\":
				if self.__i+1 < lng:
					if tmp[self.__i+1] == "\\":
						tmp1 = tmp1 + "\\"
						# skip next char
						self.__i += 1
						c += 1
					else:
						_log.Log(gmLog.lErr, "Escape logic ambiguity detected. Aborting unescaping.")
						return aByteA
				else:
					_log.Log(gmLog.lErr, "Trailing single backslash detected. Returning last character unchanged.")
					tmp1 = tmp1 + tmp[self.__i]
			else:
				tmp1 = tmp1 + tmp[self.__i]
			# and point to next char
			self.__i += 1

		_log.Log(gmLog.lData, "unescaped %s escaped characters" % c)
		return tmp1
#-----------------------------------
class cPatientDocumentList:
	"""Encapsulate a list of documents belonging to a single patient.

	- each document can be represented by a cDocument instance
	"""
	#-----------------------------------
	def __init__(self, aConn = None):
		_log.Log(gmLog.lData, "Instantiated.")
		# sanity checks
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot get meta data without database connection.')
			return None
		self.__conn = aConn
	#-----------------------------------
	def getList(self, aPatientID = None):
		"""Build a complete list of metadata for all documents of our patient."""
		# sanity checks
		if aPatientID == None:
			_log.Log(gmLog.lErr, "Cannot associate a patient with her documents without a patient ID.")
			return (1==0)

		cursor = self.__conn.cursor()
		tmp = cDocument()
		mdata = []
		# get all document IDs
		cmd = "SELECT id from doc_med WHERE patient_id='%s'" % aPatientID
		cursor.execute(cmd)
		matching_rows = cursor.fetchall()
		for row in matching_rows:
			doc_id = row[0]
			tmp.loadMetaDataFromGNUmed(self.__conn, doc_id)
			mdata.append(tmp.getMetaData())
		cursor.close
		return mdata
	#-----------------------------------
	def getDocument(self, aTempDir = None, aDocumentID = None):
		"""Export document data into files.

		FIXME: this is inefficient as it always transfers all objects of a document
		- we should be able to specify which object we want to retrieve
		- also, this should not duplicate meta data loading if possible
		"""
		# sanity checks
		if aDocumentID == None:
			_log.Log(gmLog.lErr, "Cannot load document without document ID.")
			return (1==0)
		else:
			_log.Log(gmLog.lData, "Trying to load document with id %s" % aDocumentID)

		if (aTempDir == None) or (not os.path.exists (aTempDir)):
			_log.Log(gmLog.lErr, "The directory '%s' does not exist ! Falling back to default temporary directory." % aTempDir) # which is tempfile.tempdir == None == use system defaults
		else:
			_log.Log(gmLog.lData, "working into directory '%s'" % aTempDir)

		tmp = cDocument()
		if not tmp.loadMetaDataFromGNUmed(self.__conn, aDocumentID):
			_log.Log(gmLog.lErr, "Cannot load metadata from database !")
			return (1==0)

		if not tmp.exportDocFromGNUmed(self.__conn, aTempDir):
			_log.Log(gmLog.lErr, "Cannot export object data from database !")
			return (1==0)

		return tmp.getMetaData()
#============================================================
def call_viewer_on_file(aFile = None):
	"""Try to find an appropriate viewer with all tricks and call it."""

	_log.Log(gmLog.lInfo, "Calling viewer on [%s]." % aFile)

	if aFile == None:
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
		import docMime
	except ImportError:
		exc = sys.exc_info()
		msg = _("Cannot import docMime.py !")
		_log.LogException(msg, exc, fatal=0)
		return None, msg

	mime_type = docMime.guess_mimetype(aFile)
	_log.Log(gmLog.lData, "mime type : %s" % mime_type)
	viewer_cmd = docMime.get_viewer_cmd(mime_type, aFile)
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
			f_ext = docMime.guess_ext_by_mimetype(mime_type)
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
	#if file_to_display != aFile:
		#os.remove(file_to_display)

	return 1, ""
#============================================================
# Main
#============================================================
if __name__ == '__main__':
	_ = lambda x:x
	_log.SetAllLogLevels(gmLog.lData)
	call_viewer_on_file(sys.argv[1])

#============================================================
# $Log: docDocument.py,v $
# Revision 1.31  2003-01-26 16:46:15  ncq
# - retrieve objects in chunks if needed and supported
#
# Revision 1.30  2003/01/25 00:23:49  ncq
# - get size of object with metadata
#
# Revision 1.29  2003/01/24 14:57:55  ncq
# - date is a timestamp now
#
# Revision 1.28  2003/01/24 13:16:08  ncq
# - verbosify doc_type on getMetadataFromGnumed()
#
# Revision 1.27  2003/01/24 12:29:33  ncq
# - make aware of v_i18n_doc_type
#
# Revision 1.26  2003/01/12 13:26:24  ncq
# - don't use exc = sys.exc_info() when inlined
#
# Revision 1.25  2003/01/05 13:42:52  ncq
# - only use startfile() on windows, not on POSIX
#
# Revision 1.24  2002/12/27 14:40:47  ncq
# - sort items by creation date/page index
# - on startup expand first level only (documents yes, pages no)
#
# Revision 1.23  2002/12/24 14:18:40  ncq
# - handle more exceptions gracefully
#
# Revision 1.22  2002/11/30 22:48:13  ncq
# - fix some Windows related oddities with mime types/file extensions
# - don't remove the object file from under the viewer
#
# Revision 1.21  2002/11/23 16:45:21  ncq
# - make work with pyPgSQL
# - fully working now but needs a bit of polish
#
# Revision 1.20  2002/11/08 15:51:37  ncq
# - make it work with pyPgSQL
#
# Revision 1.19  2002/10/01 09:47:36  ncq
# - sync, should sort of work
#
# Revision 1.18  2002/09/17 01:07:27  ncq
# - fixed indentation typo
#
# Revision 1.17  2002/09/17 00:06:30  ncq
# - documented meta data layout
#
# Revision 1.16  2002/09/12 21:39:55  ncq
# - several tweaks for displaying files
#
# Revision 1.15  2002/09/12 20:34:41  ncq
# - added helper call_viewer_on_file()
#
