#!/usr/bin/python
#######################################################
"""
- proof-of-concept text mode document export client

search for FIXME to find places to fix

@copyright: GPL
"""
#######################################################
# modules
import sys, os.path

sys.path.append(os.path.join("..", "modules"))

import gmLog, gmCfg

from docPatient import cPatient
from docDocument import cDocument, cPatientDocumentList
from docDatabase import cDatabase
import docMime
#------------------------------------------
myDB = None
myCfg = gmCfg.gmDefCfg
myDocList = None
# get a convenient handle for the default logger
__log__ = gmLog.gmDefLog
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__ = "$Revision: 1.2 $"
#------------------------------------------
#------------------------------------------
def selectPatient():
	# read patient id's from database
	cmd = "SELECT id, firstnames, lastnames FROM v_basic_person LIMIT 10"
	patients = myDB.runArbitraryQuery(cmd)
	if patients == None:
		__log__.Log(gmLog.lErr, "Cannot read first 10 patients from database !")
		return None

	# display patients
	print "Showing first 10 patients in database."
	print "--------------------------------------------------------"
	for pat in patients:
		print "ID: %9s | name: %s %s" % (pat[0], pat[1], pat[2])
	print "--------------------------------------------------------"

	# let user select one
	print "Please select patient for which to show available documents !\n"
	aPatID = raw_input("patient ID: ").strip()
	if aPatID.isdigit():
		return aPatID
	else:
		return None
#------------------------------------------
def selectDocument(aPatientID = None):
	# sanity checks
	if aPatientID == None:
		__log__.Log(gmLog.lErr, "Cannot retrieve documents without knowing the patient !")
		return None
	# read document IDs from database
	metadata = myDocList.getList(aPatientID)
	if len(metadata) == 0:
		__log__.Log(gmLog.lErr, "No documents found for this patient (ID = %s)." % aPatientID)
		return None

	# display documents
	print "Showing documents for this patient."
	print "-------+------------+---------------------------+-------+----------"
	print "     # | ref date   | comment                   |  type | reference"
	print "-------+------------+---------------------------+-------+----------"
	for i in range(len(metadata)):
		obj = metadata[i]
		print "%6s | %10s | %25s | %5s | %10s" % (i, obj['date'][:10], obj['comment'][:25], obj['type'], obj['reference'][:10])
	print "-------+------------+---------------------------+-------+----------"

	# let user select one
	print "Please select a document for export !\n"
	docidx = raw_input("document #: ").strip()
	if docidx.isdigit():
		return metadata[int(docidx)]['id']
	else:
		return None
#------------------------------------------
# Main
#------------------------------------------
__log__.Log (gmLog.lInfo, "starting export")

if __name__ == "__main__":
	__log__.Log (gmLog.lInfo, "running standalone")

	if myCfg == None:
		__log__.Log (gmLog.lErr, "cannot run without config file")
		sys.exit()

	# connect to DB
	myDB = cDatabase(myCfg)
	if myDB == None:
		__log__.Log (gmLog.lErr, "cannot create Befund database connection object")
		sys.exit()

	if myDB.connect() == None:
		__log__.Log (gmLog.lErr, "cannot connect to Befund database")
		sys.exit()

	print "Testing document archive export."
	print "================================"

	patid = selectPatient()
	if patid != None:
		myDocList = cPatientDocumentList(myDB.getConn())
		docid = selectDocument(patid)
		if docid != None:
			print "OK, loading document with id", docid
			metadata = myDocList.getDocument(myCfg.get("export", "target"), aDocumentID=docid)
			print "We could now hand over the data to a viewer:"
			print metadata
			for obj in metadata['objects']:
				print "----------------------------------------"
				fname = obj['file name']
				mime_type = docMime.guess_mimetype(fname)
				print "file		: %s" % fname
				print "comment	: %s" % obj['comment']
				print "mime type: %s" % mime_type
				print "view cmd	: %s" % docMime.get_viewer_cmd(mime_type, fname)

	myDB.disconnect()

__log__.Log (gmLog.lInfo, "done exporting")
