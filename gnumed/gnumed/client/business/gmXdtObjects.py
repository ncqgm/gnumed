"""GnuMed German XDT parsing objects.

This encapsulates some of the XDT data into
objects for easy access.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXdtObjects.py,v $
# $Id: gmXdtObjects.py,v 1.1 2003-02-17 23:33:14 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "S.Hilbert"
__license__ = "GPL"

import os.path, sys, fileinput, string

# access our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

from gmExceptions import ConstructorError
from gmXdtMappings import name_xdtID_map, xdt_gmgender_map
#==============================================================
xdt_pat_fields = ('last name', 'first name', 'date of birth', 'gender')

class xdtPatient:

	def __init__(self, anXdtFile = None):
		# sanity checks
		if anXdtFile is None:
			raise ConstructorError, "need XDT file name"
		if not os.path.exists(os.path.abspath(anXdtFile)):
			raise ConstructorError, "XDT file [%s] does not exist" % anXdtFile

		self.filename = anXdtFile

		if not self.__load_from_xdt():
			raise ConstructorError, "XDT file [%s] does not contain enough patient details" % anXdtFile
	#-----------------------------------
	def __load_from_xdt(self):
		"""Read the _first_ patient from an xDT compatible file."""

		self.__data = {}

		# read patient data
		fields_found = 0
		for line in fileinput.input(self.filename):
			# found all data already ?
			if fields_found == len(xdt_pat_fields):
				# yep - close input
				fileinput.close()
				# leave loop
				break

			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','')

			for field in xdt_pat_fields:
				# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
				if line[3:7] == name_xdtID_map[field]:
					self.__data[field] = line[7:]
					#_log.Log(gmLog.lData, "found item [%s]: %s" % (field, self.__data[field]))
					fields_found = fields_found + 1
					# leave this loop
					break
		# cleanup
		fileinput.close()

		# found all data ?
		if fields_found != len(xdt_pat_fields):
			_log.Log(gmLog.lErr, "did not find sufficient patient data in XDT file [%s]" % self.filename)
			_log.Log(gmLog.lErr, "found only %s items:" % fields_found)
			_log.Log(gmLog.lErr, self.__data)
			return None

		# now normalize what we got
		#  mangle date of birth into ISO8601 (yyyymmdd) for Postgres
		if not self.__data.has_key('date of birth'):
			_log.Log(gmLog.lErr, 'patient has no "date of birth" field')
			return None
		else:
			self.__data['dob day'] = self.__data['date of birth'][:2]
			self.__data['dob month'] = self.__data['date of birth'][2:4]
			self.__data['dob year'] = self.__data['date of birth'][4:]

		#  mangle gender
		if not self.__data.has_key('gender'):
			_log.Log(gmLog.lErr, 'patient has no "gender" field')
			return None
		else:
			tmp = self.__data['gender']
			self.__data['gender'] = xdt_gmgender_map[tmp]

		_log.Log(gmLog.lData, self.__data)

		# all is well, so return true
		return 1
	#--------------------------------------------------------
	# attribute handler
	#--------------------------------------------------------
	def __getitem__(self, item):
		try:
			return self.__data[item]
		except KeyError:
			_log.LogException('[%s] not cached in self.__data', sys.exc_info())

		if item == 'filename':
			return self.filename
		if item == 'all':
			return self.__data

#==============================================================
# main
#--------------------------------------------------------------
if __name__ == "__main__":
	# test framework if run by itself
	_log.SetAllLogLevels(gmLog.lData)
	_log.Log(gmLog.lInfo, __version__)

	patfile = sys.argv[1]
	_log.Log(gmLog.lInfo, "reading patient data from xDT file [%s]" % patfile)

	try:
		aPatient = xdtPatient(anXdtFile = patfile)
	except:
		_log.LogException('Cannot instantiate xDT patient object from [%s]' % patfile, sys.exc_info())
		sys.exit(-1)

	print aPatient['all']

#==============================================================
# $Log: gmXdtObjects.py,v $
# Revision 1.1  2003-02-17 23:33:14  ncq
# - first version
#
