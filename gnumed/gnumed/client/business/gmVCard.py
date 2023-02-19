# -*- coding: utf-8 -*-
"""Import vCard data."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2"

# std lib
import sys
import datetime as pyDT
import logging


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPerson
from Gnumed.business import gmDemographicRecord


_log = logging.getLogger('gm-vcf')

#============================================================
def __parse_vcard_adr2dto(vcard, dto):
	adr = None
	try:
		adr = vcard.adr.value
	except AttributeError:
		_log.debug('vCard.ADR attribute not available')
		return None

	if not adr:
		return None

	region_code = None
	region = adr.region.strip()
	if region == '':
		region = None
	# deduce country
	country_code = None
	country = adr.country.strip()
	if country == '':
		country = None
	if country is None:
		country_row = gmDemographicRecord.map_urb_zip_region2country(urb = adr.city, zip = adr.code, region = region)
		if country_row is not None:
			country = country_row['country']
			country_code = country_row['code_country']
	else:
		country_code = gmDemographicRecord.map_country2code(country = country)
	if None in [country, country_code]:
		_log.error('unknown vCard.ADR.country (%s), skipping address', adr.country)
		return None

	# deduce region
	if region is None:
		region_row = gmDemographicRecord.map_urb_zip_country2region(urb = adr.city, zip = adr.code, country_code = country_code)
		if region_row is not None:
			region = region_row['region']
			region_code = region_row['code_region']
	else:
		region_code = gmDemographicRecord.map_region2code(region = region, country_code = country_code)
	if region_code is None:
		_log.warning('unknown vCard.ADR.region (%s), using default region', adr.region)

	dto.remember_address (
		number = '?',
		street = adr.street,
		urb = adr.city,
		region_code = region_code,
		zip = adr.code,
		country_code = country_code,
		adr_type = 'home',
		subunit = None
	)
	return dto

#------------------------------------------------------------
def parse_vcard2dto(vc_text=None, filename=None):

	import vobject

	if vc_text is None:
		_log.info('trying to parse vCard from [%s]', filename)
		for encoding in ['utf-8-sig', 'Windows-1252']:
			try:
				vcf = open(filename, mode = 'rt', encoding = encoding)
				vc_text = vcf.read()
				vcf.close()
				break
			except UnicodeDecodeError:
				_log.exception('vCard not encoded as [%s]', encoding)
		if vc_text is None:
			return None
		vcf_lines = []
		found_first = False
		for line in vc_text.split('\n'):
			if not found_first:
				if line.strip() == 'BEGIN:VCARD':
					found_first = True
					vcf_lines.append(line)
				continue
			vcf_lines.append(line)
			if line.strip() == 'END:VCARD':
				break
		vc_text = '\n'.join(vcf_lines)

	dob_format = '%Y%m%d'

	try:
		vc = vobject.readOne(vc_text)
	except vobject.base.ParseError:
		_log.exception('cannot parse, really a vcf ?')
		return None

	try:
		if vc.kind.value.strip() != 'individual':
			_log.warning('not a vCard for a single person (vCard.KIND=%s)', vc.kind.value)
			return None
	except AttributeError:
		_log.debug('vCard.KIND attribute not available')

	dto = gmPerson.cDTO_person()
	dto.firstnames = vc.n.value.given.strip()
	dto.lastnames = vc.n.value.family.strip()
	try:
		dto.title = vc.title.value.strip()
	except AttributeError:
		_log.debug('vCard.TITLE attribute not available')
	try:
		gender = vc.gender.value.strip().casefold()
		if gender != '':
			dto.gender = gender
	except AttributeError:
		_log.debug('vCard.GENDER attribute not available')
	try:
		dob = pyDT.datetime.strptime(vc.bday.value.strip(), dob_format)
		dto.dob = dob.replace(tzinfo = gmDateTime.pydt_now_here().tzinfo)
		dto.dob_is_estimated = False
	except AttributeError:
		_log.debug('vCard.BDAY attribute not available')
	dto.source = 'vCard %s' % vc.version.value.strip()

	dto = __parse_vcard_adr2dto(vc, dto)

	tel = None
	try:
		tel = vc.tel.value
	except AttributeError:
		_log.debug('vCard.TEL attribute not available')
	if tel is not None:
		if 'TYPE' in vc.tel.params:
			channel = (vc.tel.params['TYPE'][0]).casefold()
			if not channel.endswith('phone'):
				channel += 'phone'
		else:
			channel = 'homephone'
		dto.remember_comm_channel(channel = channel, url = tel)

	email = None
	try:
		email = vc.email.value
	except AttributeError:
		_log.debug('vCard.EMAIL attribute not available')
	if email is not None:
		dto.remember_comm_channel(channel = 'email', url = email)

	url = None
	try:
		url = vc.url.value
	except AttributeError:
		_log.debug('vCard.URL attribute not available')
	if url is not None:
		dto.remember_comm_channel(channel = 'web', url = url)

	return dto

#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmDateTime.init()

	def test():
		dto = parse_vcard2dto(filename = sys.argv[2])
		print(dto)
		print(dto.addresses)
		print(dto.comm_channels)

	test()
