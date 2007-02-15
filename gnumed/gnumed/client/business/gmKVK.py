# -*- coding: latin-1 -*-
"""GNUmed German KVK objects.

These objects handle German patient cards (KVK).

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmKVK.py,v $
# $Id: gmKVK.py,v 1.10 2007-02-15 14:54:47 ncq Exp $
__version__ = "$Revision: 1.10 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, fileinput, codecs, time, datetime as pyDT, glob

# our modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.business import gmPerson
from Gnumed.pycommon import gmLog, gmExceptions, gmDateTime, gmTools

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


true_kvk_fields = [
	'insurance_company',
	'insurance_number',
	'kvk_number',
	'insuree_number',
	'insuree_status',
	'insuree_status_detail',
	'title',
	'firstnames',
	'name_affix',
	'lastnames',
	'dob',
	'street',
	'region_code',
	'zip',
	'urb',
	'valid_until'
]


map_kvkd_tags2dto = {
	'Version': 'version',
	'Datum': 'last_read_date',
	'Zeit': 'last_read_time',
	'KK-Name': 'insurance_company',
	'KK-Nummer': 'insurance_number',
	'KVK-Nummer': 'kvk_number',
	'V-Nummer': 'insuree_number',
	'V-Status': 'insuree_status',
	'V-Statusergaenzung': 'insuree_status_detail',
	'Titel': 'title',
	'Vorname': 'firstnames',
	'Namenszusatz': 'name_affix',
	'Familienname': 'lastnames',
	'Geburtsdatum': 'dob',
	'Strasse': 'street',
	'Laendercode': 'region_code',
	'PLZ': 'zip',
	'Ort': 'urb',
	'gueltig-bis': 'valid_until',
	'Pruefsumme-gueltig': 'crc_valid',
	'Kommentar': 'comment'
}

#============================================================
class cDTO_KVK(gmPerson.cDTO_person):

	def __init__(self, filename=None):
		self.dto_type = 'KVK'
		self.dob_format = '%d%m%Y'
		self.last_read_time_format = '%H:%M:%S'
		self.last_read_date_format = '%d.%m.%Y'
		self.filename = filename
		self.parse_kvk_file()
	#--------------------------------------------------------
	def parse_kvk_file(self):

		kvk_file = codecs.open(filename = self.filename, mode = 'rU', encoding = 'utf8')

		for line in kvk_file:
			line = line.replace('\n', '').replace('\r', '')
			tag, content = line.split(':', 1)
			content = content.strip()

			if tag == 'Geburtsdatum':
				tmp = time.strptime(content, self.dob_format)
				content = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

			setattr(self, map_kvkd_tags2dto[tag], content)

		# last_read_date and last_read_time -> last_read_timestamp
		ts = time.strptime (
			'%s %s' % (self.last_read_date, self.last_read_time),
			'%s %s' % (self.last_read_date_format, self.last_read_time_format)
		)
		self.last_read_timestamp = pyDT.datetime(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec, tzinfo = gmDateTime.gmCurrentLocalTimezone)

		# guess gender from firstname
		self.gender = gmTools.coalesce(gmPerson.map_firstnames2gender(firstnames=self.firstnames), 'f')
#============================================================
class cKVK_data:
	"""Abstract KVK data class.

	"""
	#--------------------------------------------------------
	def __init__(self):
		for field in true_kvk_fields:
			self.__dict__[field] = None
	#--------------------------------------------------------
	def __setitem__(self, key, value):
		# this will kick us out on KeyError
		tmp = self.__dict__[key]
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
		self.filename = os.path.abspath(os.path.expanduser(aFile))

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
def get_available_kvks_as_dtos(spool_dir = None):

	kvk_files = glob.glob(os.path.join(spool_dir, 'KVK-*.dat'))
	dtos = []
	for kvk_file in kvk_files:
		try:
			dto = cDTO_KVK(filename = kvk_file)
		except:
			_log.LogException('probably not a KVKd file: [%s]' % kvk_file)
			continue
		dtos.append(dto)

	return dtos
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
		# FIXME: use glob.glob()
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
			lname = "%s" % u' '.join([ kvk['title'], kvk['name_affix'],  kvk['lname'] ])
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
	dto = cDTO_KVK(filename = kvkd_file)
	print dto
#	tmp = cKVKd_file(aFile = kvkd_file)

	# test get_available_kvks()
#	path = os.path.dirname(kvkd_file)
#	kvks = get_available_kvks(aDir = path)
#	print kvks
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
# Revision 1.10  2007-02-15 14:54:47  ncq
# - fix test suite
# - true_kvk_fields list
# - map_kvkd_tags2dto
# - cDTO_KVK()
# - get_available_kvks_as_dtos()
#
# Revision 1.9  2006/01/01 20:37:22  ncq
# - cleanup
#
# Revision 1.8  2005/11/01 08:49:49  ncq
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
