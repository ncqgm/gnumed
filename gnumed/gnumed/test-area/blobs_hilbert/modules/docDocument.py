#!/usr/bin/python

"""This module encapsulates document level operations.

@copyright: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/modules/Attic/docDocument.py,v $
__version__ = "$Revision: 1.12 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#=======================================================================================
import os.path, fileinput, string, types, sys, tempfile, os
import gmLog
import docPatient

__log__ = gmLog.gmDefLog
#=======================================================================================
class cDocument:

	def __init__(self):
		__log__.Log(gmLog.lData, "Instantiated.")
		self.__metadata = {}
	#-----------------------------------
	def loadMetaDataFromXML(self, aBaseDir = None, aCfg = None, aSection = None):
		"""Load document metadata from XML file."""
		# sanity checks
		if aCfg == None:
			__log__.Log(gmLog.lErr, "Parameter aCfg must point to a config parser object.")
			return None

		if not type(aSection) == type('a string'):
			__log__.Log(gmLog.lErr, "Parameter aSection must be a string.")
			return None

		if not os.path.exists (aBaseDir):
			__log__.Log(gmLog.lErr, "The directory '" + str(aBaseDir) + "' does not exist !")
			return None
		else:
			__log__.Log(gmLog.lData, "working from directory '" + str(aBaseDir) + "'")

		# check for Befund description file
		desc_file_name = aCfg.get(aSection, "description")
		if not os.path.exists (os.path.join(aBaseDir, desc_file_name)):
			__log__.Log (gmLog.lErr, "skipping " + aBaseDir + "- no description file (" + desc_file_name + ") found")
			return None
		else:
			DescFile = os.path.join(aBaseDir, desc_file_name)

		self.__metadata = {}

		# document type
		tmp = self.__get_from_xml(aTag = aCfg.get(aSection, "type_tag"), anXMLfile = DescFile)
		if tmp == None:
			__log__.Log(gmLog.lErr, "Cannot load document type.")
			return None
		else:
			self.__metadata['type'] = string.join(tmp)
			__log__.Log(gmLog.lData, "Document type: " + str(self.__metadata['type']))

		# document comment
		tmp = self.__get_from_xml(aTag = aCfg.get(aSection, "comment_tag"), anXMLfile = DescFile)
		if tmp == None:
			__log__.Log(gmLog.lErr, "Cannot load document comment.")
			return None
		else:
			self.__metadata['comment'] = string.join(tmp)
			__log__.Log(gmLog.lData, "Document comment: " + str(self.__metadata['comment']))

		# document reference date
		tmp = self.__get_from_xml(aTag = aCfg.get(aSection, "date_tag"), anXMLfile = DescFile)
		if tmp == None:
			__log__.Log(gmLog.lErr, "Cannot load document reference date.")
			return None
		else:
			self.__metadata['date'] = string.join(tmp)
			__log__.Log(gmLog.lData, "document reference date: " + str(self.__metadata['date']))

		# external reference string
		tmp = self.__get_from_xml(aTag = aCfg.get(aSection, "ref_tag"), anXMLfile = DescFile)
		if tmp == None:
			__log__.Log(gmLog.lErr, "Cannot load document reference string.")
			return None
		else:
			self.__metadata['reference'] = string.join(tmp)
			__log__.Log(gmLog.lData, "document reference string: " + str(self.__metadata['reference']))

		# document description
		tmp = self.__get_from_xml(aTag = aCfg.get(aSection, "desc_tag"), anXMLfile = DescFile)
		if tmp == None:
			__log__.Log(gmLog.lErr, "Cannot load long document description.")
		else:
			self.__metadata['description'] = string.join(tmp)
			__log__.Log(gmLog.lData, "long document description: " + str(self.__metadata['description']))

		# list of data files
		if not self.__read_img_list(DescFile, aBaseDir):
			__log__.Log(gmLog.lErr, "Cannot retrieve list of document data files.")
			return None

		return 1
	#-----------------------------------
	def loadImgListFromXML(self, aDescFile = None, aBaseDir = None):
		# list of data files
		if not self.__read_img_list(aDescFile, aBaseDir):
			__log__.Log(gmLog.lErr, "Cannot retrieve list of document data files.")
			return None
		else:
			return 1
	#-----------------------------------
	def loadMetaDataFromGNUmed(self, aConn = None, aDocumentID = None):
		"""Document meta data loader for GNUmed compatible database."""
		# FIXME: error handling !

		__log__.Log(gmLog.lInfo, 'loading stage 1 (document) metadata from GNUmed compatible database')

		# sanity checks
		if aConn == None:
			__log__.Log(gmLog.lErr, 'Cannot load metadata without database connection.')
			return (1==0)

		if aDocumentID == None:
			__log__.Log(gmLog.lErr, 'Cannot load document metadata without a document ID.')
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
		self.__metadata['type'] = result[1]
		self.__metadata['comment'] = result[2]
		self.__metadata['date'] = result[3]
		self.__metadata['reference'] = result[4]

		# get object level metadata for all objects of this document
		cmd = "SELECT oid, comment FROM doc_obj WHERE doc_id='%s'" % (self.__metadata['id'])
		cursor.execute(cmd)
		matching_rows = cursor.fetchall()
		self.__metadata['objects'] = {}
		for row in matching_rows:
			oid = row[0]
			tmp = {'comment': row[1]}
			# cDocument.metadata->objects->oid->comment
			self.__metadata['objects'][oid] = tmp

		cursor.close()
		__log__.Log(gmLog.lData, 'Meta data: %s' % self.__metadata)

		return (1==1)
	#-----------------------------------
	def getMetaData(self):
		"""Return meta data no matter where we got it from."""
		return self.__metadata
	#-----------------------------------
	def importIntoGNUmed(self, aConn = None, aPatient = None):
		__log__.Log(gmLog.lInfo, 'importing document into GNUmed compatible database')

		# sanity checks
		if aConn == None:
			__log__.Log(gmLog.lErr, 'Cannot import document without database connection.')
			return (1==0)

		if not isinstance(aPatient, docPatient.cPatient):
			__log__.Log (gmLog.lErr, "The object '" + str(aPatient) + "' is not a cPatient instance !")
			return (1==0)

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		try:
			# translate document type
			cmd = "SELECT id FROM doc_type WHERE name='%s'" % (self.__metadata['type'])
			cursor.execute(cmd)
			if cursor.rowcount != 1:
				__log__.Log(gmLog.lErr, 'Document type "%s" is not valid for this database !' % (self.__metadata['type']))
				cursor.close()
				return (1==0)
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
				img_data = img_data + "\n"
				img_data = img_data + "charset:DIN_66003\n"
				img_data = img_data + "last name:" + str(aPatient.lastnames) + "\n"
				img_data = img_data + "first name:" + str(aPatient.firstnames) + "\n"
				img_data = img_data + "date of birth:" + str(aPatient.dob) + "\n"
				img_data = img_data + "reference date:" + str(self.__metadata['date']) + "\n"
				img_data = img_data + "external reference:" + str(self.__metadata['reference']) + "\n"
				# and escape stuff so we can store it in a BYTEA field
				img_data = self.__escapeByteA(img_data)
				# finally insert the data
				cmd = "INSERT INTO doc_obj (doc_id, seq_idx, data) VALUES (currval('doc_med_id_seq'), '" + str(obj['index']) + "', '" + img_data + "')"
				cursor.execute(cmd)

			# insert long document description if available
			if self.__metadata['reference'] != None:
				cmd = "INSERT INTO doc_desc (doc_id, text) VALUES (currval('doc_med_id_seq'), '%s')" % self.__metadata['description']
				cursor.execute(cmd)

			# make permanent what we got so far
			aConn.commit()
			cursor.close()
			__log__.Log(gmLog.lInfo, "document successfully imported")
			return (1==1)

		except:
			aConn.rollback()
			cursor.close()
			exc = sys.exc_info()
			__log__.LogException ("Exception: Cannot import document.", exc)
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
		__log__.Log(gmLog.lInfo, 'exporting document from GNUmed compatible database')

		# sanity checks
		if aConn == None:
			__log__.Log(gmLog.lErr, 'Cannot export document without database connection.')
			return (1==0)

		if not self.__metadata.has_key('objects'):
			__log__.Log(gmLog.lErr, 'Cannot export document without object IDs')
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
			aFile.write(self.__unescapeByteA(str(img_data)))
			aFile.close()

		cursor.close()

		__log__.Log(gmLog.lData, 'Meta data: %s' % self.__metadata)
		return (1==1)
	#-----------------------------------
	def exportObjFromGNUmed(self, aConn = None, aTempDir = None, anObjID = None):
		"""Export object into local file.

		- self.__metadata['objects'] must hold a (potentieally empty)
		  list of object IDs
		- this will usually be accomplished by a previous call to loadMetaDataFromGNUmed()
		"""
		__log__.Log(gmLog.lInfo, 'exporting object from GNUmed compatible database')

		# sanity checks
		if aConn == None:
			__log__.Log(gmLog.lErr, 'Cannot export object without database connection.')
			return None

		if anObjID == None:
			__log__.Log(gmLog.lErr, 'Cannot export object without an object ID.')
			return None

		if not self.__metadata.has_key('objects'):
			__log__.Log(gmLog.lErr, 'Cannot export object without object IDs.')
			return None

		if not self.__metadata['objects'].has_key(anObjID):
			__log__.Log(gmLog.lErr, 'Cannot export object (%s). It does not seem to belong to this document (%d).' % (anObjID, self.__metadata['id']))
			return None

		# if None -> use tempfile module default, else use that path as base directory for temp files
		tempfile.tempdir = aTempDir
		tempfile.template = "obj-"

		# now get the object
		obj = self.__metadata['objects'][anObjID]
		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()
		# retrieve object
		cmd = "SELECT data FROM doc_obj WHERE oid='%s'" % (anObjID)
		cursor.execute(cmd)
		# cDocument.metadata->objects->file name
		obj['file name'] = tempfile.mktemp()
		aFile = open(obj['file name'], 'wb+')
		# it would be a fatal error to see more than one result as oids are supposed to be unique
		aFile.write(self.__unescapeByteA(cursor.fetchone()[0]))
		aFile.close()
		# close our connection
		cursor.close()

		__log__.Log(gmLog.lData, 'Meta data: %s' % self.__metadata)
		return (1==1)
	#-----------------------------------
	def __read_img_list(self, aDescFile = None, aBaseDir = None):
		"""Read list of image files from XML metadata file.

		We assume the order of file names to correspond to the sequence of pages.
		"""
		# sanity check
		if aBaseDir == None:
			aBaseDir = ""

		self.__metadata['objects'] = {}

		i = 1
		# now read the xml file
		for line in fileinput.input(aDescFile):
			# is this a line we want ?
			start_pos = string.find(line,'<image')
			if start_pos == -1:
				continue

			# yes, so check for closing tag
			end_pos = string.find(line,'</image>')
			if end_pos == -1:
				# but we don't do multiline tags
				__log__.Log (gmLog.lErr, "Incomplete <image></image> line. We don't do multiline tags. Sorry.")
				return None

			# extract filename
			# FIXME: this is probably the place to add object level comments ?
			start_pos = string.find(line,'>', start_pos, end_pos) + 1
			file = line[start_pos:end_pos]
			tmp = {}
			tmp['file name'] = os.path.abspath(os.path.join(aBaseDir, file))
			tmp['index'] = i
			# we must use imaginary oid's since we are reading from a file
			self.__metadata['objects'][i] = tmp
			i += 1

		# cleanup
		fileinput.close()

		if len(self.__metadata['objects'].keys()) == 0:
			__log__.Log (gmLog.lErr, "no files found for import")
			return None

		__log__.Log(gmLog.lData, "document data files to be processed: " + str(self.__metadata['objects']))

		return 1
	#-----------------------------------
	def __get_from_xml(self, aTag = None, anXMLfile = None):
		# sanity
		if type(aTag) != types.StringType:
			__log__.Log(gmLog.lErr, "Argument aTag (" + str(aTag) + ") is not a string.")
			return None

		TagStart = "<" + aTag + ">"
		TagEnd = "</" + aTag + ">"

		__log__.Log(gmLog.lInfo, "Retrieving " + TagStart + "content" + TagEnd + ".")

		inTag = 0
		content = []

		for line in fileinput.input(anXMLfile):
			tmp = line

			# this line starts a description
			if string.find(tmp, TagStart) != -1:
				inTag = 1
				# strip junk left of <tag>
				(junk, good_stuff) = string.split (tmp, TagStart, 1)
				__log__.Log(gmLog.lData, "Found tag start in line: junk='%s' content='%s'" % (junk, good_stuff))
				tmp = good_stuff

			# this line ends a description
			if string.find(tmp, TagEnd) != -1:
				# only if tag start has been found already
				if inTag == 1:
					# strip junk right of </tag>
					(good_stuff, junk) = string.split (tmp, TagEnd, 1)
					__log__.Log(gmLog.lData, "Found tag end in line: junk='%s' content='%s'" % (junk, good_stuff))
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
			__log__.Log (gmLog.lData, "%s tag content succesfully read: %s" % (TagStart, str(content)))
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
		__log__.Log(gmLog.lInfo, "starting")
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

		__log__.Log(gmLog.lData, "done: %d total, %d escaped" % (len(aString), c))
		return tmp
	#-----------------------------------
	def __unescapeByteA(self, aByteA):
		__log__.Log(gmLog.lInfo, "starting")
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
						__log__.Log(gmLog.lErr, "Escape logic ambiguity detected. Aborting unescaping.")
						return aByteA
				else:
					__log__.Log(gmLog.lErr, "Trailing single backslash detected. Returning last character unchanged.")
					tmp1 = tmp1 + tmp[self.__i]
			else:
				tmp1 = tmp1 + tmp[self.__i]
			# and point to next char
			self.__i += 1

		__log__.Log(gmLog.lData, "unescaped %s escaped characters" % c)
		return tmp1
#-----------------------------------
class cPatientDocumentList:
	"""Encapsulate a list of documents belonging to a single patient.

	- each document can be represented by a cDocument instance
	"""
	#-----------------------------------
	def __init__(self, aConn = None):
		__log__.Log(gmLog.lData, "Instantiated.")
		# sanity checks
		if aConn == None:
			__log__.Log(gmLog.lErr, 'Cannot get meta data without database connection.')
			return None
		self.__conn = aConn
	#-----------------------------------
	def getList(self, aPatientID = None):
		"""Build a complete list of metadata for all documents of our patient."""
		# sanity checks
		if aPatientID == None:
			__log__.Log(gmLog.lErr, "Cannot associate a patient with her documents without a patient ID.")
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
			__log__.Log(gmLog.lErr, "Cannot load document without document ID.")
			return (1==0)
		else:
			__log__.Log(gmLog.lData, "Trying to load document with id %s" % aDocumentID)

		if (aTempDir == None) or (not os.path.exists (aTempDir)):
			__log__.Log(gmLog.lErr, "The directory '%s' does not exist ! Falling back to default temporary directory." % aTempDir) # which is tempfile.tempdir == None == use system defaults
		else:
			__log__.Log(gmLog.lData, "working into directory '%s'" % aTempDir)

		tmp = cDocument()
		if not tmp.loadMetaDataFromGNUmed(self.__conn, aDocumentID):
			__log__.Log(gmLog.lErr, "Cannot load metadata from database !")
			return (1==0)

		if not tmp.exportDocFromGNUmed(self.__conn, aTempDir):
			__log__.Log(gmLog.lErr, "Cannot export object data from database !")
			return (1==0)

		return tmp.getMetaData()
#----------------------------------------------------------------------------
