from SimpleCommand import *
from SimplePersonViewMapper import *
import gmPG
import string

#input newData is a map of db field names to updated values.

class SimpleEditPersonStoreCommand(Command):

	def execute(self, oldData, newData):
		mapper = SimplePersonViewMapper().getMapping()

		newData['id'] = oldData['id']
		print "db map = ", newData	

		backend = gmPG.ConnectionPool()
                db = backend.GetConnection('default')

                cursor = db.cursor()
                cmdstr = "commit"
                print cmdstr
                cursor.execute(cmdstr)
 # transaction starts after last commit

                try:
#update using id
			str = "update names set lastnames='%(lastnames)s' , firstnames='%(firstnames)s' where id_identity=%(id)d" % newData
			print str
			cursor.execute(str)
			
			str = "select id_address from identities_addresses where id_identity = %(id)d"% newData
			print str
			cursor.execute(str)
			
			id_addr = cursor.fetchone()[0]
			newData['id_address'] =  id_addr
			str = "update address set street='%(street)s' , addendum='%(addendum)s' where id = %(id_address)d"%newData
			
			print str
			cursor.execute(str)

			str = "update identity set dob='%(dob)s' , gender='%(gender)1s' , pupic='%(pupic)s' where id=%(id)d" % newData
			print str
			cursor.execute(str)
			str = "select * from phone where id_identity = %(id)d"% newData
			cursor.execute(str)
			if cursor.rowcount == 0	:
				str = """insert into phone (id_identity, phone1, phone2) values( %(id)d, 
					'%(phone1)s', '%(phone2)s')""" % newData
			else:
				str = "update phone set phone1='%(phone1)s', phone2='%(phone2)s' where id_identity=%(id)d" % newData
			print str
			cursor.execute(str)
			
			cursor.execute("commit")

		except Exception, errorStr:

			print "failed", errorStr, " : abort"
			cursor.execute("rollback")


			
		
		
			
				
			
		
					
			
			
