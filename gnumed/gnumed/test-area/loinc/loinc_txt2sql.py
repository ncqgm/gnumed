# this script creates a sql script out of LOINCDB.TXT , found in Oct 2004 at www.loinc.org
# initial code by Syan Tan

import sys, string

# the name of the table that has been created
table = "loinc_raw"
loinc_sql_script = "raw_loinc_import.sql"
# This file can be downloaded from http://www.loinc.org/download/database/LOINCtab.zip
loinc_txt_file = "LOINCDB.TXT"

#check loinc_text_file exists
try:
	f = file(loinc_txt_file, "r")
except:
	print "\n***the loinc db text file ", loinc_txt_file, " is not in the current directory.\n***"
	sys.exit(-3)

cols = [
	"code text",
	"component text",
	"property text",
	"time text",
	"system text",
	"scale text",
	"method text"
]
for i in range(8, 61):
	cols.append(" col%d text" % i)

header = """
set client_encoding to "unicode";

\unset ON_ERROR_STOP
drop table %s;
\set ON_ERROR_STOP 1

create table %s (
%s
);

""" % (table, table, ',\n'.join(cols))

print header

#add more print statements as the column titles become clear.

print "alter table %s rename col17 to comment;" % table
print "alter table %s rename col31 to reference;" % table
print "alter table %s rename col58 to keywords;" % table
print "alter table %s rename col9 to department;" % table

print "begin;"

longest = 0
last = -1

stmt = "insert into " + table + " values(%s)"

# lists to store unexecutable, and executable statements
#errors, ok  = [], []

for src_line in file(loinc_txt_file):

	# original code to determine if lines had different number of tabs.
	# all data lines have 60 tabs. 
	fields = src_line.split("\t")
	if len(fields) > longest:
		longest = len(fields)
	if len(fields) <> last:
		last = len(fields)
		print "--", last

	# if this is a data line:
	if len(fields) == 60:
		for j in range(0, 60):
			#remove white space
			fields[j] = fields[j].strip()

			#preprocess line characters
			for k in range(len(fields[j])-1, -1, -1):
				#print "--", fields[j][k], "?"

				#escape single quotes	
				if fields[j][k] == "'":
					fields[j] = fields[j][:k] + "'"+ fields[j][k:]

				#exclude non-printable characters. fixes UNICODE incompatibility with postgres	
#				elif not fields[j][k] in string.printable:
#					fields[j] = fields[j][:k] +fields[j][k+1:]
					
			#surround blank fields with quote		
			if fields[j] is '' or fields[j] is None:
				fields[j] = "''"

			# make number fields strings
			elif fields[j][0] in string.digits:
					fields[j] = "'"+fields[j]+"'"

			# change text field double quote to single quote for postgres
			elif fields[j][0] == '"' :
					fields[j] = "'" + fields[j][1:-1] +"'"

		s = stmt % ", ".join( fields )
		print s
#		try:
#			cu.execute(s)
#			ok.append(s)
#		except:
#			print sys.exc_info()[0], sys.exc_info()[1]
#			errors.append(s)
#			c.rollback()

#c.rollback()

print "commit;"

print "-- longest:", longest

#print "-- -----------ERROR STATEMENTS"
#print "-- There were ", len(errors) , " error sql statements. (?Unicode)"

#f = file("errors.sql", "w")
#for x in errors:
#	f.write(x)
#	f.write('\n')

#f.close()

#print "save ok statements ?"
#if raw_input('y/n?') == 'y':
#	f = file("loinc_data.sql", "w")
#	for x in ok:
#		f.write(x)
#		f.write('\n')
#	f.close()
	
#print "Execute ok statements ? "
#if raw_input("y/n") == 'y' :
#	cu = c.cursor()
#	for x in ok:
#		cu.execute(x)
#	c.commit()
