#!/usr/bin/python
#
#Copyright: Dr. Horst Herb <hherb@gnumed.net>
#This source code is protected by the GPL licensing scheme.
#Details regarding the GPL are available at http://www.gnu.org
#You may use and share it as long as you don't deny this right
#to anybody else.
#This software is free software by the terms of the GPL license

"""This script imports demographic data from a MDW
(Medical Drirector for Windows (R)) database table
into the gnumed demographic database service.
The imported table is usually named PATIENTS.DBF."""
#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/importers/Attic/gmMDWImporter.py,v $
# $Id: gmMDWImporter.py,v 1.1 2004-04-13 14:24:08 ncq Exp $

__version__ = "$Revision: 1.1 $"
__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

#standard modules
import string
#our own modules
import gmdbf, gmPG


def parse_street_number(str):
	"""returns street number, street name parsed from parameter 'str'
	assuming that if the first character of the first word separated
	by a blank in the street string 'str' is a number, this word
	will represent the street number"""
	#assume there is a space between street number and street
	tokens = string.split(str, ' ')
	#only one word? Can't be number + street name then ...
	if len(tokens)<2:
		return None, str

	#let's check whether the first character of the first token is a number:
	try:
		if int(tokens[0][0]) in range(10):
			number = tokens[0]
		else:
			number = None
	except:
		number = None
	if number is None:
		return number, str
	else:
		return number, string.join(tokens[1:])

def save_quoted(str):
	"""Postgres chokes on single quotes; 
	they have to be escaped by double single quotes"""
	return string.replace(str, "'", "''")


def quoted(str):
	"""add single quotes to a trimmed string suitable for postgres sql queries"""
	if str is None:
		return "''"
	else:
		return "'%s'" % string.strip(save_quoted(str))


def quotedNull(str):
	"""like quoted, only that 'NULL' is returned for empty strings"""
	s = quoted(str)
	if s == "''":
		s = 'NULL'
	return s


def import_person(rec, db):
	"""import a person's demographic data from a MDW record
	into the gnumed database"""
	pc = db.cursor()

	#start a new transaction
	pc.execute('BEGIN')
	#get a new unique ID for this person
	pc.execute("select nextval('identity_id_seq')")
	(id,) = pc.fetchone()

	dob = quotedNull(rec['DOB'])
	deceased = quotedNull(rec['DECDATE'])
	gender = string.strip(string.lower(rec['SEX']))
	if gender not in ('m', 'f'):
		gender = "'?'"
	else:
		gender = "'%s'" % gender
	qstr = "INSERT INTO identity(id, gender, dob, deceased) VALUES (%i, %s, %s, %s)" % \
	        (id, gender, dob, deceased)
	pc.execute(qstr)
	#now the names:
	title = quoted(rec['TITLE'])
	firstnames = quoted(rec['FIRSTNAME'])
	lastnames = quoted(rec['SURNAME'])
	qstr = "insert into names(id_identity, lastnames, firstnames, title) VALUES (%i, %s, %s, %s)" % \
		(id, lastnames, firstnames, title)
	pc.execute(qstr)
	pc.execute('COMMIT')
	return id


def find_address(db, state, postcode, city, number, street):
	"""check whether a street already exists in the gnumed database.
	If so, return it's unique ID - else, return None"""
	c = db.cursor()
	if state == "''":
		state = "'?'"
	c.execute("select addr_id from v_basic_address where state=%s and postcode=%s and \
	            city=%s and number=%s and street=%s" % (state, postcode, city, number, street))
	try:
		(result,) = c.fetchone()
	except:
		result = None
	return result


def import_address(rec, db):
	"""check whether the address as given in parameter 'rec'
	exists already in database 'db'; if not, create it.
	Return the gnumed internal id for this address"""

	pc=db.cursor()
	#first, convert the MDW data into a postgres friendly format
	number, street = parse_street_number(rec['ADDRESS'])
	number=quoted(number)
	street = quoted(street)
	postcode = quoted(rec['POSTCODE'])
	city = quoted(rec['CITY'])
	pc.execute("select find_state(%s, 'AU')" % postcode)
	(state,) = pc.fetchone()
	state = quoted(state)
	if state == "''":
		state="'?'"
	#does this adress exist already?
	addrid = find_address(db, state, postcode, city, number, street)
	if addrid is not None:
		#address exists already, no need to insert it
		return addrid
	#if it doesn't exist yet, create it:
	pc.execute('BEGIN')
	#the rules behind v_basic_address will take care of not inserting
	#anything twice
	qstr = "INSERT INTO v_basic_address(country, state, postcode, city, number, street, address_at) \
                 VALUES ('AU', %s, %s, %s, %s, %s, 1)" % (state, postcode, city, number, street)
	pc.execute(qstr)
	#which address id now?
	pc.execute("select currval('address_id_seq')")
	(addrid, ) = pc.fetchone()
	pc.execute('COMMIT')
	return addrid



def link_person_address(person_id, addr_id, db):
	"""link a person to an address in the many-to-many pivot table"""
	c = db.cursor()
	#id_type 1 = 'home address'
	if addr_id is None:
		print "Shit, addr_id is None!"
	c.execute('BEGIN')
	qstr = ("insert into identities_addresses(id_identity, id_address, id_type) \
	          values (%d, %d, %d)" % (person_id, addr_id, 1))
	c.execute(qstr)
	c.execute('COMMIT')


def process_record(rec, db):
	"""process one MDW demographic record by inserting it's field values
	into the gnumed database"""
	person_id = import_person(rec, db)
	addr_id = import_address(rec, db)
	link_person_address(person_id, addr_id, db)



# open the dBase based demographic MDW file
db = gmdbf.dbf('PATIENTS.DBF');
#request the appropriate service from the gnumed database broker
pgpool = gmPG.ConnectionPool()
pdb = pgpool.GetConnection('personalia')
#loop through all records in the demographic MDW file
i=0
for n in xrange(db.nrecs):
	print i
	process_record(db.dictresult(n), pdb)
	i+=1

#===============================================================
# $Log: gmMDWImporter.py,v $
# Revision 1.1  2004-04-13 14:24:08  ncq
# - first version here
#
