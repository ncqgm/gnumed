# -*- coding: utf-8 -*-
"""Import LinuxMedNews XML data.

	http://linuxmednews.com/1414243433"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2"

# std lib
import sys
import datetime as pyDT
import logging
from xml.etree import ElementTree as etree


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPerson


_log = logging.getLogger('gm-LinuxMedNewsXML')

#============================================================
def parse_xml_linuxmednews(xml_text=None, filename=None):
	dob_format = '%Y-%m-%d'

	try:
		if xml_text is None:
			_log.debug('parsing XML in [%s]', filename)
			pat = etree.parse(filename)
		else:
			pat = etree.fromstring(xml_text)
	except etree.ParseError:
		_log.exception('Cannot parse, is this really XML ?')
		return None

	dto = gmPerson.cDTO_person()

	dto.firstnames = pat.find('firstname').text
	dto.lastnames = pat.find('lastname').text
	dto.title = pat.find('name_prefix').text
	dto.gender = pat.find('gender').text
	dob = pyDT.datetime.strptime(pat.find('DOB').text, dob_format)
	dto.dob = dob.replace(tzinfo = gmDateTime.pydt_now_here().tzinfo)
	dto.dob_is_estimated = False
	dto.source = 'LinuxMedNews XML'

	#dto.remember_comm_channel(channel=None, url=None):
	#dto.remember_address(number=None, street=None, urb=None, region_code=None, zip=None, country_code=None, adr_type=None, subunit=None)

	return dto

#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#import datetime
	gmDateTime.init()

	def test():
		print(parse_xml_linuxmednews(filename = sys.argv[2]))

	test()
