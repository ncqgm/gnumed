#!/usr/bin/python

"""docPatient.py encapsulates patient operations for BLOB import.

@copyright: GPL
"""
#=======================================================================================
import os.path, string, fileinput

import gmLog

__author__	= "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__	= "$Revision: 1.1 $"
__log__		= gmLog.gmDefLog

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
	pass
	self.ID = None
    #-----------------------------------
    def getFromXDT (self, anXdtFile):
	"""
	Read the _first_ patient from an xDT compatible file
	"""
	# check for BDT patient data file
	if not os.path.exists (anXdtFile):
	    __log__.Log(gmLog.lErr, "patient data file (xDT) '" + str(anXdtFile) + "' not found")
	    raise IOError, "patient data file (xDT) '" + str(anXdtFile) + "' not found"

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
		    __log__.Log(gmLog.lData, "found item [" + field + "]: " + tmpPat[field])
		    data_found = data_found + 1
		    # leave this loop
		    break

	# cleanup
	fileinput.close()

	# looped over all lines or found all data
	if data_found != len(xdt_pat_fields):
	    __log__.Log(gmLog.lErr, "could not find sufficient patient data in xDT file " + str(anXdtFile))
	    __log__.Log(gmLog.lErr, "found only " + str(data_found) + " items:")
	    __log__.Log(gmLog.lErr, str(aPatient))
	    raise EOFError, "could not find sufficient patient data in xDT file " + str(anXdtFile)

	# now normalize what we got
	self.firstnames = tmpPat['first name']
	self.lastnames = tmpPat['last name']

	# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
	if tmpPat.has_key('date of birth') != 1:
	    __log__.Log(gmLog.lErr,'patient has no "date of birth" field')
	    raise AttributeError, 'patient has no "date of birth" field'
	else:
	    self.dob = tmpPat['date of birth'][4:] + tmpPat['date of birth'][2:4] + tmpPat['date of birth'][:2]

	# mangle gender
	if tmpPat.has_key('gender') != 1:
	    __log__.Log(gmLog.lErr,'patient has no "gender" field')
	    raise AttributeError, 'patient has no "gender" field'
	else:
	    self.gender = xdt2gm_gender_map[tmpPat['gender']]

	__log__.Log(gmLog.lData, self.toString())

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
	__log__.Log(gmLog.lInfo, 'importing patient into GNUmed compatible database')

	# sanity check
	if aConn == None:
	    __log__.Log(gmLog.lErr, 'Cannot import patient without connection object.')
	    return (1==0)

	# start our transaction (done implicitely by defining a cursor)
	cursor = aConn.cursor()

	# first check out whether the patient is already in the database
	#cmd = "SELECT id FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND dob='%s' AND gender='%s' LIMIT 2" % (self.firstnames, self.lastnames, self.dob, self.gender)
	cmd = "SELECT id FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND dob='%s' AND gender='%s'" % (self.firstnames, self.lastnames, self.dob, self.gender)
	cursor.execute(cmd)
	pat_ids = cursor.fetchall()
	__log__.Log(gmLog.lData, "matching patient ID(s): " + str(pat_ids))

	# patient already there
	if len(pat_ids) == 1:
	    (self.ID,) = pat_ids[0]
	    __log__.Log(gmLog.lData, "patient already in database: " + str(pat_ids))
	    return (1==1)
	# more than one patient matching - die
	elif len(pat_ids) > 1:
	    __log__.Log(gmLog.lErr, "More than one patient matched - ambiguity - integrity at stake - aborting. " + str(pat_ids))
	    return (1==0)
	# not in there yet
	elif len(pat_ids) == 0:
	    __log__.Log(gmLog.lData, "patient not yet in database")

	cmd = "INSERT INTO v_basic_person (firstnames, lastnames, dob, cob, gender) VALUES ('%s', '%s', '%s', '%s', '%s');" % (self.firstnames, self.lastnames, self.dob, self.cob, self.gender)
	cursor.execute(cmd)
	cmd = "SELECT last_value FROM identity_id_seq"
	cursor.execute(cmd)
	self.ID = cursor.fetchone()[0]

	aConn.commit()
	cursor.close()

	__log__.Log(gmLog.lData, "patient ID: " + str(self.ID))
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
	__log__.Log(gmLog.lInfo, 'getting patient ID from GNUmed compatible database')

	if self.ID != None:
	    return ((1==1), self.ID)

	# sanity check
	if aConn == None:
	    __log__.Log(gmLog.lErr, 'Cannot retrieve patient ID without connection object.')
	    return ((1==0), None)

	# start our transaction (done implicitely by defining a cursor)
	cursor = aConn.cursor()

	# get matching patients
	cmd = "SELECT id FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND dob='%s' AND gender='%s'" % (self.firstnames, self.lastnames, self.dob, self.gender)
	cursor.execute(cmd)
	pat_ids = cursor.fetchall()
	__log__.Log(gmLog.lData, "matching patient ID(s): " + str(pat_ids))
	aConn.commit()
	cursor.close()

	# one patient there (most likely case first)
	if len(pat_ids) == 1:
	    (self.ID,) = pat_ids[0]
	    return ((1==1), self.ID)
	# more than one patient matching
	elif len(pat_ids) > 1:
	    __log__.Log(gmLog.lWarn, "More than one patient matched.")
	    return ((1==0), pat_ids)
	# not in there
	elif len(pat_ids) == 0:
	    __log__.Log(gmLog.lData, "No matching patient(s).")
	    return ((1==0), None)
	else:
	    __log__.Log(gmLog.lErr, "This should not happen.")
	    return ((1==0), None)
#-----------------------------------
#------- MAIN ----------------------
#-----------------------------------
if __name__ == "__main__":
    # test framework if run by itself

    import sys
    patfile = sys.argv[1]
    __log__.Log(gmLog.lInfo, "reading patient data from xDT file " + patfile)

    aPatient = cPatient()
    if aPatient.getFromXDT(patfile):
	print aPatient.firstnames
	print aPatient.lastnames
	print aPatient.dob
	print aPatient.gender
        print aPatient.cob
    else:
	print "Crying foul !"
