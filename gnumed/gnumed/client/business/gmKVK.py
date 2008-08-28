# -*- coding: latin-1 -*-
"""GNUmed German KVK objects.

These objects handle German patient cards (KVK).

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmKVK.py,v $
# $Id: gmKVK.py,v 1.20 2008-08-28 18:30:28 ncq Exp $
__version__ = "$Revision: 1.20 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os, os.path, fileinput, codecs, time, datetime as pyDT, glob, re as regex, logging


# our modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson
from Gnumed.pycommon import gmExceptions, gmDateTime, gmTools, gmPG2


_log = logging.getLogger('gm.kvk')
_log.info(__version__)

true_egk_fields = [
	'insurance_company',
	'insurance_number',
	'insuree_number',
	'insuree_status',
	'insuree_status_detail',
	'insuree_status_comment',
	'title',
	'firstnames',
	'lastnames',
	'dob',
	'street',
	'zip',
	'urb',
	'valid_since',
]


true_kvk_fields = [
	'insurance_company',
	'insurance_number',
	'insurance_number_vknr',
	'insuree_number',
	'insuree_status',
	'insuree_status_detail',
	'insuree_status_comment',
	'title',
	'firstnames',
	'name_affix',
	'lastnames',
	'dob',
	'street',
	'urb_region_code',
	'zip',
	'urb',
	'valid_until'
]


map_kvkd_tags2dto = {
	'Version': 'libchipcard_version',
	'Datum': 'last_read_date',
	'Zeit': 'last_read_time',
	'Lesertyp': 'reader_type',
	'Kartentyp': 'card_type',
	'KK-Name': 'insurance_company',
	'KK-Nummer': 'insurance_number',
	'KVK-Nummer': 'insurance_number_vknr',
	'VKNR': 'insurance_number_vknr',
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
	'Laendercode': 'urb_region_code',
	'PLZ': 'zip',
	'Ort': 'urb',
	'gueltig-seit': 'valid_since',
	'gueltig-bis': 'valid_until',
	'Pruefsumme-gueltig': 'crc_valid',
	'Kommentar': 'comment'
}

issuer_template = u'%s (%s)'
insurance_number_external_id_type = u'Versichertennummer'
insurance_number_external_id_type_egk = u'Versichertennummer (eGK)'

#============================================================
class cDTO_eGK(gmPerson.cDTO_person):

	kvkd_card_id_string = u'Elektronische Gesundheitskarte'

	def __init__(self, filename=None, strict=True):
		self.dto_type = 'eGK'
		self.dob_format = '%d%m%Y'
		self.valid_since_format = '%d%m%Y'
		self.last_read_time_format = '%H:%M:%S'
		self.last_read_date_format = '%d.%m.%Y'
		self.filename = filename

		self.__parse_egk_file(strict = strict)

		# if we need to interpret KBV requirements by the
		# letter we have to delete the file right here
		#self.delete_from_source()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def get_candidate_identities(self, can_create = False):
		old_idents = gmPerson.cDTO_person.get_candidate_identities(self, can_create = can_create)

		cmd = u"""
select pk_identity from dem.v_external_ids4identity where
	value = %(val)s and
	name = %(name)s and
	issuer = %(kk)s
"""
		args = {
			'val': self.insuree_number,
			'name': insurance_number_external_id_type,
			'kk': issuer_template % (self.insurance_company, self.insurance_number)
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		# weed out duplicates
		new_idents = []
		for r in rows:
			for oid in old_idents:
				if r[0] == oid.ID:
					break
			new_idents.append(gmPerson.cIdentity(aPK_obj = r['pk_identity']))

		old_idents.extend(new_idents)

		return old_idents
	#--------------------------------------------------------
	def import_extra_data(self, identity=None, *args, **kwargs):
		# Versicherungsnummer
		identity.add_external_id (
			id_type = insurance_number_external_id_type_egk,
			id_value = self.insuree_number,
			issuer = issuer_template % (self.insurance_company, self.insurance_number),
			comment = u'Nummer (eGK) des Versicherten bei der Krankenkasse',
			context = u'p'
		)
		# address
		street = self.street
		number = regex.findall(' \d+.*', street)
		if len(number) == 0:
			number = None
		else:
			street = street.replace(number[0], '')
			number = number[0].strip()
		identity.link_address (
			number = number,
			street = street,
			postcode = self.zip,
			urb = self.urb,
			state = u'??',
			country = u'DE'			# actually: map urb_region_code
		)
		# FIXME: eGK itself
	#--------------------------------------------------------
	def delete_from_source(self):
		try:
			os.remove(self.filename)
			self.filename = None
		except:
			_log.exception('cannot delete kvkd file [%s]' % self.filename, verbose = False)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __parse_egk_file(self, strict=True):

		_log.debug('parsing eGK data in [%s]', self.filename)

		egk_file = codecs.open(filename = self.filename, mode = 'rU', encoding = 'utf8')

		card_type_seen = False
		for line in egk_file:
			line = line.replace('\n', '').replace('\r', '')
			tag, content = line.split(':', 1)
			content = content.strip()

			if tag == 'Kartentyp':
				card_type_seen = True
				if content != cDTO_eGK.kvkd_card_id_string:
					_log.error('parsing wrong card type')
					_log.error('found   : %s', content)
					_log.error('expected: %s', cDTO_KVK.kvkd_card_id_string)
				if strict:
					raise ValueError('wrong card type: %s, expected %s', content, cDTO_KVK.kvkd_card_id_string)
				else:
					_log.debug('trying to parse anyway')

			if tag == 'Geburtsdatum':
				tmp = time.strptime(content, self.dob_format)
				content = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

			try:
				setattr(self, map_kvkd_tags2dto[tag], content)
			except KeyError:
				_log.exception('unknown KVKd eGK file key [%s]' % tag)

		# valid_since -> valid_since_timestamp
		ts = time.strptime (
			'%s20%s' % (self.valid_since[:4], self.valid_since[4:]),
			self.valid_since_format
		)

		# last_read_date and last_read_time -> last_read_timestamp
		ts = time.strptime (
			'%s %s' % (self.last_read_date, self.last_read_time),
			'%s %s' % (self.last_read_date_format, self.last_read_time_format)
		)
		self.last_read_timestamp = pyDT.datetime(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec, tzinfo = gmDateTime.gmCurrentLocalTimezone)

		# guess gender from firstname
		self.gender = gmTools.coalesce(gmPerson.map_firstnames2gender(firstnames=self.firstnames), 'f')

		if not card_type_seen:
			_log.warning('no line with card type found, unable to verify')
#============================================================
class cDTO_KVK(gmPerson.cDTO_person):

	kvkd_card_id_string = u'Krankenversichertenkarte'

	def __init__(self, filename=None, strict=True):
		self.dto_type = 'KVK'
		self.dob_format = '%d%m%Y'
		self.valid_until_format = '%d%m%Y'
		self.last_read_time_format = '%H:%M:%S'
		self.last_read_date_format = '%d.%m.%Y'
		self.filename = filename

		self.__parse_kvk_file(strict = strict)

		# if we need to interpret KBV requirements by the
		# letter we have to delete the file right here
		#self.delete_from_source()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def get_candidate_identities(self, can_create = False):
		old_idents = gmPerson.cDTO_person.get_candidate_identities(self, can_create = can_create)

		cmd = u"""
select pk_identity from dem.v_external_ids4identity where
	value = %(val)s and
	name = %(name)s and
	issuer = %(kk)s
"""
		args = {
			'val': self.insuree_number,
			'name': insurance_number_external_id_type,
			'kk': issuer_template % (self.insurance_company, self.insurance_number)
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		# weed out duplicates
		new_idents = []
		for r in rows:
			for oid in old_idents:
				if r[0] == oid.ID:
					break
			new_idents.append(gmPerson.cIdentity(aPK_obj = r['pk_identity']))

		old_idents.extend(new_idents)

		return old_idents
	#--------------------------------------------------------
	def import_extra_data(self, identity=None, *args, **kwargs):
		# Versicherungsnummer
		identity.add_external_id (
			id_type = insurance_number_external_id_type,
			id_value = self.insuree_number,
			issuer = issuer_template % (self.insurance_company, self.insurance_number),
			comment = u'Nummer des Versicherten bei der Krankenkasse',
			context = u'p'
		)
		# address
		street = self.street
		number = regex.findall(' \d+.*', street)
		if len(number) == 0:
			number = None
		else:
			street = street.replace(number[0], '')
			number = number[0].strip()
		identity.link_address (
			number = number,
			street = street,
			postcode = self.zip,
			urb = self.urb,
			state = u'??',
			country = u'DE'		# actually: map urb_region_code
		)
		# FIXME: kvk itself
	#--------------------------------------------------------
	def delete_from_source(self):
		try:
			os.remove(self.filename)
			self.filename = None
		except:
			_log.exception('cannot delete kvkd file [%s]' % self.filename, verbose = False)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __parse_kvk_file(self, strict=True):

		_log.debug('parsing KVK data in [%s]', self.filename)

		kvk_file = codecs.open(filename = self.filename, mode = 'rU', encoding = 'utf8')

		card_type_seen = False
		for line in kvk_file:
			line = line.replace('\n', '').replace('\r', '')
			tag, content = line.split(':', 1)
			content = content.strip()

			if tag == 'Kartentyp':
				card_type_seen = True
				if content != cDTO_KVK.kvkd_card_id_string:
					_log.error('parsing wrong card type')
					_log.error('found   : %s', content)
					_log.error('expected: %s', cDTO_KVK.kvkd_card_id_string)
				if strict:
					raise ValueError('wrong card type: %s, expected %s', content, cDTO_KVK.kvkd_card_id_string)
				else:
					_log.debug('trying to parse anyway')

			if tag == 'Geburtsdatum':
				tmp = time.strptime(content, self.dob_format)
				content = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

			try:
				setattr(self, map_kvkd_tags2dto[tag], content)
			except KeyError:
				_log.exception('unknown KVKd kvk file key [%s]' % tag)

		# valid_until -> valid_until_timestamp
		ts = time.strptime (
			'28%s20%s' % (self.valid_until[:2], self.valid_until[2:]),
			self.valid_until_format
		)

		# last_read_date and last_read_time -> last_read_timestamp
		ts = time.strptime (
			'%s %s' % (self.last_read_date, self.last_read_time),
			'%s %s' % (self.last_read_date_format, self.last_read_time_format)
		)
		self.last_read_timestamp = pyDT.datetime(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec, tzinfo = gmDateTime.gmCurrentLocalTimezone)

		# guess gender from firstname
		self.gender = gmTools.coalesce(gmPerson.map_firstnames2gender(firstnames=self.firstnames), 'f')

		if not card_type_seen:
			_log.warning('no line with card type found, unable to verify')
#============================================================
def detect_card_type(card_file=None):

	data_file = codecs.open(filename = card_file, mode = 'rU', encoding = 'utf8')

	for line in kvk_file:
		line = line.replace('\n', '').replace('\r', '')
		tag, content = line.split(':', 1)
		content = content.strip()

		if tag == 'Kartentyp':
			pass
#============================================================
def get_available_kvks_as_dtos(spool_dir = None):

	kvk_files = glob.glob(os.path.join(spool_dir, 'KVK-*.dat'))
	dtos = []
	for kvk_file in kvk_files:
		try:
			dto = cDTO_KVK(filename = kvk_file)
		except:
			_log.exception('probably not a KVKd KVK file: [%s]' % kvk_file)
			continue
		dtos.append(dto)

	return dtos
#------------------------------------------------------------
def get_available_egks_as_dtos(spool_dir = None):

	egk_files = glob.glob(os.path.join(spool_dir, 'eGK-*.dat'))
	dtos = []
	for egk_file in egk_files:
		try:
			dto = cDTO_eGK(filename = egk_file)
		except:
			_log.exception('probably not a KVKd eGK file: [%s]' % egk_file)
			continue
		dtos.append(dto)

	return dtos
#------------------------------------------------------------
def get_available_cards_as_dtos(spool_dir = None):

	dtos = []
	dtos.extend(get_available_kvks_as_dtos(spool_dir = spool_dir))
	dtos.extend(get_available_egks_as_dtos(spool_dir = spool_dir))

	return dtos
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmDateTime.init()

	def test_egk_dto():
		# test cKVKd_file object
		kvkd_file = sys.argv[2]
		print "reading eGK data from KVKd file", kvkd_file
		dto = cDTO_eGK(filename = kvkd_file, strict = False)
		print dto
		for attr in true_egk_fields:
			print getattr(dto, attr)

	def test_kvk_dto():
		# test cKVKd_file object
		kvkd_file = sys.argv[2]
		print "reading KVK data from KVKd file", kvkd_file
		dto = cDTO_KVK(filename = kvkd_file, strict = False)
		print dto
		for attr in true_kvk_fields:
			print getattr(dto, attr)

	def test_get_available_kvks_as_dto():
		dtos = get_available_kvks_as_dtos(spool_dir = sys.argv[2])
		for dto in dtos:
			print dto

	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		if len(sys.argv) < 3:
			print "give name of KVKd file as first argument"
			sys.exit(-1)
		test_egk_dto()
		#test_kvk_dto()
		#test_get_available_kvks_as_dto()

#============================================================
# docs
#------------------------------------------------------------
#	name       | mandat | type | length | format
#	--------------------------------------------
#	Name Kasse |  x     | str  | 2-28
#	Nr. Kasse  |  x     | int  | 7
#	   VKNR    |        | int  | 5						# MUST be derived from Stammdaten-file, not from KVK
#	Nr. Pat    |  x     | int  | 6-12
#	Status Pat |  x     | str  | 1 or 4
#	Statuserg. |        | str  | 1-3
#	Titel Pat  |        | str  | 3-15
#	Vorname    |        | str  | 2-28
#	Adelspraed.|        | str  | 1-15
#	Nachname   |  x     | str  | 2-28
#	geboren    |  x     | int  | 8      | DDMMYYYY
#	Straße     |        | str  | 1-28
#	Ländercode |        | str  | 1-3
#	PLZ        |  x     | int  | 4-7
#	Ort        |  x     | str  | 2-23
#	gültig bis |        | int  | 4      | MMYY

#============================================================
# $Log: gmKVK.py,v $
# Revision 1.20  2008-08-28 18:30:28  ncq
# - region_code -> urb_region_code
# - support eGK now that libchipcard can read it :-)
# - improved testing
#
# Revision 1.19  2008/02/25 17:31:41  ncq
# - logging cleanup
#
# Revision 1.18  2008/01/30 13:34:50  ncq
# - switch to std lib logging
#
# Revision 1.17  2007/12/26 12:35:30  ncq
# - import_extra_data(..., *args, **kwargs)
#
# Revision 1.16  2007/11/12 22:54:26  ncq
# - fix longstanding semantic bug ! KVK-Nummmer really is VKNR
# - delete KVKd file after importing it
# - improve get_candidate_identities()
# - improve import_extra_data()
# - implement delete_from_source()
# - cleanup, improve docs
#
# Revision 1.15  2007/11/02 10:55:37  ncq
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
