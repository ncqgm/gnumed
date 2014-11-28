# -*- coding: utf-8 -*-
"""Import vCard data."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2"

# std lib
import sys
import codecs
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


_log = logging.getLogger('gm-LinuxMedNewsXML')

#============================================================
def parse_vcard2dto(vc_text=None, filename=None):

	import vobject

	if vc_text is None:
		_log.info('trying to parse vCard from [%s]', filename)
		for encoding in ['utf8', 'Windows-1252']:
			try:
				vcf = codecs.open(filename, mode = u'rB', encoding = encoding)
				vc_text = vcf.read()
				vcf.close()
				break
			except UnicodeDecodeError:
				_log.exception('vCard not encoded as [%s]', encoding)
		if vc_text is None:
			return None

	dob_format = '%Y%m%d'

	try:
		vc = vobject.readOne(vc_text)
	except vobject.base.ParseError:
		_log.exception('cannot parse, really a vcf ?')
		return None

	try:
		if vc.kind.value.strip() != u'individual':
			_log.warning('not a vCard for a single person (vCard.KIND=%s)', vc.kind.value)
			return None
	except AttributeError:
		_log.debug('vCard.KIND attribute not available')

	dto = gmPerson.cDTO_person()
	dto.firstnames = vc.n.value.given.strip()
	dto.lastnames = vc.n.value.family.strip()
	if vc.title:
		dto.title = vc.title.value.strip()
	try:
		gender = vc.gender.value.strip().lower()
		if gender != u'':
			dto.gender = gender
	except AttributeError:
		_log.debug('vCard.GENDER attribute not available')
	try:
		dob = pyDT.datetime.strptime(vc.bday.value.strip(), dob_format)
		dto.dob = dob.replace(tzinfo = gmDateTime.pydt_now_here().tzinfo)
		dto.dob_is_estimated = False
	except AttributeError:
		_log.debug('vCard.BDAY attribute not available')
	dto.source = u'vCard %s' % vc.version.value.strip()

	adr = None
	try:
		adr = vc.adr.value
	except AttributeError:
		_log.debug('vCard.ADR attribute not available')
	if adr is not None:
		region_code = None
		region = adr.region.strip()
		if region == u'':
			region = None
		# deduce country
		country_code = None
		country = adr.country.strip()
		if country == u'':
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
		else:
			# deduce region
			if region is None:
				region_row = gmDemographicRecord.map_urb_zip_country2region(urb = adr.city, zip = adr.code, country_code = country_code)
				if region_row is not None:
					region = region_row['state']
					region_code = region_row['code_state']
			else:
				region_code = gmDemographicRecord.map_region2code(region = region, country_code = country_code)
			if region_code is None:
				_log.warning('unknown vCard.ADR.region (%s), using default region', adr.region)
			dto.remember_address (
				number = u'?',
				street = adr.street,
				urb = adr.city,
				region_code = region_code,
				zip = adr.code,
				country_code = country_code,
				adr_type = 'home',
				subunit = None
			)

	tel = None
	try:
		tel = vc.tel.value
	except AttributeError:
		_log.debug('vCard.TEL attribute not available')
	if tel is not None:
		if vc.tel.params.has_key(u'TYPE'):
			channel = (vc.tel.params[u'TYPE'][0]).lower()
			if not channel.endswith('phone'):
				channel += 'phone'
		else:
			channel = u'homephone'
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

	from Gnumed.pycommon import gmLog2

	#import datetime
	gmDateTime.init()

	def test():
		try:
			dto = parse_vcard2dto(filename = sys.argv[2])
			print dto
			print dto.addresses
			print dto.comm_channels
		except:
			_log.exception('cannot parse vCard')
			gmLog2.log_stack_trace()
			raise

	test()
