"""GnuMed German XDT parsing objects.

This encapsulates some of the XDT data into
objects for easy access.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXdtObjects.py,v $
# $Id: gmXdtObjects.py,v 1.3 2003-04-19 22:56:03 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert"
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
class xdtPatient:
	"""Handle patient demographics in xDT files.

	- these files are used for inter-application communication in Germany
	"""
	_map_id2name = {
		'3101': 'last name',
		'3102': 'first name',
		'3103': 'dob',
		'3110': 'gender'
	}
	_wanted_fields = (
		'3101',
		'3102',
		'3103',
		'3110'
	)

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
		# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
		for line in fileinput.input(self.filename):
			# found all data already ?
			if fields_found == len(xdtPatient._wanted_fields):
				# yep - close input
				fileinput.close()
				# leave loop
				break

			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','')

			# do we care about this line ?
			field = line[3:7]
			if field in xdtPatient._wanted_fields:
				field_name = xdtPatient._map_id2name[field]
				self.__data[field_name] = line[7:]
				#_log.Log(gmLog.lData, "found item [%s]: %s" % (field_name, self.__data[field_name]))
				fields_found = fields_found + 1

		# cleanup
		fileinput.close()

		# found all data ?
		if fields_found != len(xdtPatient._wanted_fields):
			_log.Log(gmLog.lErr, "did not find sufficient patient data in XDT file [%s]" % self.filename)
			_log.Log(gmLog.lErr, "found only %s items:" % fields_found)
			_log.Log(gmLog.lErr, self.__data)
			return None

		# now normalize what we got
		if not self.__data.has_key('dob'):
			_log.Log(gmLog.lErr, 'patient has no "date of birth" field')
			return None
		else:
			self.__data['dob day'] = self.__data['dob'][:2]
			self.__data['dob month'] = self.__data['dob'][2:4]
			self.__data['dob year'] = self.__data['dob'][4:]

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

		if item == 'filename':
			return self.filename
		if item == 'all':
			return self.__data

		try:
			return self.__data[item]
		except KeyError:
			_log.LogException('[%s] not cached in self.__data', sys.exc_info())
			return None

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
# Revision 1.3  2003-04-19 22:56:03  ncq
# - speed up __load_data(), better encapsulate xdt file maps
#
# Revision 1.2  2003/02/18 02:43:16  ncq
# - rearranged __getitem__ to check self.__data last
#
# Revision 1.1  2003/02/17 23:33:14  ncq
# - first version
#
