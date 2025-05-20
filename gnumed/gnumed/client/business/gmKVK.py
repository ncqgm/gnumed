# -*- coding: utf-8 -*-
"""GNUmed German KVK/eGK objects.

These objects handle German patient cards (KVK and eGK).

KVK: http://www.kbv.de/ita/register_G.html
eGK: http://www.gematik.de/upload/gematik_Qop_eGK_Spezifikation_Teil1_V1_1_0_Kommentare_4_1652.pdf
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import os
import os.path
import time
import glob
import datetime as pyDT
import re as regex
import json
import logging


# our modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.business import gmPerson
from Gnumed.business import gmGender


_log = logging.getLogger('gm.kvk')

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


map_CCRdr_gender2gm = {
	'M': 'm',
	'W': 'f',
	'U': None,
	'D': 'h'
}


map_CCRdr_region_code2country = {
	'D': 'DE'
}


EXTERNAL_ID_ISSUER_TEMPLATE = '%s (%s)'
EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER = 'Versichertennummer'
EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER_EGK = 'Versichertennummer (eGK)'

#============================================================
class cDTO_CCRdr(gmPerson.cDTO_person):

	def __init__(self, filename=None, strict=True):

		gmPerson.cDTO_person.__init__(self)

		self.filename = filename
		self.date_format = '%Y%m%d'
		self.valid_since = None
		self.valid_until = None
		self.card_is_rejected = False
		self.card_is_expired = False

		self.__load_vk_file()

		# if we need to interpret KBV requirements by the
		# letter we have to delete the file right here
		#self.delete_from_source()

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def get_candidate_identities(self, can_create = False):
		old_idents = gmPerson.cDTO_person.get_candidate_identities(self, can_create = can_create)

		# look for candidates based on their Insuree Number
		if not self.card_is_rejected:
			cmd = """
				SELECT pk_identity FROM dem.v_external_ids4identity WHERE
					value = %(val)s AND
					name = %(name)s AND
					issuer = %(kk)s
				"""
			args = {
				'val': self.insuree_number,
				'name': '%s (%s)' % (
					EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER,
					self.raw_data['Karte']
				),
				'kk': EXTERNAL_ID_ISSUER_TEMPLATE % (self.raw_data['KostentraegerName'], self.raw_data['Kostentraegerkennung'])
			}
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

			# weed out duplicates
			name_candidate_ids = [ o.ID for o in old_idents ]
			for r in rows:
				if r[0] not in name_candidate_ids:
					old_idents.append(gmPerson.cPerson(aPK_obj = r[0]))

		return old_idents

	#--------------------------------------------------------
	def delete_from_source(self):
#		try:
#			os.remove(self.filename)
#			self.filename = None
#		except Exception:
#			_log.exception('cannot delete CCReader file [%s]' % self.filename, verbose = False)
		pass	# for now

	#--------------------------------------------------------
	def import_extra_data(self, identity=None, *args, **kwargs):
		if not self.card_is_rejected:
			args = {
				'pat': identity.ID,
				'dob': self.preformatted_dob,
				'valid_until': self.valid_until,
				'data': self.raw_data
			}
			cmd = """
				INSERT INTO de_de.insurance_card (
					fk_identity,
					formatted_dob,
					valid_until,
					raw_data
				) VALUES (
					%(pat)s,
					%(dob)s,
					%(valid_until)s,
					%(data)s
				)"""
			gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __load_vk_file(self):

		_log.debug('loading eGK/KVK/PKVK data from [%s]', self.filename)
		vk_file = open(self.filename, mode = 'rt', encoding = 'utf-8-sig')
		self.raw_data = json.load(vk_file)
		vk_file.close()

		if self.raw_data['Fehlerbericht']['FehlerNr'] != '0x9000':
			_log.error('error [%s] reading VK: %s', self.raw_data['Fehlerbericht']['FehlerNr'], self.raw_data['Fehlerbericht']['Fehlermeldung'])
			raise ValueError('error [%s] reading VK: %s' % (self.raw_data['Fehlerbericht']['FehlerNr'], self.raw_data['Fehlerbericht']['Fehlermeldung']))

		# rejection
		if self.raw_data['Ablehnen'] == 'ja':
			self.card_is_rejected = True
			_log.info('eGK may contain insurance information but KBV says it must be rejected because it is of generation 0')

		# validity
		# - since
		tmp = time.strptime(self.raw_data['VersicherungsschutzBeginn'], self.date_format)
		self.valid_since = pyDT.date(tmp.tm_year, tmp.tm_mon, tmp.tm_mday)
		# - until
		tmp = time.strptime(self.raw_data['VersicherungsschutzEnde'], self.date_format)
		self.valid_until = pyDT.date(tmp.tm_year, tmp.tm_mon, tmp.tm_mday)
		if self.valid_until < pyDT.date.today():
			self.card_is_expired = True

		# DTO source
		src_attrs = []
		if self.card_is_expired:
			src_attrs.append(_('expired'))
		if self.card_is_rejected:
			_log.info('eGK contains insurance information but KBV says it must be rejected because it is of generation 0')
			src_attrs.append(_('rejected'))
		src_attrs.append('CCReader')
		self.source = '%s (%s)' % (
			self.raw_data['Karte'],
			', '.join(src_attrs)
		)

		# name / gender
		self.firstnames = self.raw_data['Vorname']
		self.lastnames = self.raw_data['Nachname']
		self.gender = map_CCRdr_gender2gm[self.raw_data['Geschlecht']]

		# title
		title_parts = []
		for part in ['Titel', 'Namenszusatz', 'Vorsatzwort']:
			tmp = self.raw_data[part].strip()
			if tmp == '':
				continue
			title_parts.append(tmp)
		if len(title_parts) > 0:
			self.title = ' '.join(title_parts)

		# dob
		dob_str = self.raw_data['Geburtsdatum']
		year_str = dob_str[:4]
		month_str = dob_str[4:6]
		day_str = dob_str[6:8]
		self.preformatted_dob = '%s.%s.%s' % (day_str, month_str, year_str)	# pre-format for printing including "0"-parts
		if year_str == '0000':
			self.dob = None			# redundant but explicit is good
		else:
			if day_str == '00':
				self.dob_is_estimated = True
				day_str = '01'
			if month_str == '00':
				self.dob_is_estimated = True
				month_str = '01'
			dob_str = year_str + month_str + day_str
			tmp = time.strptime(dob_str, self.date_format)
			self.dob = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, 11, 11, 11, 111, tzinfo = gmDateTime.gmCurrentLocalTimezone)

		# addresses
		# - street
		try:
			adr = self.raw_data['StrassenAdresse']
			try:
				self.remember_address (
					adr_type = 'eGK (Wohnadresse)',
					number = adr['Hausnummer'],
					subunit = adr['Anschriftenzusatz'],
					street = adr['Strasse'],
					urb = adr['Ort'],
					region_code = '',
					zip = adr['Postleitzahl'],
					country_code = map_CCRdr_region_code2country[adr['Wohnsitzlaendercode']]
				)
			except ValueError:
				_log.exception('invalid street address on card')
			except KeyError:
				_log.error('unknown country code [%s] on card in street address', adr['Wohnsitzlaendercode'])
		except KeyError:
			_log.warning('no street address on card')
		# PO Box
		try:
			adr = self.raw_data['PostfachAdresse']
			try:
				self.remember_address (
					adr_type = 'eGK (Postfach)',
					number = adr['Postfach'],
					#subunit = adr['Anschriftenzusatz'],
					street = _('PO Box'),
					urb = adr['PostfachOrt'],
					region_code = '',
					zip = adr['PostfachPLZ'],
					country_code = map_CCRdr_region_code2country[adr['PostfachWohnsitzlaendercode']]
				)
			except ValueError:
				_log.exception('invalid PO Box address on card')
			except KeyError:
				_log.error('unknown country code [%s] on card in PO Box address', adr['Wohnsitzlaendercode'])
		except KeyError:
			_log.warning('no PO Box address on card')

		if not (self.card_is_expired or self.card_is_rejected):
			self.insuree_number = None
			try:
				self.insuree_number = self.raw_data['Versicherten_ID']
			except KeyError:
				pass
			try:
				self.insuree_number = self.raw_data['Versicherten_ID_KVK']
			except KeyError:
				pass
			try:
				self.insuree_number = self.raw_data['Versicherten_ID_PKV']
			except KeyError:
				pass
			if self.insuree_number is not None:
				try:
					self.remember_external_id (
						name = '%s (%s)' % (
							EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER,
							self.raw_data['Karte']
						),
						value = self.insuree_number,
						issuer = EXTERNAL_ID_ISSUER_TEMPLATE % (self.raw_data['KostentraegerName'], self.raw_data['Kostentraegerkennung']),
						comment = 'Nummer (eGK) des Versicherten bei der Krankenkasse, gültig: %s - %s' % (
							gmDateTime.pydt_strftime(self.valid_since, '%Y %b %d', none_str = '?'),
							gmDateTime.pydt_strftime(self.valid_until, '%Y %b %d', none_str = '?')
						)
					)
				except KeyError:
					_log.exception('no insurance information on eGK')

#============================================================
class cDTO_eGK(gmPerson.cDTO_person):

	kvkd_card_id_string = 'Elektronische Gesundheitskarte'

	def __init__(self, filename=None, strict=True):
		self.card_type = 'eGK'
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

		cmd = """
select pk_identity from dem.v_external_ids4identity where
	value = %(val)s and
	name = %(name)s and
	issuer = %(kk)s
"""
		args = {
			'val': self.insuree_number,
			'name': EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER,
			'kk': EXTERNAL_ID_ISSUER_TEMPLATE % (self.insurance_company, self.insurance_number)
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		# weed out duplicates
		new_idents = []
		for r in rows:
			for oid in old_idents:
				if r[0] == oid.ID:
					break
			new_idents.append(gmPerson.cPerson(aPK_obj = r['pk_identity']))

		old_idents.extend(new_idents)

		return old_idents
	#--------------------------------------------------------
	def import_extra_data(self, identity=None, *args, **kwargs):
		# FIXME: rather use remember_external_id()

		# Versicherungsnummer
		identity.add_external_id (
			type_name = EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER_EGK,
			value = self.insuree_number,
			issuer = EXTERNAL_ID_ISSUER_TEMPLATE % (self.insurance_company, self.insurance_number),
			comment = 'Nummer (eGK) des Versicherten bei der Krankenkasse'
		)
		# address
		street = self.street
		number = regex.findall(r' \d+.*', street)
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
			region_code = '',			# actually: map urb2region ?
			country_code = 'DE'		# actually: map urb+region2country_code
		)
		# FIXME: eGK itself
	#--------------------------------------------------------
	def delete_from_source(self):
		try:
			os.remove(self.filename)
			self.filename = None
		except Exception:
			_log.exception('cannot delete kvkd file [%s]' % self.filename, verbose = False)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __parse_egk_file(self, strict=True):

		_log.debug('parsing eGK data in [%s]', self.filename)

		egk_file = open(self.filename, mode = 'rt', encoding = 'utf-8-sig')

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
		self.gender = gmTools.coalesce(gmGender.map_firstnames2gender(firstnames=self.firstnames), 'f')

		if not card_type_seen:
			_log.warning('no line with card type found, unable to verify')

#============================================================
class cDTO_KVK(gmPerson.cDTO_person):

	kvkd_card_id_string = 'Krankenversichertenkarte'

	def __init__(self, filename=None, strict=True):
		self.card_type = 'KVK'
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

		cmd = """
select pk_identity from dem.v_external_ids4identity where
	value = %(val)s and
	name = %(name)s and
	issuer = %(kk)s
"""
		args = {
			'val': self.insuree_number,
			'name': EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER,
			'kk': EXTERNAL_ID_ISSUER_TEMPLATE % (self.insurance_company, self.insurance_number)
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		# weed out duplicates
		new_idents = []
		for r in rows:
			for oid in old_idents:
				if r[0] == oid.ID:
					break
			new_idents.append(gmPerson.cPerson(aPK_obj = r['pk_identity']))

		old_idents.extend(new_idents)

		return old_idents
	#--------------------------------------------------------
	def import_extra_data(self, identity=None, *args, **kwargs):
		# Versicherungsnummer
		identity.add_external_id (
			type_name = EXTERNAL_ID_TYPE_VK_INSUREE_NUMBER,
			value = self.insuree_number,
			issuer = EXTERNAL_ID_ISSUER_TEMPLATE % (self.insurance_company, self.insurance_number),
			comment = 'Nummer des Versicherten bei der Krankenkasse'
		)
		# address
		street = self.street
		number = regex.findall(r' \d+.*', street)
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
			region_code = '',
			country_code = 'DE'		# actually: map urb_region_code
		)
		# FIXME: kvk itself
	#--------------------------------------------------------
	def delete_from_source(self):
		try:
			os.remove(self.filename)
			self.filename = None
		except Exception:
			_log.exception('cannot delete kvkd file [%s]' % self.filename, verbose = False)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __parse_kvk_file(self, strict=True):

		_log.debug('parsing KVK data in [%s]', self.filename)

		kvk_file = open(self.filename, mode = 'rt', encoding = 'utf-8-sig')

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
		self.gender = gmTools.coalesce(gmGender.map_firstnames2gender(firstnames=self.firstnames), 'f')

		if not card_type_seen:
			_log.warning('no line with card type found, unable to verify')
#============================================================
def detect_card_type(card_file=None):

	kvk_file = open(card_file, mode = 'rt', encoding = 'utf-8-sig')
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
		except Exception:
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
		except Exception:
			_log.exception('probably not a KVKd eGK file: [%s]' % egk_file)
			continue
		dtos.append(dto)

	return dtos
#------------------------------------------------------------
def get_available_CCRdr_files_as_dtos(spool_dir = None):

	ccrdr_files = glob.glob(os.path.join(spool_dir, 'CCReader-*.dat'))
	dtos = []
	for ccrdr_file in ccrdr_files:
		try:
			dto = cDTO_CCRdr(filename = ccrdr_file)
		except Exception:
			_log.exception('probably not a CCReader file: [%s]' % ccrdr_file)
			continue
		dtos.append(dto)

	return dtos
#------------------------------------------------------------
def get_available_cards_as_dtos(spool_dir = None):
	dtos = []
#	dtos.extend(get_available_CCRdr_files_as_dtos(spool_dir = spool_dir))
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

	def test_vks():
		dtos = get_available_CCRdr_files_as_dtos(spool_dir = sys.argv[2])
		for dto in dtos:
			print(dto)

	def test_egk_dto():
		# test cKVKd_file object
		kvkd_file = sys.argv[2]
		print("reading eGK data from KVKd file", kvkd_file)
		dto = cDTO_eGK(filename = kvkd_file, strict = False)
		print(dto)
		for attr in true_egk_fields:
			print(getattr(dto, attr))

	def test_kvk_dto():
		# test cKVKd_file object
		kvkd_file = sys.argv[2]
		print("reading KVK data from KVKd file", kvkd_file)
		dto = cDTO_KVK(filename = kvkd_file, strict = False)
		print(dto)
		for attr in true_kvk_fields:
			print(getattr(dto, attr))

	def test_get_available_kvks_as_dto():
		dtos = get_available_kvks_as_dtos(spool_dir = sys.argv[2])
		for dto in dtos:
			print(dto)

	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		if len(sys.argv) < 3:
			print("give name of KVKd file as first argument")
			sys.exit(-1)
		test_vks()
		#test_egk_dto()
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
