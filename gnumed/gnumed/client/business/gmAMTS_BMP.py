# -*- coding: utf-8 -*-
"""Manage German AMTS BMP data."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2"

# std lib
import sys
import os
import logging
import decimal
import datetime as pyDT
#from xml.etree import ElementTree as py_etree
import typing


# 3rd party
#lxml_etree = None
import lxml.etree as lxml_etree


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
	from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPerson


AMTS_BMP_ENCODING = 'latin1'
AMTS_BMP_DOB_FORMAT = '%Y%m%d'
AMTS_BMP_DOB_FORMAT_NO_DAY = '%Y%m'
AMTS_BMP_DOB_FORMAT_YEAR_ONLY = '%Y'
AMTS2GMD_GENDER_MAP = {
	'W': 'f',
	'M': 'm',
	'D': 'h',
	'X': None
}

# the attribute
#
#			<xs:attribute name="p" use="prohibited">
#				<xs:annotation>
#					<xs:documentation>Name: Patchnummer 
#
# Beschreibung: Patchnummer des zugrunde liegenden BMP (zusätzlich zum Attribut Version)
# </xs:documentation>
#				</xs:annotation>
#			</xs:attribute>
#
# needs to be removed from the XSDs or else lxml will
# choke on the <use="prohibited"> part
AMTS_BMP_XSDs = {
	'2.5': 'bmp_V2.5.xsd',
	'2.4.1': 'bmp_V2.4.1.xsd',
	'2.3': 'bmp023.xsd'
}


_log = logging.getLogger('AMTS_BMP')

#============================================================
class cDTO_AmtsBmp(gmPerson.cDTO_person):

	def __init__(self):
		super().__init__()
		self.dob_formats = [
			AMTS_BMP_DOB_FORMAT,
			AMTS_BMP_DOB_FORMAT_NO_DAY,
			AMTS_BMP_DOB_FORMAT_YEAR_ONLY
		]
		self.dob_tz = gmDateTime.pydt_now_here().tzinfo
		self.gender_map = AMTS2GMD_GENDER_MAP

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _get_unambiguous_identity(self) -> typing.Union[None, gmPerson.cPerson]:
		egk_tag = 'eGK'
		egk_issuer = 'Krankenkasse'
		egk_id = None
		for ext_id in self.external_ids:
			if ext_id['name'] == egk_tag and ext_id['issuer'] == egk_issuer:
				egk_id = ext_id['value']
				break
		if egk_id is None:
			_log.debug('cannot search for patient by eGK ID')
			return None

		candidates = gmPerson.get_persons_by_external_id (
			external_id = egk_id,
			external_id_type = egk_tag,
			issuer = egk_issuer
		)
		if len(candidates) != 1:
			_log.debug('cannot uniquely identify person by eGK ID [%s]', egk_id)
			return None

		return candidates[0]

#============================================================
class cAmtsBmpFile:

	# take up to three filenames (or more, in non-strict mode)
	def __init__(self, filename) -> None:
		self.__filename:str = filename
		self.__xml_schema:lxml_etree.XMLSchema = None
		self.xml_doc = None
		self.bmp_version = None

	#--------------------------------------------------------
	# version=..., strict=True/False
	def valid(self):
		for bmp_version in AMTS_BMP_XSDs:
			xsd_filename = os.path.join(gmTools.gmPaths().system_app_data_dir, 'resources', 'amts', AMTS_BMP_XSDs[bmp_version])
			try:
				self.__xml_schema = lxml_etree.XMLSchema(file = xsd_filename)
			except lxml_etree.XMLSchemaParseError:
				_log.exception('cannot find [%s], trying local base dir', xsd_filename)
				# retry, maybe in dev tree
				xsd_filename = os.path.join(gmTools.gmPaths().local_base_dir, 'resources', 'amts', AMTS_BMP_XSDs[bmp_version])
				self.__xml_schema = lxml_etree.XMLSchema(file = xsd_filename)

			with open(self.__filename, encoding = 'iso-8859-1') as bmp_file:
				try:
					self.xml_doc = lxml_etree.parse(bmp_file)
				except lxml_etree.XMLSyntaxError:
					_log.exception('[%s] does not parse as XML', self.__filename)
					break
			validated = self.__xml_schema.validate(self.xml_doc)
			if validated:
				self.bmp_version = bmp_version
				_log.debug('[%s] validates as AMTS BMP v%s', self.__filename, self.bmp_version)
				# check for second/third file !
				return True
			_log.debug('[%s] does not validate against [%s]', self.__filename, xsd_filename)

		_log.debug('[%s] does not validate as AMTS BMP', self.__filename)
		return False

	#--------------------------------------------------------
	def format(self, eol:str=None, verbose:bool=False) -> typing.Union[str, typing.List[str]]:
		assert (self.xml_doc is not None), 'self.xml_doc is None, forgot to call valid() before'

		lines = []
		lines.append(_('AMTS BMP file: %s') % self.__filename)
		lines.append(_('Created: %s') % self.created_when)
		lines.append(_('Version: %s') % self.bmp_version)
		lines.append(_('UID: %s') % self.uid)
		lines.append(_('Creator:'))
		lines.append(' ' + str(self.originator))
		lines.append(_('Patient:'))
		lines.append(' ' + str(self.patient_as_dto))
		lines.append(_('Clinical data:'))
		lines.append(' ' + str(self.clinical_data))
		if verbose:
			lines.append(_('Raw data:'))
			lines.extend(lxml_etree.tostring(self.xml_doc, encoding = 'unicode', pretty_print = True, method = 'xml').split('\n'))

		if eol is None:
			return lines
		return eol.join(lines)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _patient_as_dto(self) -> cDTO_AmtsBmp:
		assert (self.xml_doc is not None), 'self.xml_doc is None, forgot to call valid() before'

		pat = self.xml_doc.find('P').attrib
		dto = cDTO_AmtsBmp()
		# lastname parts
		dto.lastnames = pat['f']
		try:
			dto.lastnames = u'%s %s' % (pat['v'], dto.lastnames)
		except KeyError:
			pass
		try:
			dto.lastnames = u'%s %s' % (pat['z'], dto.lastnames)
		except KeyError:
			pass
		# firstnames
		dto.firstnames = pat['g']
		# title
		try:
			dto.title = pat['t']
		except KeyError:
			pass
		# gender
		try:
			dto.gender = pat['s']
		except KeyError:
			pass
		# DOB
		dob_str = pat['b']
		while dob_str.endswith('00'):
			dto.dob_is_estimated = True
			dob_str = dob_str[:-2]
		dto.dob = dob_str
		source = 'AMTS BMP v%s [uid=%s]' % (self.bmp_version, self.uid)
		# eGK
		try:
			dto.remember_external_id(name = 'eGK', value = pat['egk'], issuer = 'Krankenkasse', comment = source)
		except KeyError:
			pass

		dto.source = source

		return dto

	patient_as_dto = property(_patient_as_dto)

	#--------------------------------------------------------
	def _get_clinical_data(self) -> dict:
		assert (self.xml_doc is not None), 'self.xml_doc is None, forgot to call valid() before'

		O_tag = self.xml_doc.find('O')
		if O_tag is None:
			return {}
		clinical_data = {'valid_when': self.created_when}
		O = O_tag.attrib
		try:
			clinical_data['allergies'] = O['ai'].split(',')
		except KeyError:
			pass
		try:
			clinical_data['pregnant'] = (O['p'] == '1')
		except KeyError:
			pass
		try:
			clinical_data['breast_feeding'] = (O['b'] == '1')
		except KeyError:
			pass
		try:
			clinical_data['weight'] = (decimal.Decimal(O['w']), 'kg')
		except KeyError:
			pass
		try:
			clinical_data['height'] = (int(O['h']), 'cm')
		except KeyError:
			pass
		try:
			clinical_data['creatinine'] = (decimal.Decimal(O['c']), 'mg/dl')
		except KeyError:
			pass
		try:
			clinical_data['comment'] = O['x'].strip()
		except KeyError:
			pass
		return clinical_data

	clinical_data = property(_get_clinical_data)

	#--------------------------------------------------------
	def _get_created_when(self) -> pyDT.datetime:
		assert (self.xml_doc is not None), 'self.xml_doc is None, forgot to call valid() before'

		return pyDT.datetime.strptime (
			self.xml_doc.find('A').attrib['t'],
			'%Y-%m-%dT%H:%M:%S'
		)

	created_when = property(_get_created_when)

	#--------------------------------------------------------
	def _get_uid(self) -> str:
		assert (self.xml_doc is not None), 'self.xml_doc is None, forgot to call valid() before'
		return self.xml_doc.getroot().attrib['U']

	uid = property(_get_uid)

	#--------------------------------------------------------
	#dto.remember_comm_channel(channel=None, url=None):
	#dto.remember_address(number=None, street=None, urb=None, region_code=None, zip=None, country_code=None, adr_type=None, subunit=None)
	def _get_originator(self) -> dict:
		assert (self.xml_doc is not None), 'self.xml_doc is None, forgot to call valid() before'
		A_tag = self.xml_doc.find('A')
		if A_tag is None:
			return {}
		originator = {}
		A = A_tag.attrib
		try:
			originator['id'] = (A['lanr'].strip(), 'lanr')
		except KeyError:
			pass
		try:
			originator['id'] = (A['idf'].strip(), 'idf')
		except KeyError:
			pass
		try:
			originator['id'] = (A['kik'].strip(), 'kik')
		except KeyError:
			pass
		try:
			originator['name'] = A['n'].strip()
		except KeyError:
			pass
		try:
			originator['street'] = A['s'].strip()
		except KeyError:
			pass
		try:
			originator['zip'] = A['z'].strip()
		except KeyError:
			pass
		try:
			originator['city'] = A['c'].strip()
		except KeyError:
			pass
		try:
			originator['phone'] = A['p'].strip()
		except KeyError:
			pass
		try:
			originator['email'] = A['e'].strip()
		except KeyError:
			pass
		return originator

	originator = property(_get_originator)

#============================================================
#============================================================
#============================================================
#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	print('log file:', gmLog2._logfile_name)

	gmDateTime.init()

	#-------------------------------------------------------
	def test_validate_files():
		for fname in sys.argv[2:]:
			print(fname)
			bmp = cAmtsBmpFile(fname)
			if not bmp.valid():
				print('-> failed')
				continue
			print('-> conformant with version', bmp.bmp_version)

	#-------------------------------------------------------
	def test():
		print(sys.argv[2])
		print()
		bmp = cAmtsBmpFile(sys.argv[2])
		if not bmp.valid():
			print('failed')
			return
		print('validated as version', bmp.bmp_version)
		print(lxml_etree.tostring(bmp.xml_doc, encoding = 'unicode', pretty_print = True, method = 'xml'))
		dto = bmp.patient_as_dto
		print(dto)
		print(dto.external_ids)
		print(bmp.created_when)
		print('clinical data:', bmp.clinical_data)
		print('originator:', bmp.originator)
#		print('exists:', dto.exists)
#		cands = dto.get_candidate_identities(can_create=False)
#		print('candidates:')
#		for cand in cands:
#			print(cand)

	#-------------------------------------------------------
	test_validate_files()
	#test()
