"""This is a test client for server generated from gmclinical.sql with analyse_sql3.py"""


from xmlrpclib import *
import time
s = Server( "http://localhost.localdomain:9000")

#print "fields are ", s.get_description('enum_confidentiality_level')
r = s.describe_fields_enum_confidentiality_level()
print "fields are", r
s.create_enum_confidentiality_level("mid level" + time.strftime('%T'))

r = s.select_all_enum_confidentiality_level()

print r

#s.update_enum_confidentiality_level( 4, { 'description': "my change" } )

