#this script creates a sql table out of LOINCDB.TXT , found in Oct 2004 at www.loinc.org

#precondition



import sys, string, pgdb



# the name of the table that has been created
table="loinc1"
create_table_sql = "create_table_loinc.sql"
# This file can be downloaded from http://www.loinc.org/download/database/LOINCtab.zip
loinc_txt_file = "LOINCDB.TXT"

#check loinc_text_file exists
try:
	f = file(loinc_txt_file, "r")
except:
	print "\n***the loinc db text file ", loinc_txt_file, " is not in the current directory.\n**"
	sys.exit(-3)
	

c = pgdb.connect("localhost:gnumed")
cu = c.cursor()


#test swap standard out
f= sys.stdout
f2 = file("test_swap.txt", "w")
sys.stdout = f2
print "this is a long text"
print "the fox jumped over the lazy dog"
f2.close()
sys.stdout = f


f3 = file("create_table_loinc.sql", "w")
sys.stdout = f3

#USAGE: redirect output to a file e.g. create_loinc_table.sql

s= "create table "+table+"( code text, component text, property text, time text, system text, scale text, method text, "
l = []
for i in range( 8, 61):
	l.append(" col%d text"% i )
s += ",".join(l) + ")"

print s, ";"

#add more print statements as the column titles become clear.

print "alter table "+table+" rename col17 to comment" , ";"
print "alter table "+table+" rename col31 to reference", ";"
print "alter table "+table+" rename col58 to keywords", ";"
print "alter table "+table+" rename col9 to department", ";"

f3.close()
sys.stdout = f

for x in file(create_table_sql):
	cu.execute(x)

c.commit()



longest = 0
last = -1

stmt = "insert into "+table+" values(%s)"

# lists to store unexecutable, and executable statements
errors, ok  = [], []

for x in file(loinc_txt_file):

	# original code to determine if lines had different number of tabs.
	# all data lines have 60 tabs. 
	l = x.split("\t")
	if len(l) > longest:
		longest = len(l)
	if len(l) <> last:
		last = len(l)
		print last
	
	# if this is a data line:	
	if len(l) == 60:

		for j in range(0, 60):
			#remove white space
			l[j] = l[j].strip()

			#preprocess line characters
			for k in range(len(l[j])-1, -1, -1):
				#print l[j][k], "?"

				#escape single quotes	
				if l[j][k] == "'":
					l[j] = l[j][:k] + "'"+ l[j][k:]

				#exclude non-printable characters. fixes UNICODE incompatibility with postgres	
				elif not l[j][k] in string.printable:
					l[j] = l[j][:k] +l[j][k+1:]
					
			#surround blank fields with quote		
			if l[j] is '' or l[j] is None:
				l[j] = "''"

			# make number fields strings
			elif l[j][0] in string.digits:
					l[j] = "'"+l[j]+"'"

			# change text field double quote to single quote for postgres
			elif l[j][0] == '"' :
					l[j] = "'" + l[j][1:-1] +"'"

		s = stmt % ", ".join( l )
		#print s
		try:
			cu.execute(s)
			ok.append(s)
		except:
			print sys.exc_info()[0], sys.exc_info()[1]
			errors.append(s)
			c.rollback()

c.rollback()
		

print longest

print "-------------ERROR STATEMENTS"
print "There were ", len(errors) , " error sql statements. (?Unicode)"

f = file("errors.sql", "w")
for x in errors:
	f.write(x)
	f.write('\n')

f.close()

print "save ok statements ?"
if raw_input('y/n?') == 'y':
	f = file("loinc_data.sql", "w")
	for x in ok:
		f.write(x)
		f.write('\n')
	f.close()	
	
print "Execute ok statements ? "
if raw_input("y/n") == 'y' :
	cu = c.cursor()
	for x in ok:
		cu.execute(x)
	c.commit()	



