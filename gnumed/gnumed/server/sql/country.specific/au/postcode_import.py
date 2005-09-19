#!/usr/bin/python

usagestr = """

Creates an import script for relevant post code data
from the CSV file provided by Australia post
(http://www.auspost.com.au/postcodes/)into gnumeds database

Copyright 2001 Dr. Horst Herb

This is free software,
licensed under the GNU General Public License (GPL)

USAGE: import_pcode_au <inputfile>

Ouptput happens to stdout; you'll have to redirect output into a file
and import this file from the psql command prompt with the "\i" statement
"""

import string, sys

import_delimiter = ','

#order of entries in the AusPost postcode data file
pcode=0
locality=1
state=2
comments=3

def usage():
    print usagestr


def safestr(str):
	"postgres chokes on embedded ' "
	return string.replace(str, "'", "\''")


try:
	filename = sys.argv[1]
except:
	usage()
	sys.exit("You have to enter the file name of the import file!")

offset=0
ID_ACT = offset+1
ID_NSW = offset+2
ID_NT = offset+3
ID_SA = offset+4
ID_TAS = offset+5
ID_QLD = offset+6
ID_VIC = offset+7
ID_WA = offset+8

states = { 'ACT':ID_ACT, 'NSW':ID_NSW, 'NT':ID_NT, 'SA':ID_SA, 'TAS':ID_TAS, 'QLD':ID_QLD, 'VIC':ID_VIC, 'WA':ID_WA }

print "INSERT INTO state(code, country, name) VALUES ('ACT', 'AU', 'Australian Capital Territory');"
print "INSERT INTO state(code, country, name) VALUES ('NSW', 'AU', 'New South Wales');"
print "INSERT INTO state(code, country, name) VALUES ('NT', 'AU', 'Northern Territory');"
print "INSERT INTO state(code, country, name) VALUES ('SA', 'AU', 'South Australia');"
print "INSERT INTO state(code, country, name) VALUES ('TAS', 'AU', 'Tasmania');"
print "INSERT INTO state(code, country, name) VALUES ('QLD', 'AU', 'Queensland');"
print "INSERT INTO state(code, country, name) VALUES ('VIC', 'AU', 'Victoria');"
print "INSERT INTO state(code, country, name) VALUES ('WA', 'AU', 'West Australia');"

f = open(filename)
lines = f.readlines()
firstline=1
count = 0
begun=0
MAXCOUNT=100 #commit 100 transactions at a time to improve performance

for line in lines:
	#skip the first line containing the headers
	if firstline:
		firstline=0
		continue

	if count==MAXCOUNT:
		begun=0
		count=0

	if count==0:
		begun=1

	count +=1
	tmp = string.split(line, import_delimiter)
	#get rid of the quotation marks of the imported fields
	# FIXME: must get rid of duplicates !!!
	cmd = "insert into urb (id_state, postcode, name) values ((select id from state where country='AU' and code='%s'), %s, '%s');" % (
		tmp[state][1:-1],
		tmp[pcode][1:-1],
		safestr(tmp[locality][1:-1])
	)
	print cmd

print "\nselect gm_upd_default_states();"

if begun:
	pass
