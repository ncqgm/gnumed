# -*- coding: latin-1 -*-
"""GnuMed LDT anonymizer.

This script anonymizes German pathology result
files in LDT format.

copyright: authors
"""
#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/khilbert/ldt-anonymizer/anonymize-ldt.py,v $
# $Id: anonymize-ldt.py,v 1.1 2004-05-13 19:44:41 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL, details at http://www.gnu.org"

import fileinput, sys, random, time

def usage():
	print "use like this:"
	print " python anonymize-ldt <ldt-datei>"
	sys.exit()

map_sensitive_fields = {
	'0203': 'anon: doc',
	'0204': 'anon: speciality',
	'0205': 'anon: street',
	'0206': 'anon: zip-city',
	# hardcoded GnuMed test value
	'8300': 'your own practice',
	'8312': 'anon: doc ID',
	# sample ID
	'8310': 'anon: %s',
	'8311': 'anon: lab internal sample ID',
	'8405': 'anon: arbitrary patient info',
	'3101': 'anon: last name',
	'3102': 'anon: first name',
	# Geschlecht: 0 = unbekannt
	'8407': '0'
}

if len(sys.argv) < 2:
	usage()

infilename = sys.argv[1]
outfilename = "%s.anon.txt" % infilename
print "anonymizing [%s] into [%s]" % (infilename, outfilename)

outfile = open(outfilename, "wb+")

random.jumpahead(int(time.strftime('%S%M%H')))

for line in fileinput.input(infilename):
	line_type = line[3:7]
	line_data = line[7:-2]
	if line_type in map_sensitive_fields.keys():
		anon_data = map_sensitive_fields[line_type]
		if line_type == '8310':
			anon_data = map_sensitive_fields[line_type] % random.randrange(sys.maxint)
			# if you don't want random sample IDs uncomment this line:
			#anon_data = map_sensitive_fields[line_type] % "sample ID"
		print "anonymisiere Feld [%s]: [%s] -> [%s]" % (line_type, line_data, anon_data)
		len_int = len(anon_data) + 5
		new_line = "%03d%s%s\r\n" % (len_int, line_type, anon_data)
		outfile.write(new_line)
	else:
		outfile.write(line)

outfile.close()

print "done"

#===============================================================
# $Log: anonymize-ldt.py,v $
# Revision 1.1  2004-05-13 19:44:41  ncq
# - first version
#
