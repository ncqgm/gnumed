from xmlrpclib import *
import time
import os
import sys
tablename = "enum_confidentiality_level"
count = 20


def usage():	
	print """
	
	USAGEi:  
		python test_rpc_client -h -c n_clients -p port -s url-string 
	
		where 
			-h	this help
			
			n_clients : number of child processes running calls to xmlrpc server
			
			port : sets the url string to "http://localhost:[port]"

			url-string: sets the url to the given url string including port.

			"""

	sys.exit(0)

from getopt import *

optlist, remaining_args = getopt(sys.argv[1:], 'hc:s:p:')

if len(optlist) == 0:
	usage()

for opt, value in optlist:
	if opt == '-h':
		usage()

	url = "http://localhost.localdomain:9001"
	if opt == '-s':
		url = value

	if opt == '-p':
		url = 'http://localhost.localdomain:'+value
		
	if opt == '-c':
		count = int(value)
		
		
s = Server( url)

for x in xrange(0, count):
	f = os.fork()
	if f in (-1, 0):
		break


if f  > 0:
	t = time.time()
	while(1):
		pid, status = os.waitpid( -1, 0)
		count = count -1
		print "processes left =", count
		if count == 0:
			t = time.time() - t
			print "Time taken = ", t
			from pyPgSQL.PgSQL import *
			c = connect("::gnumed")
			cu = c.cursor()
			print "deleting all from ",tablename," *************"
			cu.execute("delete from "+ tablename)
			cu.execute("commit")
			c.close()
			sys.exit(1)


	
#print "fields are ", s.get_description('enum_confidentiality_level')

r = s.describe_fields_enum_confidentiality_level()
print "\n\nfields are ************", r , "\n\n"
print " adding a tuple **********"
s.create_enum_confidentiality_level("mid level" + time.strftime('%T'))
r = s.select_all_enum_confidentiality_level()
print "select all returns *************"
print r


