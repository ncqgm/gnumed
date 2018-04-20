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

A0A'b'0A0:

	- standard Canadian postal code format which is 3 characters:
		- (upper case letter + single digit number + upper case letter)
		- followed by a breaking space
		- followed by (number+letter number)

US Zip code:

	- 12345 or 12345-1234

Dependant # / Carrier ID

I did some checking, and it seems in BC a corner case about
the "00" being instead "66". The provision to designate
newborns (as dependent "66" and, in the case of multiple
births, "64" ... "63") seems now obsoleted by the ability of
the hospital to log into the provincial system and generate
a new Personal Health Number. Any such legacy values in
Medical Manager would not be to drive the slave.

The PHN can therefore be taken as unique *within* carrier
ID. While the following may be far fetched, there is no
agreement between Canada's provinces to avoid collisions, so
it could be possible to exist

 	BC.CA MOH | Personal Health Number | 90123456780
 	ON.CA MOH | Personal Health Number | 90123456780

"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys, io, time, datetime as pyDT


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

	pats_file = io.open(filename, mode = 'rt', encoding = encoding)

	dtos = []

	for line in pats_file:
		if len(line) < MSVA_line_len:
			continue			# perhaps raise Exception ?

		dto = gmPerson.cDTO_person()
		dto.source = 'Med.Manager/CA'

		dto.firstnames = '%s %s' % (
			gmTools.capitalize(line[:20].strip(), gmTools.CAPS_FIRST_ONLY),		# should be _NAMES
			gmTools.capitalize(line[20:22].strip(), gmTools.CAPS_FIRST_ONLY)	# should be _NAMES
		)
		dto.lastnames = gmTools.capitalize(line[22:47].strip(), gmTools.CAPS_FIRST_ONLY)	# should be _NAMES

		region = line[59:61]
		dto.remember_external_id (
			name = 'PHN (%s.CA)' % region,
			value = line[47:57],
			issuer = 'MOH (%s.CA)' % region
		)

		dob = time.strptime(line[65:73].strip(), MSVA_dob_format)
		dto.dob = pyDT.datetime(dob.tm_year, dob.tm_mon, dob.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
		dto.gender = line[83].lower()

		dto.remember_external_id (
			name = 'MM (CA) Chart #',
			value = line[84:92],
			issuer = 'Medical Manager (CA) application'
		)

		# this is the home address
		street = '%s // %s' % (
			gmTools.capitalize(line[92:117].strip(), gmTools.CAPS_FIRST),
			gmTools.capitalize(line[117:142].strip(), gmTools.CAPS_FIRST)
		)
		dto.remember_address (
			number = '?',
			street = street,
			urb = line[142:167],
			region_code = line[167:169],
			zip = line[169:178],
			country_code = 'CA'
		)

		# channel types must correspond to GNUmed database comm type
		dto.remember_comm_channel(channel = 'homephone', url = line[178:188])
		dto.remember_comm_channel(channel = 'workphone', url = line[188:198])

		dto.remember_external_id (
			name = 'Social Insurance Number',
			value = line[198:207],
			issuer = 'Canada'
		)

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
	print("reading patient data from MSVA file [%s]" % patfile)

	dtos = read_persons_from_msva_file(patfile)
	for dto in dtos:
		print("DTO:", dto)
		print("dto.dob:", dto.dob, type(dto.dob))
		print("dto.dob.tz:", dto.dob.tzinfo)
		print("dto.zip / urb / region: %s / %s / %s" % (dto.zip, dto.urb, dto.region))
		print("dto.street:", dto.street)
		for ext_id in dto.external_ids:
			print(ext_id)
		for comm in dto.comms:
			print(comm)
#		searcher = gmPersonSearch.cPatientSearcher_SQL()
#		ident = searcher.get_identities(dto=dto)[0]
#		print ident

#==============================================================
