#!/usr/bin/env python

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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/import/Attic/import-med_docs.py,v $
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__ = "$Revision: 1.2 $"

# modules
import os, fileinput, string, time, sys, os.path

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

import gmCfg
_cfg = gmCfg.gmDefCfgFile
if _cfg is None:
	_log.Log (gmLog.lPanic, "cannot run without config file")
	sys.exit(1)

import gmI18N, gmXdtObjects

#from docPatient import cPatient
from docDocument import cDocument
from docDatabase import cDatabase

myDB = None
#=========================================================
def can_import(aDir):
	"""Check if all preconditions for import are met."""

	# is frontend action on this dir complete ?
	checkpoint_file = os.path.join(aDir, _cfg.get("import", "checkpoint file"))
	if not os.path.exists(checkpoint_file):
		_log.Log (gmLog.lErr, "skipping [%s]: semaphore file [%s] not found" % (aDir, checkpoint_file))
		return None

	# is dir already locked ?
	# this would be due to
	#  a) somebody else is currently importing
	#  b) we died the last time around
	lock_file = os.path.join(aDir, _cfg.get("import", "lock file"))
	if os.path.exists(lock_file):
		_log.Log (gmLog.lErr, "skipping [%s]: lock file [%s] already exists" % (aDir, lock_file))
		return None

	# lock it now
	try:
		lock = open(lock_file, "w")
	except:
		exc = sys.exc_info()
		_log.LogException("Cannot lock [%s] for import." % aDir, exc)
		return None

	lock.close()
	return 1
#---------------------------------------------------------
def unlock(aDir):
	"""Delete lock file again in case we failed."""
	lock_file = os.path.join(aDir, _cfg.get("import", "lock file"))
	try:
		os.remove(lock_file)
	except:
		exc = sys.exc_info()
		_log.LogException("Cannot unlock [%s] for subsequent import retries." % aDir, exc, fatal=0)
#---------------------------------------------------------
def mark_for_deletion(aDir):
	"""Mark directory for removal."""
	done_file = os.path.join(aDir, _cfg.get("import", "completion marker file"))
	try:
		done = open(done_file,"w")
	except:
		_log.LogException("Cannot mark [%s] as successfully imported." % aDir, sys.exc_info())
		return None
	done.close()
	return 1
#---------------------------------------------------------
def import_from_dir(aDir):
	_log.Log (gmLog.lInfo, "importing from repository sub dir [%s]" % aDir)

	# sanity checks
	if not can_import(aDir):
		return None

	# get patient data from xDT file
	tmp = _cfg.get("import", "patient file")
	pat_file = os.path.abspath(os.path.join(aDir, tmp))
	pat_format = _cfg.get("import", "patient file format")
	_log.Log(gmLog.lWarn, 'patient file format is [%s]' % pat_format)
	_log.Log(gmLog.lWarn, 'note that we only handle xDT files so far')

	# get patient data from xDT file
	try:
		__xdt_pat = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
	except:
		_log.LogException("Skipping [%s]: problem reading patient data from %s file [%s]" % (aDir, pat_format, pat_file), sys.exc_info())
		unlock(aDir)
		return None

	# setup document object
	aDoc = cDocument(aCfg = _cfg)
	if aDoc is None:
		_log.Log(gmLog.lErr, "cannot instantiate document object")
		unlock(aDir)
		return None

	# FIXME: pass file name to document
	# and load corresponding metadata
	if not aDoc.loadMetaDataFromXML(aBaseDir = aDir, aSection = "metadata"):
		_log.Log(gmLog.lErr, "cannot load document meta data")
		unlock(aDir)
		return None

	# now import the good stuff
	if not myDB.importDocument (__xdt_pat, aDoc):
		_log.Log(gmLog.lErr, "cannot import documents into database")
		unlock(aDir)
		return None

	# mark input files for removal if all is well
	# (but keep import lock so we don't accidentally import twice)
	mark_for_deletion(aDir)
	return 1
#------------------------------------------
def standalone():
	REPOSITORIES = _cfg.get("import", "repositories")
	for REPOSITORY in REPOSITORIES:
		REPOSITORY = os.path.abspath(os.path.expanduser(REPOSITORY))
		_log.Log (gmLog.lInfo, "importing from repository [%s]" % REPOSITORY)
		# get the list of document directories in the repository
		dirlist = os.listdir (REPOSITORY)
		# now handle one dir after another
		for theDir in dirlist:
			# we don't check for errors here since we just move on to the next dir
			import_from_dir(os.path.join(REPOSITORY, theDir))

	# FIXME: update doc types in config file here
#==========================================
# MAIN
#------------------------------------------
_log.Log (gmLog.lInfo, "starting import")

if __name__ == "__main__":
	_log.Log (gmLog.lInfo, "running standalone")

	# connect to DB
	myDB = cDatabase(_cfg)
	if myDB is None:
		_log.Log (gmLog.lErr, "cannot create document database connection object")
		sys.exit(1)

	if myDB.connect(readonly_flag=0) is None:
		_log.Log (gmLog.lErr, "cannot connect to document database")
		sys.exit(1)

	try:
		standalone()
	except:
		exc = sys.exc_info()
		_log.LogException ("Exception: Unhandled exception encountered.", exc)
		raise

	myDB.disconnect()

_log.Log (gmLog.lInfo, "done importing")

sys.exit(0)

#=========================================================
# $Log: import-med_docs.py,v $
# Revision 1.2  2004-01-06 23:22:16  ncq
# - use XdtObjects business objects
#
# Revision 1.1  2003/03/01 15:39:49  ncq
# - moved here from test-area
#
# Revision 1.12  2003/01/30 23:47:41  ncq
# - more fallout
#
# Revision 1.11  2003/01/30 23:32:07  ncq
# - missing _cfg in doc = cDocument()
#
# Revision 1.10  2003/01/24 09:22:17  ncq
# - need gmI18N for some modules
#
# Revision 1.9  2002/12/22 23:59:31  ncq
# - mark successfully imported directories for later removal
#
# Revision 1.8  2002/11/23 16:45:21  ncq
# - make work with pyPgSQL
# - fully working now but needs a bit of polish
#
# Revision 1.7  2002/11/08 15:52:18  ncq
# - make it work with pyPgSQL
#
# Revision 1.6  2002/10/01 09:47:36  ncq
# - sync, should sort of work
#
