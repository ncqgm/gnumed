import unittest
import jsonrpclib

from GNumed.pycommon import gmPG2

class TestJsonServer(unittest.TestCase):
	def test_login(self):
		s = jsonrpclib.ServerProxy("http://127.0.0.1:8080/services", verbose=0)

#		don't do this!  it causes psycopg2 "connection pool exhausted"
#		and all subsequent queries are rejected.
#		reply = s.get_doc_types()
#		 print reply
		
		reply = s.login("any-doc", "any-doc")
		print reply
		reply = s.get_schema_version()
		print reply
		reply = s.get_doc_types()
		print reply

if __name__=="__main__":
	unittest.main()