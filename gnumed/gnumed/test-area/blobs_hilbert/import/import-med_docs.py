#!/usr/bin/python
#######################################################
"""
- import documents into the document archive
- document descriptions in XML format
- patient data in BDT format
- one document (possibly spanning multiple pages)
  per repository subdirectory

search for FIXME to find places to fix

@copyright: GPL
"""
#######################################################
# modules
import os, fileinput, string, time, sys, os.path

# location of our modules
sys.path.append(os.path.join('..', 'modules'))

import gmLog, gmCfg

from docPatient import cPatient
from docDocument import cDocument
from docDatabase import cDatabase
#######################################################
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__ = "$Revision: 1.4 $"

__log__ = gmLog.gmDefLog
__cfg__ = gmCfg.gmDefCfg

myDB = None
#------------------------------------------
def import_from_dir(aDir):
	__log__.Log (gmLog.lInfo, "importing from repository sub dir " + aDir)

	# look for checkpoint file whether frontend action on this dir is complete
	checkpoint_file = __cfg__.get("metadata", "checkpoint")
	if not os.path.exists (os.path.join(aDir, checkpoint_file)):
		__log__.Log (gmLog.lErr, "skipping " + aDir + ": semaphore file '" + checkpoint_file + "' not found")
		return None

	# get patient data from BDT file
	pat_file = __cfg__.get("metadata", "patient")
	aPatient = cPatient()
	if not aPatient.loadFromFile("xdt", os.path.join(aDir, pat_file)):
		__log__.Log(gmLog.lErr, "Skipping \"%s\": problem with reading patient data from xDT file \"%s\"" % (aDir, pat_file))
		return None

	# setup document object
	aDoc = cDocument()
	if aDoc == None:
		__log__.Log(gmLog.lErr, "cannot instantiate document object")
		return None

	# and load corresponding metadata
	if not aDoc.loadMetaDataFromXML(aDir, __cfg__):
		__log__.Log(gmLog.lErr, "cannot load document meta data")
		return None

	# now import the good stuff
	if not myDB.importDocument (aPatient, aDoc):
		__log__.Log(gmLog.lErr, "cannot import documents into database")
		return None

	# move/delete input files if all is well
	# FIXME

	return (1==1)
#------------------------------------------
def standalone():
	REPOSITORIES = string.split(__cfg__.get("source", "repositories"))
	for REPOSITORY in REPOSITORIES:
		__log__.Log (gmLog.lInfo, "importing from repository " + REPOSITORY)
		# get the list of document directories in the repository
		dirlist = os.listdir (REPOSITORY)
		# now handle one dir after another
		for theDir in dirlist:
			# we don't check for errors here since we just move on to the next dir
			import_from_dir(os.path.join(REPOSITORY, theDir))
#------- MAIN ----------------------
__log__.SetAllLogLevels(gmLog.lData)
if __cfg__ == None:
	__log__.Log (gmLog.lErr, "cannot run without config file")
	sys.exit(1)

__log__.Log (gmLog.lInfo, "starting import")

if __name__ == "__main__":
	__log__.Log (gmLog.lInfo, "running standalone")

	# connect to DB
	myDB = cDatabase(__cfg__)
	if myDB == None:
		__log__.Log (gmLog.lErr, "cannot create document database connection object")
		sys.exit(1)

	if myDB.connect() == None:
		__log__.Log (gmLog.lErr, "cannot connect to document database")
		sys.exit(1)

	try:
		standalone()
	except:
		exc = sys.exc_info()
		__log__.LogException ("Exception: Unhandled exception encountered.", exc)
		raise

	myDB.disconnect()

__log__.Log (gmLog.lInfo, "done importing")

sys.exit(0)
