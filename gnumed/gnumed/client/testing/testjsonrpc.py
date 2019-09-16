import unittest
from lovely.jsonrpc import proxy


class TestJsonServer(unittest.TestCase):
    def notest_single_login(self):
        session = proxy.Session(username="", password="")
        s = proxy.ServerProxy("http://127.0.0.1:8080/JSON", 
                              session=session, send_id=True)

	#reply = s.login("lkcl", "fail")
        reply = s.login("any-doc", "any-doc")
        print "1", reply
        print

        reply = s.get_schema_version()
        print "1", reply
        print
        reply = s.get_doc_types()
        print "1", reply
        print


    def notest_login(self):
        session = proxy.Session(username="", password="")
        s = proxy.ServerProxy("http://127.0.0.1:8080/JSON", 
                              session=session, send_id=True)

        session2 = proxy.Session(username="", password="")
        s2= proxy.ServerProxy("http://127.0.0.1:8080/JSON", 
                              session=session2, send_id=True)

#       don't do this!  it causes psycopg2 "connection pool exhausted"
#       and all subsequent queries are rejected.
#        reply = s.get_doc_types()
#        print reply
	
        reply = s.login("any-doc", "any-doc")
        #reply = s.login("lkcl", "fail")
        print "1", reply
        print
        try:
            reply = s2.login("any-doc", "fail")
            print "2", reply
            print "FAILURE DID NOT OCCUR"
        except Exception:
            print "expected failure"

        reply = s.get_schema_version()
        print "1", reply
        print

        session3 = proxy.Session(username="", password="")
        s3= proxy.ServerProxy("http://127.0.0.1:8080/JSON", 
                              session=session3, send_id=True)

        reply = s3.login("any-doc", "any-doc")
        print "3", reply
        print

        try:
            reply = s3.get_doc_types()
            print "3", reply
            print
        except Exception:
            print "unexpected failure"

        reply = s2.get_doc_types()
        print "2", reply
        print

    def test_inbox(self):
        session = proxy.Session(username="", password="")
        s = proxy.ServerProxy("http://127.0.0.1:8080/JSON", 
                              session=session, send_id=True)

        reply = s.login("any-doc", "any-doc")
        print "login", reply

        reply = s.get_schema_version()
        print "schema", reply

        reply = s.get_doc_types()
        print "doctypes", reply

        reply = s.get_provider_inbox_data()
        print reply
        
if __name__=="__main__":
    unittest.main()

