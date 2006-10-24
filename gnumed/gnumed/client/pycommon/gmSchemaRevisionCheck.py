"""GnuMed schema revision checker.

This module will collect schema revision information from the GnuMed backend
and provides methods that can be called from modules to check if they can safely
work with the revision provided.
Schema names are the filenames of the sql files used to create this schema on 
bootstrap with the '.sql'-suffix stripped.

license: GPL

Notes: We cannot actually assume all revisions to be listed in service
       'default' but we can assume the relevant revision to be listed
	   in the very same service the user/caller is going to look for
	   the actual schema tables. I would solve this by lazy-fetching
	   on-access and caching.

Should not gmSchemaRevisionChecker inherit from cBorg ? See gmCurrentPatient.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmSchemaRevisionCheck.py,v $
# $Id: gmSchemaRevisionCheck.py,v 1.4 2006-10-24 13:20:34 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "Hilmar Berger <ju0815nk@gmx.net>"

# access our modules
import sys, os.path, string, re

# start logging
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmExceptions, gmPG2

#============================================================
class gmSchemaRevisionChecker:
	"""Checks the schema revisions in a GnuMed database.

	all instances of this class share the same dictionary
	this way we have to get the data only once
	"""
	_revisions = {}
	_initialized = 0
	#--------------------------------------------------------
	def __init__(self):
		"""Initializes the version list."""
		# check if the list has already been initialized
		# by another instance
		if not gmSchemaRevisionChecker._initialized:
			self._getRevisions()
	#--------------------------------------------------------
	def getSchemaRevision(self,schema = None):
		"""Returns the current revision of a schema."""
		if gmSchemaRevisionChecker._revisions.has_key(schema):
			return gmSchemaRevisionChecker._revisions[schema]
	#--------------------------------------------------------
	def checkSchemaRevision(self,schema = None, minRevision = '0.0', exact = 0):
		"""Check the Revision of a particular schema.

		If exact is 0, this method will check if the current revision is at
		least minRevision. If exact = 1, it will check if it is exactly 
		minRevision.
		Returns 1 if the current revision suffices the condition named above,
		0 if not and None if the schema was not found or if the revision is
		not of format 'x.y'.
		minRevision can be passed as string or float.
		"""
		if gmSchemaRevisionChecker._revisions.has_key(schema):
			# get the current revisions
			version = gmSchemaRevisionChecker._revisions[schema]
			# check if minRevision is really of form 'x.y'
			if type(eval(str(minRevision))) is not type(1.1):
				return None
			# split both current and min revision in major and minor part
			currMajor, currMinor = version.split('.')
			minMajor, minMinor = str(minRevision).split('.')
			# check if the current version is at least minRevision
			if not exact:
				if int(currMajor) > int(minMajor):
					return 1
				elif int(currMajor) == int(minMajor) and int(currMinor) >= int(minMinor):
					return 1
				else:
					return 0
			# check if current version = minRevision					
			else:
				if currMajor == minMajor and currMinor == minMinor:
					return 1
				else:
					return 0
	#--------------------------------------------------------
	def _getRevisions(self):
		"""Fetches the Revisions from the backend.

		FIXME: see Notes section at top.

		We assume that gm_schema_revision is on service 'default'.
		Sets the class-wide dictionary '_revisions'.
		"""
		# retrieve revisions
		cmd = "select filename, version from gm_schema_revision"
		result = gmPG.run_ro_query('default', cmd, None)
		if result is None:
			_log.Log(gmLog.lWarn, 'unable to fetch schema revision information')
			return None

		# extract schema and revision from stored strings
		schemaPattern = re.compile("\$RCSfile: (\S+).sql")
		versionPattern = re.compile("\$Revisi..: (\d+.\d+)")
		for entry in result:
			version = '?'
			schema = '?'
			schemaMatch = schemaPattern.search(entry[0])
			versionMatch = versionPattern.search(entry[1])
			if schemaMatch is not None:
				schema = schemaMatch.group(1)
			if versionMatch is not None:
				version = versionMatch.group(1)
			_log.Log(gmLog.lData, 'found schema: %s revision %s' % (schema,version))
			# check for malformed entries; these will not be stored
			if version == '?' or schema == '?':
				_log.Log(gmLog.lData, 'malformed schema entry found: %s %s' % (entry[0],entry[1]))
			else:
				gmSchemaRevisionChecker._revisions[schema] = version

		# mark _revisions as initialized
		gmSchemaRevisionChecker._initialized = 1
#============================================================
# main/testing
#------------------------------------------------------------
if __name__ == "__main__":
	a = gmSchemaRevisionChecker()
	x = a.getSchemaRevision('gmconfiguration')
	print a.checkSchemaRevision('gmconfiguration',1.1), " should be 1"
	print a.checkSchemaRevision('gmconfiguration','1.100000'), " should be 0"
	print a.checkSchemaRevision('gmconfiguration',x), " should be 1"
	print a.checkSchemaRevision('gmconfiguration',float(x)+0.1,exact = 1), " should be 0"
#============================================================
# $Log: gmSchemaRevisionCheck.py,v $
# Revision 1.4  2006-10-24 13:20:34  ncq
# - gmPG -> gmPG2
#
# Revision 1.3  2004/03/20 19:46:38  ncq
# - cleanup
#
# Revision 1.2  2004/02/25 09:46:21  ncq
# - import from pycommon now, not python-common
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.5  2003/11/28 23:03:54  ncq
# - comments and cleanup
# - since I am a control-freak I like this code, hehe :-)
#
# Revision 1.4  2003/11/28 16:12:52  hinnef
# - removed dead code
#
# Revision 1.3  2003/11/28 10:31:55  ncq
# - use run_ro_query() in get_schema_revisions
#
# Revision 1.2  2003/11/28 07:57:20  hinnef
# - corrected revision match pattern that had been overwritten by cvs
#
# Revision 1.1  2003/11/27 18:16:55  hinnef
# - initial checkin
#
