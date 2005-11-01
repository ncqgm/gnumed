# -*- coding: latin-1 -*-
"""GNUmed German KVK objects.

These objects handle German patient cards (KVK).

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmKVK.py,v $
# $Id: gmKVK.py,v 1.8 2005-11-01 08:49:49 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, fileinput, re, string

# our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'pycommon'))

from Gnumed.pycommon import gmLog, gmExceptions

_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

#============================================================
class cKVK_data:
	"""Abstract KVK data class.

	"""
	_lst_KVK_fields = [
		'kk_name',
		'kk_number',
		'kvk_number',
		'v_number',
		'v_status',
		'v_status_aux',
		'title',
		'fname',
		'name_affix',
		'lname',
		'dob',
		'street',
		'state_code',
		'zip_code',
		'town',
		'valid_until'
	]
	#--------------------------------------------------------
	def __init__(self):
		for field in self._lst_KVK_fields:
			self.__dict__[field] = None
	#--------------------------------------------------------
	def __setitem__(self, key, value):
		# this will kick us out on KeyError
		try:
			tmp = self.__dict__[key]
		except KeyError:
			_log.LogException('invalid KVK field', sys.exc_info())
			raise

		self.__dict__[key] = value
	#--------------------------------------------------------
	def __getitem__(self, key):
		return self.__dict__[key]
#============================================================
class cKVKd_file:
	"""KVKd file handler.

	Encapsulates logic around libchipcard kvkd files.
	"""
	_map_kvkd_cKVK = {
		'KK-Name': 'kk_name',
		'KK-Nummer': 'kk_number',
		'KVK-Nummer': 'kvk_number',
		'V-Nummer': 'v_number',
		'V-Status': 'v_status',
		'V-Statusergaenzung': 'v_status_aux',
		'Titel': 'title',
		'Vorname': 'fname',
		'Namenszusatz': 'name_affix',
		'Familienname': 'lname',
		'Geburtsdatum': 'dob',
		'Strasse': 'street',
		'Laendercode': 'state_code',
		'PLZ': 'zip_code',
		'Ort': 'town',
		'gueltig-bis': 'valid_until'
	}
	#--------------------------------------------------------
	_lst_kvkd_file_fields = [
		'Version',
		'Datum',
		'Zeit',
		'Pruefsumme-gueltig',
		'Kommentar'
	]
	#--------------------------------------------------------
	def __init__(self, aFile = None):
		if aFile is None:
			raise gmExceptions.ConstructorError, "need file name to read KVK data from kvkd"

		self.filename = os.path.abspath(os.path.expanduser(aFile))
		if not os.path.exists(self.filename):
			raise gmExceptions.ConstructorError, "kvkd file [%s] does not exist" % self.filename

		if not self.__parse_file():
			raise gmExceptions.ConstructorError, "cannot parse kvkd file [%s]" % self.filename

		if not self.__verify_data():
			raise gmExceptions.ConstructorError, "cannot verify data in kvkd file [%s]" % self.filename

		return None
	#--------------------------------------------------------
	def __parse_file(self):
		self.kvk = cKVK_data()
		try:
			for line in fileinput.input(self.filename):
				tmp = line.replace('\012', '')
				tmp = tmp.replace('\015', '')
				name, content = tmp.split(':', 1)
				# now, either it's a true KVK field
				try:
					self.kvk[self._map_kvkd_cKVK[name]] = content
				# or an auxiliary field from libchipcard's kvkd :-)
				except KeyError:
					# or maybe not, after all ?
					if not name in self._lst_kvkd_file_fields:
						raise KeyError, "invalid self.__dict__ key [%s]" % name
					self.__dict__[name] = content

			fileinput.close()
		except StandardError:
			_log.LogException('cannot access or parse kvkd file [%s]' % self.filename, sys.exc_info())
			fileinput.close()
			return None

		return 1
	#--------------------------------------------------------
	def __verify_data(self):
		# "be generous in what you accept and strict on what you emit"
		return 1
	#--------------------------------------------------------
	#--------------------------------------------------------
	def __getitem__(self, key):
		try:
			return self.kvk[key]
		except KeyError:
			if not self.__dict__.has_key(key):
				raise KeyError, "invalid self.__dict__ key [%s]" % key
			else:
				return self.__dict__[key]
	#--------------------------------------------------------
	# public methods
	#--------------------------------------------------------
	def delete_file(self):
		"""Remove the underlying file.

		Yes, this is needed. It is a requirement by the KBV.
		"""
		try:
			os.remove(self.filename)
		except StandardError:
			_log.LogException('cannot remove kvkd file [%s]' % self.filename, sys.exc_info())
			return None
		return 1
#============================================================
def get_available_kvks (aDir = None):
	# sanity checks
	if aDir is None:
		_log.Log(gmLog.lErr, 'must specify kvkd repository directory')
		return None

	basedir = os.path.abspath(os.path.expanduser(aDir))
	if not os.path.exists(basedir):
		_log.Log(gmLog.lErr, 'kvkd repository directory [%s] is not valid' % basedir)
		return None

	# filter out our files
	files = os.listdir(basedir)
	kvk_files = []
	for file in files:
		if re.match('^KVK-\d+\.dat$', file):
			kvk_files.append(os.path.join(basedir, file))

	# and set up list of objects
	kvks = []
	for file in kvk_files:
		try:
			kvk = cKVKd_file(file)
			kvks.append(kvk)
		except:
			_log.LogException('[%s] probably not a KVKd file' % file, sys.exc_info())

	return kvks
#------------------------------------------------------------
def kvks_extract_picklist(aList = None):
	# sanity checks
	if aList is None:
		_log.Log(gmLog.lErr, 'must specify kvk object list')
		return ([], [])

	# extract data list
	data = []
	idx = 0
	for kvk in aList:
		try:
			item = []
			item.append(idx)
			idx += 1
			item.append(kvk['Datum'])
			item.append(kvk['Zeit'])
			lname = "%s" % string.join([ kvk['title'], kvk['name_affix'],  kvk['lname'] ], ' ')
			item.append(lname)
			item.append(kvk['fname'])
			item.append(kvk['dob'])
			item.append(kvk['town'])
			item.append(kvk['street'])
			item.append("%11s" % kvk['kk_name'])
			# FIXME: make display of valid_until smarter !
			valid = kvk['valid_until']
			item.append(valid)
			item.append(kvk['filename'])
		except KeyError:
			_log.LogException('error extracting pick list from KVKd file object, obtained: %s' % item, sys.exc_info())
			# skip that one
			continue
		data.append(item)

	# set up column order for pick list
	col_order = [
		{'label': _('last name'),		'field name': 3},
		{'label': _('first name'),		'field name': 4},
		{'label': _('dob'),				'field name': 5},
		{'label': _('town'),			'field name': 6},
		{'label': _('street'),			'field name': 7},
		{'label': _('insurance company'), 'field name': 8},
		{'label': _('valid until'),		'field name': 9}
	]
	return data, col_order
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "give name of KVKd file as first argument"
		sys.exit(-1)

	# test cKVKd_file object
	kvkd_file = sys.argv[1]
	print "reading KVK data from KVKd file", kvkd_file
	tmp = cKVKd_file(aFile = kvkd_file)

	# test get_available_kvks()
	path = os.path.dirname(kvkd_file)
	kvks = get_available_kvks(aDir = path)
	print kvks
#============================================================
# docs
#------------------------------------------------------------
#	name       | mandat | type | length | format
#	--------------------------------------------
#	Name Kasse |  x     | str  | 2-28
#	Nr. Kasse  |  x     | int  | 7
#	Nr. KVK    |        | int  | 5
#	Nr. Pat    |  x     | int  | 6-12
#	Status Pat |  x     | str  | 1 or 4
#	Statuserg. |        | str  | 1-3
#	Titel Pat  |        | str  | 3-15
#	Vorname    |        | str  | 2-28
#	Adelspräd. |        | str  | 1-15
#	Nachname   |  x     | str  | 2-28
#	geboren    |  x     | int  | 8      | DDMMYYYY
#	Straße     |        | str  | 1-28
#	Ländercode |        | str  | 1-3
#	PLZ        |  x     | int  | 4-7
#	Ort        |  x     | str  | 2-23
#	gültig bis |        | int  | 4      | MMYY

#============================================================
# $Log: gmKVK.py,v $
# Revision 1.8  2005-11-01 08:49:49  ncq
# - naming fix
#
# Revision 1.7  2005/03/06 14:48:23  ncq
# - patient pick list now works with 'field name' not 'data idx'
#
# Revision 1.6  2004/03/04 19:46:53  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.5  2004/03/02 10:21:10  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.4  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.3  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.2  2003/04/19 22:53:46  ncq
# - missing parameter for %s
#
# Revision 1.1  2003/04/09 16:15:24  ncq
# - KVK classes and helpers
#
