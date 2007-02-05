"""GNUmed to PracSoft(tm) AU connector classes.

The Australian PracSoft package writes patient data to a file
called PATIENTS.IN whenever patient data is added or edited.

This file has a de-facto format with one patient per line. The
line format has been derived empirically with no knowledge of
PracSoft internals whatsoever. The content is "ASCII" text of
fixed width fields.

This implementation is in the sole responsibility of the authors.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPracSoftAU.py,v $
# $Id: gmPracSoftAU.py,v 1.1 2007-02-05 14:29:04 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys, codecs, time, datetime as pyDT


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools, gmDateTime
from Gnumed.business import gmPerson

PATIENTS_IN_len = 223
PATIENTS_IN_dob_format = '%d/%m/%Y'

#============================================================
def read_persons_from_pracsoft_file(filename=None, encoding='ascii'):

	pats_file = codecs.open(filename=filename, mode='rU', encoding=encoding)
	dtos = []

	for line in pats_file:
		if len(line) < PATIENTS_IN_len:
			continue			# perhaps raise Exception ?

		dto = gmPerson.cDTO_person()
		dto.external_ids = [
			{'PracSoft No.': line[0:9].strip(), 'issuer': 'AU PracSoft application', 'context': 'p'},
			{'CRN': line[166:180].replace(' ', ''), 'issuer': 'Centrelink (AU)', 'context': 'p'},
			{'DVA': line[180:194].replace(' ', ''), 'issuer': "Department of Veteran's Affairs (AU)", 'context': 'p'},
			{'AU-Medicare': line[153:166].replace(' ', ''), 'issuer': 'HIC (AU)', 'context': 'p'}
		]

		dto.title = gmTools.capitalize(line[9:14].strip(), gmTools.CAPS_FIRST)
		dto.firstnames = gmTools.capitalize(line[44:74].strip(), gmTools.CAPS_NAMES)
		dto.lastnames = gmTools.capitalize(line[14:44].strip(), gmTools.CAPS_NAMES)

		dto.gender = line[223].lower()
		dob = time.strptime(line[143:153].strip(), PATIENTS_IN_dob_format)
		dto.dob = pyDT.datetime(dob.tm_year, dob.tm_mon, dob.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

		# this is the home address
		dto.street = gmTools.capitalize(line[74:114].strip(), gmTools.CAPS_FIRST)
		dto.zip = line[139:143].strip()
		dto.urb = line[114:139].strip()

		dto.comms = [					# types must correspond to GNUmed database comm type
			{'homephone': line[194:208].replace(' ', '')},
			{'workphone': line[208:222].replace(' ', '')}
		]
		dto.pracsoft_billing_flag = line[222] # P=pensioner R=repatriation

		dtos.append(dto)

	return dtos
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	patfile = sys.argv[1]
	print "reading patient data from PATIENTS.IN PracSoft file [%s]" % patfile

	dtos = read_persons_from_pracsoft_file(patfile)
	for dto in dtos:
		print "DTO:", dto
		print "dto.dob:", dto.dob, type(dto.dob)
		print "dto.dob.tz:", dto.dob.tzinfo
		print "dto.zip: %s dto.urb: %s" % (dto.zip, dto.urb)
		print "dto.street", dto.street
#		searcher = gmPerson.cPatientSearcher_SQL()
#		ident = searcher.get_identities(dto=dto)[0]
#		print ident

#==============================================================
# $Log: gmPracSoftAU.py,v $
# Revision 1.1  2007-02-05 14:29:04  ncq
# - read PracSoft PATIENTS.IN file
#
#