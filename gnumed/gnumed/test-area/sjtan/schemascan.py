"""some work for a exporter importer"""


import pyPgSQL.PgSQL as dbapi 
import re
import sys
import traceback as tb
import base64
import binascii
credentials = "hherb.com:gnumed:any-doc:any-doc"

""" uncomment the credentials below for local testing.
this is meant to sit on a server object, either local machine or LAN. 
and will take a long time across the internet. 
The values in self.model, self.values, self.collections, self.refs
need to be packed up and serialized by a server for sending to a client.
"""
credentials = "127.0.0.1::gnumed:any-doc:any-doc"

class SchemaScan:
	
	def __init__(self, config = None):
		self.conn = dbapi.connect(credentials)
		print
		print "inherits"
		for x in  self.get_inherits():
			print x
		print
		print "fk list"
		for x in  self.get_fk_list():
			print x
		print
		print "fk details"


		self._pks = dict([ (x[0],x[1]) for x in self.get_pk_attr() ])

		print "pks ", self._pks

		m = {}	
		for child, parent in self.get_inherits() :
			l = m.get(parent, [])
			l.append(child)
			m[parent] = l
		self._inherits = m



		many_to_one = {}
		one_to_many = {}

		mto = {}
		otm = {}
		
		for t1, fk, t2, pk in self.get_fk_details():
			print t1,".", fk ,"->" ,t2,".", pk

		for t1, fk, t2, pk in self.get_fk_details():
			m= many_to_one.get(t2, {})
			many_to_one[t1] = m
			m[fk]= (t2, pk)

			m = one_to_many.get(t2, {})
			one_to_many[t2] = m
			m[t1+"."+fk] = ( t1, fk, pk)

		
		id = int(raw_input("id of identity:"))

		q = [("identity", self._pks['identity'], id), ("xlnk_identity", "xfk_identity", id) ]

		# must account for xfk_identity as well


		vals = {}	

		while q <> []:
			t, key , kval  = q.pop(0)
			stmt = "select * from %s where %s = %d" % (t, key, kval )
			print "trying to execute", stmt
			try:
				r, desc = self.execute(stmt)
			except:
				tb.print_tb(sys.exc_info()[2])
				continue
			print r
			print desc
			if r == []:
				continue
				
			v = vals.get(t ,{})
			vals[t] = v
			for row in r:
			# v[id] is a map =  { field0 : val, type  , field1: val1, type1 ....  }
				print "row is ", row
				entry  = dict( [ (x,y) for x,y in zip( [d[0] for  d in desc] , [ (a,b) for a,b in zip( row, [d2[1] for d2 in desc] )] ) ] )
				#print "entry", entry

				print "self._pks[t]", self._pks[t]
				try :
					id = int(entry[self._pks[t]][0])
				except:
					print "Error find self._pks[t][0]"
					print "t = ", t
					print "pk = ", pk
					print "self._pks"  , self._pks
					continue
				

				if v.has_key(id):
					continue

				v[id] = entry # key according to primary key

				
				print "v of id=", id , " is ", v[id]

				m = many_to_one.get(t, {})
				for fk in m.keys():
					try:
						q.append( ( m[fk][0], m[fk][1], int(entry[fk])  ) )
					except:
						print "t=", t, " many to one for t is ", m
						print "fk=", fk
						print "error", "m[fk][0]",m[fk][0]
						print "m[fk][1]", m[fk][1]
						print " entry[fk]", entry.get(fk, None)

				m = one_to_many.get(t, {})
				print "one_to_many for t is ", m
				for t_fk in m.keys():
					try:
						fkval =  int(entry[m[t_fk][2]][0])
						table= m[t_fk][0]
						fk = m[t_fk][1]
						q.append( (table, fk, fkval) )
						for t in self._inherits.get(table, []):
							q.append( (t, fk, fkval) )
					except:
						print "error for ", t_fk , " of ", m

					
			
				print

		print
		print "The vals are " 
		for k,v in vals.items():
			print k
			for id,v2 in v.items():
				print "\t",id
				for field, v2 in v2.items():
					if str(v2[1]) == 'bytea':
						val = v2[0].__repr__()
					else:
						val = v2[0]
					print "\t\t", field, ": ",val ,"," , v2[1]


					
			print
			


	def get_inherits(self):

		cu = self.conn.cursor()
		cu.execute("""
		select c1.relname, c2.relname from pg_class c1, pg_class c2, pg_inherits c3
		where c3.inhrelid = c1.relfilenode and c3.inhparent = c2.relfilenode""")
		return cu.fetchall()

	def get_fk_list(self):
		"""get a foreign key list from pg_constraint"""
		cu = self.conn.cursor()
		cu.execute("""
		select c1.relname, c2.relname from pg_class c1, pg_class c2, pg_constraint c3 where c1.relfilenode = c3.conrelid and c2.relfilenode = c3.confrelid and c3.contype='f'""")
		r = cu.fetchall()
		return r


	def get_fk_details(self):
		"""gets table, keying attribute, foreign table, foreign key attr"""

		cu = self.conn.cursor()
		cu.execute( """
		select c1.relname,a1.attname, c2.relname, a2.attname from pg_class c1, pg_class c2, pg_constraint c3 , pg_attribute a1, pg_attribute a2 where c1.relfilenode = c3.conrelid and c2.relfilenode = c3.confrelid and c3.contype='f' and c3.conrelid = a1.attrelid and c3.conkey[1] = a1.attnum and c3.confkey[1] = a2.attnum and c3.confrelid = a2.attrelid
			""")
		r = cu.fetchall()
		return r
		

	def get_attributes(self, table, foreign_keys = 0):
		if foreign_keys:
			fk_cmp = ''
		else:
			fk_cmp = 'not'

		cu = self.conn.cursor()
		tables_checked_for_fk = [table] + self.get_ancestors(table)
		clause = """select attname from pg_attribute , pg_class, pg_constraint   where relfilenode = attrelid and relname = '%s' and pg_constraint.conrelid = relfilenode and pg_constraint.contype ='f' and conkey[1] = attnum"""
		l_fk = []
		for x in tables_checked_for_fk:
			l_fk.extend([ x[0] for x in self.execute(clause % x)] )
			

		l = self.global_implied_attrs + l_fk
		excludes = ', '.join ( [ ''.join(["'",x,"'"]) for x in l ] ) 
		r = self.execute("""
		select attname from pg_attribute a, pg_class c where c.relfilenode = a.attrelid and
		c.relname = '%s' and attnum > 0 and a.attname %s in ( %s ) """ % ( table, fk_cmp, excludes) ) 
		l = [ x[0] for x in r]
		return l

	def get_attribute_type(self, table, attr):
		if not self.attr_types.has_key(table):
			r = self.execute("""
		select attname, typname from pg_type t, pg_attribute a, pg_class c where c.relfilenode = a.attrelid and c.relname = '%s'  and a.atttypid = t.oid
			""" % ( table) )
			self.attr_types[table]  = dict([ (x[0],x[1]) for x in r] )

		return self.attr_types[table].get(attr,'text') 
		

	def execute(self,stmt):
		cu = self.conn.cursor()
		try:
			cu.execute(stmt)
		except:
			raise
		r = cu.fetchall()
		return r , cu.description
		
	
	def get_pk_attr( self):
		stmt = """
		select  c.relname, a.attname from pg_attribute a, pg_class c, pg_constraint pc where  a.attrelid = c.relfilenode and pc.contype= 'p' and pc.conrelid = a.attrelid and pc.conkey[1] = a.attnum

		""" 
		cu = self.conn.cursor()
		cu.execute(stmt)
		return cu.fetchall()

if __name__=="__main__":
	s = SchemaScan()
