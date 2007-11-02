# -*- coding: latin-1 -*-
"""GNUmed German KVK objects.

These objects handle German patient cards (KVK).

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmKVK.py,v $
# $Id: gmKVK.py,v 1.15 2007-11-02 10:55:37 ncq Exp $
__version__ = "$Revision: 1.15 $"
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
	'Version': 'libchipcard_version',
	'Datum': 'last_read_date',
	'Zeit': 'last_read_time',
	'Lesertyp': 'reader_type',
	'KK-Name': 'insurance_company',
	'KK-Nummer': 'insurance_number',
	'KVK-Nummer': 'kvk_number',
	'V-Nummer': 'insuree_number',
	'V-Status': 'insuree_status',
	'V-Statusergaenzung': 'insuree_status_detail',
	'V-Status-Erlaeuterung': 'insuree_status_comment',
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
		self.__find_me_sql = None

		self.__parse_kvk_file()
	#--------------------------------------------------------
	def _get_find_me_sql(self):
		return u''

	find_me_sql = property(_get_find_me_sql, lambda x:x)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __parse_kvk_file(self):

		kvk_file = codecs.open(filename = self.filename, mode = 'rU', encoding = 'utf8')

		for line in kvk_file:
			line = line.replace('\n', '').replace('\r', '')
			tag, content = line.split(':', 1)
			content = content.strip()

			if tag == 'Geburtsdatum':
				tmp = time.strptime(content, self.dob_format)
				content = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

			try:
				setattr(self, map_kvkd_tags2dto[tag], content)
			except KeyError:
				_log.LogException('unknown KVKd file key [%s]' % tag)

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
					self.kvk[self.map_kvkd_tags2dto[name]] = content
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
# main
#------------------------------------------------------------
if __name__ == "__main__":

	def test_kvk_dto():
		# test cKVKd_file object
		kvkd_file = sys.argv[2]
		print "reading KVK data from KVKd file", kvkd_file
		dto = cDTO_KVK(filename = kvkd_file)
		print dto

	def test_get_available_kvks_as_dto():
		dtos = get_available_kvks_as_dtos(spool_dir = sys.argv[2])
		for dto in dtos:
			print dto

	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		if len(sys.argv) < 3:
			print "give name of KVKd file as first argument"
			sys.exit(-1)

		#test_kvk_dto()
		#tmp = cKVKd_file(aFile = kvkd_file)
		test_get_available_kvks_as_dto()

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
# Revision 1.15  2007-11-02 10:55:37  ncq
# - syntax error fix
#
# Revision 1.14  2007/10/31 22:06:17  ncq
# - teach about more fields in file
# - start find_me_sql property
#
# Revision 1.13  2007/10/31 11:27:02  ncq
# - fix it again
# - test suite
#
# Revision 1.12  2007/05/11 14:10:19  ncq
# - latin1 -> utf8
#
# Revision 1.11  2007/02/17 13:55:26  ncq
# - consolidate, remove bitrot
#
# Revision 1.10  2007/02/15 14:54:47  ncq
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
