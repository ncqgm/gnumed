from xmlrpclib import *
import time
import os
import sys
s = Server( "http://localhost.localdomain:9000")
tablename = "enum_confidentiality_level"
count = 30

if len(sys.argv) == 1:
	print "\n\nUSAGE  python test_rpc_client n_clients\n\n\t  where n_clients is number of child processes running calls to xmlrpc server"
	sys.exit(0)

count = int(sys.argv[1])	
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


