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
export_delimiter='\t'
country = 'AU'

#order of entries in the AusPost postcode data file
pcode=0
locality=1
state=2
comments=3

def usage():
    print usagestr



if len(sys.argv) != 2:
    usage()
    sys.exit(1)

filename = sys.argv[1]


f = open(filename)
lines = f.readlines()
counter = -1


print "COPY urb FROM stdin;"


for line in lines:
    l = string.split(line, ',')
    counter += 1
    #skip the first line containing the headings
    if counter==0:
        continue
    #get rid of the quotation marks of the imported fields
    export = "%d\t%s\t%s\t%s\t%s" % (counter, country, l[state][1:-1], l[pcode][1:-1], l[locality][1:-1] )
    print export

print ""
    
