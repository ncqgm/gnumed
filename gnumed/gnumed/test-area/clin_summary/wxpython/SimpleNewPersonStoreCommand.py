import SimpleCommand # SImpleCommand just defines the interface method: execute( self, src, params): pass
import gmPG
import pgdb

from  SimplePersonViewMapper import *

# version 0.1 21-3-2002
#Inputs:  data - a map with keys: first name, last name, birthdate,sex, address 1 , address 2, medicare no 
# these input names are hardcoded in this version,  and are hardcode mapped to 
# the tables  
#	identity ( gender, dob, pupic)  for sex, birthdate and medicare no
#	names 	 (lastnames, firstnames) for  first name and last name
#	address	 (street, addendum ) for address 1 , address 2
#
#	the relational links are also created
#	
#	any change in the map names, or the table attribute names, or the table names ,
#	 means that this file will need to be changed
	
class NewPersonStoreCommand( SimpleCommand.Command):

	def execute ( self, src, data):
		mapper = SimplePersonViewMapper().getMapping()
		data = mapper.mapKeysToFieldNames(data)

		print "mapped " , data

		backend = gmPG.ConnectionPool()
		db = backend.GetConnection('default')
			
		cursor = db.cursor()
		cmdstr = "commit"
		print cmdstr
                cursor.execute(cmdstr)
 # transaction starts after last commit

		try:
#insert into the identity table
			cmdstr = "insert into identity( gender, dob, pupic) values ('%(gender)1s' , '%(dob)s', '%(pupic)s' )"%data
			print cmdstr
			
			cursor.execute(cmdstr)

 #get the newly created last identity id    
			cmdstr = "select last_value from identity_id_seq"
			print cmdstr
			cursor.execute(cmdstr)
			id_id  = cursor.fetchone()[0]

# add the identity id into the data map for saving in the names table
			data['id_id'] = id_id

			cmdstr = "insert into names (id_identity,  lastnames, firstnames) values( %(id_id)d, '%(lastnames)s', '%(firstnames)s' )"%data
			print cmdstr
			cursor.execute(cmdstr)

#get the newly created names id
			cmdstr = "select last_value from names_id_seq"
			print cmdstr
		
			cursor.execute(cmdstr)
			name_id  = cursor.fetchone()[0]
			print "name id used = ", name_id
#insert into the address table		
			cmdstr = "insert into address ( street, addendum ) values ( '%(street)s' , '%(addendum)s' )"%data
			print cmdstr
			cursor.execute(cmdstr)
# get the newly created address id
			cmdstr = "select last_value from address_id_seq"
			print cmdstr
			cursor.execute(cmdstr)

			addrid = cursor.fetchone()[0]

			print "addrid = ", addrid
# create the relational link between identity and address
			cmdstr ="""insert into identities_addresses (id_identity, id_address, address_source)
			  values ( %d, %d, 'NewPersonStoreCommand.py.v0.1')""" % ( id_id, addrid)
			print cmdstr
			cursor.execute(cmdstr)

			cmdstr = """insert into phone( id_identity, phone1, phone2) values ( %(id_id)d, '%(phone1)s',
				'%(phone2)s' )"""% data
			print cmdstr
			cursor.execute(cmdstr)
			cursor.execute('commit')
		except Exception , errormsg:
			print "error in transaction", errormsg
			cursor.execute('rollback')
		
