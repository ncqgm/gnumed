#!/usr/bin/python


usagestr = """\n\nCreates an import script for relevant post code data
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

print "INSERT INTO state(id, code, country, name) VALUES (%d, 'ACT', 'AU', 'Australian Capital Territory');" % (ID_ACT)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'NSW', 'AU', 'New South Wales');" % (ID_NSW)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'NT', 'AU', 'Northern Territory');" % (ID_NT)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'SA', 'AU', 'South Australia');" % (ID_SA)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'TAS', 'AU', 'Tasmania');" % (ID_TAS)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'QLD', 'AU', 'Queensland');" % (ID_QLD)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'VIC', 'AU', 'Victoria');" % (ID_VIC)
print "INSERT INTO state(id, code, country, name) VALUES (%d, 'WA', 'AU', 'West Australia');" % (ID_WA)


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
		print "COMMIT WORK;"
		begun=0
		count=0

	if count==0:
		print "BEGIN WORK;"
		begun=1

	count +=1
	l = string.split(line, import_delimiter)
	#get rid of the quotation marks of the imported fields
	print "INSERT INTO urb(statecode, postcode, name) values (%d, %s, '%s');" % (states[l[state][1:-1]], l[pcode][1:-1], safestr(l[locality][1:-1]) )
if begun:
	print "COMMIT WORK;"



