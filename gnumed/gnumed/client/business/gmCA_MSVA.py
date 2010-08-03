"""GNUmed to MSVA (Canada) connector classes.

Jim's notes:

- source directory will reside on a Windows NTFS file system volume.
- end-of-Record will be designated by Carriage Return and Line Feed
- character set is "plain Western" (ISO Latin 1)
- record mockup:

FIRSTNAME           XXLASTNAME                 912345677300BC    196012251234512345M6       ADDRESS_LINE_1_XXXXXXXXXXADDRESS_LINE_2_XXXXXXXXXXCITY_XXXXXXXXXXXXXXXXXXXXBCA2A 2A2  604124456760489012340000000002009071307801

- "PHN" + "Dependent #" + "Carrier ID" (in the above example "9123456773", "00", BC") work together as an identifier

- format specification:

*-- MSVAEX30.TXT format
*--
*--------------------------------------------------------------------
*-- First Name          X(20)  No punctuations ( e.g. John Allen)
*-- MSP Initials        X(02)  e.g. JA
*-- Last Name           X(25)
*-- PHN                 9(10)
*-- Dependent #         9(02)  66 for newborn, otherwise zeros
*-- Carrier ID          X(02)  Province providing coverage:
*--                            BC, AB, SA, MB, ON, PQ, OI, NB, NS, NL, YT, NT, NU
*-- Exempt              X(01)  "X" for exempt, otherwise blank
*-- Opted-out           X(01)  "H" for Hard (Send payment to patient address)
*--                            "S" for Soft (Send paymant to office address)
*--                            Blank for Opted-in
*-- Visits Used         9(02)  # of MSP visits used this calendar year, form zero up
*--                            to 12 0r 15 depending on age.
*-- Birthdate           9(08)  ccyymmdd
*-- Payee #             9(05)  
*-- Practitioner #      9(05)
*-- Sex                 X(01)  M, F
*-- Chart #             X(08)
*-- Street 1            X(25)
*-- Street 2            X(25)
*-- City                X(25)
*-- Province            X(02)
*-- Postal Code         X(09) A0A'b'0A0 or US Zip Code
*-- Home Phone          9(10) If no area code use 3 leading zeros
*-- Work Phone          9(10) If no area code use 3 leading zeros
*-- SIN                 9(09)
*-- Last Service Date   9(08) ccyymmdd
*-- Referral Doctor     9(05)
*--
*-- Record size = 220 + <CR><LF> = 222 End-of-Record designated by Carriage Return and Line Feed. 
*-- File is ASCII text - Named "MSVAEX30.TXT"
*-- X(n) = Aplhanumeric, left justified, padded with blanks
*-- 9(n) = Numeric, leading zeros


"""
#============================================================
__license__ = "GPL"
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys, codecs, time, datetime as pyDT


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools, gmDateTime
from Gnumed.business import gmPerson

MSVA_line_len = 220
MSVA_dob_format = '%Y%m%d'
MSVA_encoding = 'latin1'

#============================================================
def read_persons_from_msva_file(filename=None, encoding=None):

	if encoding is None:
		encoding = MSVA_encoding

	pats_file = codecs.open(filename = filename, mode = 'rU', encoding = encoding)

	dtos = []

	for line in pats_file:
		if len(line) < MSVA_line_len:
			continue			# perhaps raise Exception ?

		dto = gmPerson.cDTO_person()
		dto.source = u'Med.Manager/CA'
		dto.external_ids = []

		dto.firstnames = u'%s %s' % (
			gmTools.capitalize(line[:20].strip(), gmTools.CAPS_FIRST_ONLY),		# should be _NAMES
			gmTools.capitalize(line[20:22].strip(), gmTools.CAPS_FIRST_ONLY)	# should be _NAMES
		)
		dto.lastnames = gmTools.capitalize(line[22:47].strip(), gmTools.CAPS_FIRST_ONLY)	# should be _NAMES

		dto.external_ids.append({'name': u'BC.CA PHN', 'value': line[47:57], 'issuer': 'BC.CA MOH', 'context': 'p'})

		dob = time.strptime(line[65:73].strip(), MSVA_dob_format)
		dto.dob = pyDT.datetime(dob.tm_year, dob.tm_mon, dob.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
		dto.gender = line[83].lower()

		dto.external_ids.append({'name': u'MM (CA) Chart #', 'value': line[84:92].strip(), 'issuer': 'Medical Manager (CA) application', 'context': 'p'})

		# this is the home address
		dto.street = u'%s // %s' % (
			gmTools.capitalize(line[92:117].strip(), gmTools.CAPS_FIRST),
			gmTools.capitalize(line[117:142].strip(), gmTools.CAPS_FIRST)
		)
		dto.urb = line[142:167].strip()
		dto.region = line[167:169].strip()
		dto.zip = line[169:178].strip()

		dto.comms = [					# types must correspond to GNUmed database comm type
			{'homephone': line[178:188]},
			{'workphone': line[188:198]}
		]

		dtos.append(dto)

	pats_file.close()

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
	print "reading patient data from MSVA file [%s]" % patfile

	dtos = read_persons_from_msva_file(patfile)
	for dto in dtos:
		print "DTO:", dto
		print "dto.dob:", dto.dob, type(dto.dob)
		print "dto.dob.tz:", dto.dob.tzinfo
		print "dto.zip: %s dto.urb: %s dto.region: %s" % (dto.zip, dto.urb, dto.region)
		print "dto.street", dto.street
		for ext_id in dto.external_ids:
			print ext_id
		for comm in dto.comms:
			print comm
#		searcher = gmPerson.cPatientSearcher_SQL()
#		ident = searcher.get_identities(dto=dto)[0]
#		print ident

#==============================================================
