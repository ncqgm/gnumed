from xmlrpclib import *
import time
import os
s = Server( "http://localhost.localdomain:9000")
for x in xrange(1, 100):
	f = os.fork()
	if f in (-1, 0):
		break

#print "fields are ", s.get_description('enum_confidentiality_level')

r = s.describe_fields_enum_confidentiality_level()

print "fields are", r
s.create_enum_confidentiality_level("mid level" + time.strftime('%T'))

r = s.select_all_enum_confidentiality_level()

print r

#s.update_enum_confidentiality_level( 4, { 'description': "my change" } )

