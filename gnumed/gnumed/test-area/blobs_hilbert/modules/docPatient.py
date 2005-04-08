#!/usr/bin/python

"""docPatient.py encapsulates patient operations for BLOB import.

@copyright: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/modules/Attic/docPatient.py,v $
__version__	= "$Revision: 1.10 $"
__author__	= "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#=======================================================================================
import os.path, string, fileinput, sys

import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	_ = lambda x:x

# patient record fields
dat2xdtID = {\
	'last name': '3101',\
	'first name': '3102',\
	'date of birth': '3103',\
	'gender': '3110'\
}
#    'city': '3106',\
#    'street': '3107',\

# probably gnumed compatible
xdt2gm_gender_map = {\
	'1': 'm',\
	'2': 'f',\
	'm': 'm',\
	'f': 'f'\
}

gm2long_gender_map = {\
	'm': _('male'),\
	'f': _('female')\
}

# XDT:
# dob: ddmmyyyy
# gender: 1 - male, 2 - female

xdt_pat_fields = ('last name', 'first name', 'date of birth', 'gender')
#=======================================================================================
class cPatient:
	#-----------------------------------
	ID = None
	firstnames = ""
	lastnames = ""
	gender = ""
	dob = ""
	cob = "DE"
	#-----------------------------------
	def __init__(self):
		self.ID = None
		self.__file_reader = {'xdt': self.__load_from_xdt}
	#-----------------------------------
	def loadFromFile (self, aType, aFileName):
		"""Read the first patient from a file.

		- aType lets you specify what type of file it is
		"""
		# sanity checks
		if not self.__file_reader.has_key(aType):
			_log.Log(gmLog.lErr, 'No handler for file type \"%s\" available.' % aType)
			_log.Log(gmLog.lErr, 'Cannot retrieve patient from file \"%s\".' % aFileName)
			return None
		if not os.path.exists (aFileName):
			_log.Log(gmLog.lErr, "patient data file \"%s\" (type \"%s\") not found" % (aFileName, aType))
			return None

		return self.__file_reader[aType](aFileName)
	#-----------------------------------
	def __load_from_xdt (self, anXdtFile):
		"""Read the _first_ patient from an xDT compatible file."""
		tmpPat = {}

		# read patient data
		data_found = 0
		for line in fileinput.input(anXdtFile):
			# found all data already ?
			if data_found == len(xdt_pat_fields):
				# yep - close input
				fileinput.close()
				# leave loop
				break

			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','')

			for field in xdt_pat_fields:
				# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
				if line[3:7] == dat2xdtID[field]:
					tmpPat[field] = line[7:]
					_log.Log(gmLog.lData, "found item [" + field + "]: " + tmpPat[field])
					data_found = data_found + 1
					# leave this loop
					break
		# cleanup
		fileinput.close()

		# looped over all lines or found all data
		if data_found != len(xdt_pat_fields):
			_log.Log(gmLog.lErr, "could not find sufficient patient data in xDT file " + str(anXdtFile))
			_log.Log(gmLog.lErr, "found only " + str(data_found) + " items:")
			_log.Log(gmLog.lErr, str(aPatient))
			return None

		# now normalize what we got
		self.firstnames = tmpPat['first name']
		self.lastnames = tmpPat['last name']

		# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
		if tmpPat.has_key('date of birth') != 1:
			_log.Log(gmLog.lErr,'patient has no "date of birth" field')
			return None
		else:
			self.dob = tmpPat['date of birth'][4:] + tmpPat['date of birth'][2:4] + tmpPat['date of birth'][:2]

		# mangle gender
		if tmpPat.has_key('gender') != 1:
			_log.Log(gmLog.lErr,'patient has no "gender" field')
			return None
		else:
			self.gender = xdt2gm_gender_map[tmpPat['gender']]

		_log.Log(gmLog.lData, self.toString())

		# all is well, so return true
		return (1==1)
	#-----------------------------------
	def toString(self):
		return (self.firstnames + " " + self.lastnames + " (" + self.gender + "), " + self.dob + " (" + self.cob + ")")
	#-----------------------------------
	def importIntoGNUmed(self, aConn = None):
		"""Import a patient into the GNUmed database.

		This is not a complete import. It just imports the data
		necessary for relating BLOBs to patients.
		"""
		_log.Log(gmLog.lInfo, 'importing patient into GNUmed compatible database')

		# sanity check
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot import patient without connection object.')
			return (1==0)

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		# first check out whether the patient is already in the database
		#cmd = "SELECT pk_identity FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND dob='%s' AND gender='%s' LIMIT 2" % (self.firstnames, self.lastnames, self.dob, self.gender)
		cmd = "SELECT pk_identity FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND dob='%s' AND gender='%s'" % (self.firstnames, self.lastnames, self.dob, self.gender)
		try:
			cursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed" % cmd, sys.exc_info(), fatal=0)
			raise
		pat_ids = cursor.fetchall()
		_log.Log(gmLog.lData, "matching patient ID(s): " + str(pat_ids))

		# patient already there
		if len(pat_ids) == 1:
			(self.ID,) = pat_ids[0]
			_log.Log(gmLog.lData, "patient already in database: " + str(pat_ids))
			return (1==1)
		# more than one patient matching - die
		elif len(pat_ids) > 1:
			_log.Log(gmLog.lErr, "More than one patient matched - ambiguity - integrity at stake - aborting. " + str(pat_ids))
			return (1==0)
		# not in there yet
		elif len(pat_ids) == 0:
			_log.Log(gmLog.lData, "patient not yet in database")

		cmd = "INSERT INTO v_basic_person (firstnames, lastnames, dob, cob, gender) VALUES ('%s', '%s', '%s', '%s', '%s');" % (self.firstnames, self.lastnames, self.dob, self.cob, self.gender)
		try:
			cursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed" % cmd, sys.exc_info(), fatal=0)
			raise
		cmd = "SELECT last_value FROM identity_id_seq"
		try:
			cursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed" % cmd, sys.exc_info(), fatal=0)
			raise
		self.ID = cursor.fetchone()[0]

		aConn.commit()
		cursor.close()

		_log.Log(gmLog.lData, "patient ID: " + str(self.ID))
		return (1==1)
	#-----------------------------------
	def getIDfromGNUmed(self, aConn = None):
		"""Retrieve patient ID from GNUmed database.

		Returns a tuple:
		(true, ID)		- exactly one match
		(false, None)		- problem or no match
		(false, sequence)	- several matches

		FIXME: what happens if there's insufficient descriptive data ?
		"""
		_log.Log(gmLog.lInfo, 'getting patient ID from GNUmed compatible database')

		if self.ID != None:
			return ((1==1), self.ID)

		# sanity check
		if aConn == None:
			_log.Log(gmLog.lErr, 'Cannot retrieve patient ID without connection object.')
			return ((1==0), None)

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		# get matching patients
		cmd = "SELECT pk_identity FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND dob='%s' AND gender='%s'" % (self.firstnames, self.lastnames, self.dob, self.gender)
		cursor.execute(cmd)
		pat_ids = cursor.fetchall()
		_log.Log(gmLog.lData, "matching patient ID(s): " + str(pat_ids))
		aConn.commit()
		cursor.close()

		# one patient there (most likely case first)
		if len(pat_ids) == 1:
			(self.ID,) = pat_ids[0]
			return ((1==1), self.ID)
		# more than one patient matching
		elif len(pat_ids) > 1:
			_log.Log(gmLog.lWarn, "More than one patient matched.")
			return ((1==0), pat_ids)
		# not in there
		elif len(pat_ids) == 0:
			_log.Log(gmLog.lData, "No matching patient(s).")
			return ((1==0), None)
		else:
			_log.Log(gmLog.lErr, "This should not happen.")
			return ((1==0), None)
	#-----------------------------------
	def getDocsFromGNUmed(self, aConn = None, aCfg = None):
		"""Build a complete list of metadata for all documents of our patient.

		Note that we DON'T keep a list of those documents local to cPatient !
		"""
		_log.Log(gmLog.lInfo, 'getting documents from GNUmed compatible database')

		# sanity check
		if aConn is None:
			_log.Log(gmLog.lErr, 'Cannot load documents without connection object.')
			return None
		if aCfg is None:
			_log.Log(gmLog.lErr, 'Cannot load documents without config parser.')
			return None

		if self.ID is None:
			_log.Log(gmLog.lErr, "Cannot associate a patient with her documents without a patient ID.")
			return None

		import docDocument

		# start our transaction (done implicitely by defining a cursor)
		cursor = aConn.cursor()

		# get document IDs
		cmd = "SELECT id from doc_med WHERE patient_id='%s'" % self.ID
		cursor.execute(cmd)
		matching_rows = cursor.fetchall()

		if cursor.rowcount == 0:
			_log.Log(gmLog.lErr, "No documents found (%s) for patient with ID %s." % (matching_rows, self.ID))
			return None

		_log.Log(gmLog.lData, "document IDs: %s" % matching_rows)

		# and load docs
		docs = {}
		for row in matching_rows:
			doc_id = row[0]
			docs[doc_id] = docDocument.cDocument(aCfg)
			docs[doc_id].loadMetaDataFromGNUmed(aConn, doc_id)

		cursor.close
		return docs
	#-----------------------------------
	def setID (self, anID = None):
		# sanity checks
		if anID == None:
			_log.Log(gmLog.lErr, "Cannot associate a patient with her documents without a patient ID.")
			return None

		if self.ID != None:
			_log.Log(gmLog.lErr, "Patient already has an associated ID (%s). It is not safe to change it arbitrarily." % self.ID)

		_log.Log(gmLog.lData, "Setting patient ID to %s." % anID)

		self.ID = anID
#-----------------------------------
#------- MAIN ----------------------
#-----------------------------------
if __name__ == "__main__":
	# test framework if run by itself
	_log.SetAllLogLevels(gmLog.lData)

	import sys
	patfile = sys.argv[1]
	_log.Log(gmLog.lInfo, "reading patient data from xDT file " + patfile)

	aPatient = cPatient()
	if aPatient.loadFromFile("xdt", patfile):
		print aPatient.firstnames
		print aPatient.lastnames
		print aPatient.dob
		print aPatient.gender
		print aPatient.cob
	else:
		print "Crying foul !"
