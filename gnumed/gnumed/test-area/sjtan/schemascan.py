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
#credentials = "127.0.0.1::gnumed:gm-dbo:pass"
credentials = "127.0.0.1::gnumedtest:gm-dbo:pass"

class SchemaScan:
	
	def __init__(self, config = None):
		global credentials
		print "running from credentials = ", credentials
		answ = raw_input("continue (hit enter), or enter new credentials:")
		if answ <> "" and len( answ.split(":")) >= 5:
			credentials = answ

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

		#		map of tablename : primary key
		
		self._pks = dict([ (x[0],x[1]) for x in self.get_pk_attr() ])

		print "pks ", self._pks

		m = {}	
		for child, parent in self.get_inherits() :
			l = m.get(parent, [])
			l.append(child)
			m[parent] = l
		
		#  map of parent: list of children		
		self._inherits = m


		# map of referring table, referring foreign key field: tuple of (referred table, referred field)
		many_to_one = {}
		
		#map of referred to table : referring table and foreign key as 'table.fk' : and tuple ( of referred to table, foreign key, referred to key)
		
		one_to_many = {}


		self._many_to_one = many_to_one

		self._one_to_many = one_to_many

		for t1, fk, t2, pk in self.get_fk_details():
			print t1,".", fk ,"->" ,t2,".", pk

		for t1, fk, t2, pk in self.get_fk_details():
			if not many_to_one.has_key(t1):
				many_to_one[t1] = {}

			many_to_one[t1][fk]= (t2, pk)

			if not one_to_many.has_key(t2):
				one_to_many[t2] =  {}

			one_to_many[t2][t1+"."+fk] = ( t1, fk, pk)

		
		id = int(raw_input("id of identity:"))

		q = [("identity", self._pks['identity'], id), ("xlnk_identity", "xfk_identity", id) ]

		# must account for xfk_identity as well


		# the map to store the instance data: map is of form map  key=tablename: value = map of id: data
		# e.g     table1
		#            id1      
		#                   field1:data1 , field2:data2
		#	     id2
		#                   ....
		#        table2
		#	     id4   
		#                  .....
		vals = {}	
		
		# not used, for debugging
		step_through = 0

		constants = ['test_type_unified', 'encounter_type', 'vacc_indication', 'lnk_vacc_ind2code', 
				'_enum_allergy_type',
				'vacc_regime', 'vacc_def',
				'vacc_route', 'vaccine', 'lnk_vaccine2inds',
				'doc_type'
				
				]

		while q <> []:
			t, key , kval  = q.pop(0)
			if t in constants:
				continue
			stmt = "select * from %s where %s = %d" % (t, key, kval )
			print "trying to execute", stmt
			try:
				r, desc = self.execute(stmt)
			except:
				tb.print_tb(sys.exc_info()[2])
				continue
			#print r
			#print desc
			if r == []:
				continue
			if not vals.has_key(t) :
				vals[t]  = {}
			for row in r:
			# v[id] is a map =  { field0 : val, type  , field1: val1, type1 ....  }
				#print "row is ", row

				# entry is a map of field: value, type

				entry  = dict( [ (x,y) for x,y in zip( [d[0] for  d in desc] , [ (a,b) for a,b in zip( row, [d2[1] for d2 in desc] )] ) ] )
				#print "entry", entry

				#print "self._pks[t]", self._pks[t]
				try :
					id = int(entry[self._pks[t]][0])
				except:
					print "Error find self._pks[t][0]"
					print "t = ", t
					print "pk = ", pk
					print "self._pks"  , self._pks
					continue
				

				if vals[t].has_key(id):
					continue

				vals[t][id] = entry # key according to primary key

				
				#print "v of id=", id , " is ", vals[t][id]

				m = many_to_one.get(t, {})
				for fk in m.keys():
					try:
						attr_val = entry[fk][0]
						q.append( ( m[fk][0], m[fk][1], int(attr_val)  ) )
					except:
						print "t=", t, " many to one for t is ", m
						print "fk=", fk
						print "error", "m[fk][0]",m[fk][0]
						print "m[fk][1]", m[fk][1]
						print " entry[fk]", entry.get(fk, None)
						#raw_input("continue ?")

				m = one_to_many.get(t, {})
				#print "one_to_many for t is ", m
				for t_fk in m.keys():
					try:
						fkval =  int(entry[m[t_fk][2]][0])
						table= m[t_fk][0]
						fk = m[t_fk][1]
						if table == 'xlnk_identity':
							print "appending ", table, fk, fkval
							raw_input("Continue?")
						q.append( (table, fk, fkval) )
						for t in self._inherits.get(table, []):
							q.append( (t, fk, fkval) )
					except:
						print "error for ", t_fk , " of ", m
						#raw_input("continue ?")

					
			
				print

		a = raw_input("export to file?")

		if a <> "" and a[0] == 'y':
			f = raw_input("file_name to export to:")
			o = file(f, "w")
			sys.stdout = o
			
		
		abstract = ['clin_root_item']
		for t in abstract:
			del vals[t]


		print
		for k,v in vals.items():
			print k
			for id,v2 in v.items():
				print "\t",id
				for field, v2 in v2.items():
					if str(v2[1]) == 'bytea':
						val = base64.encodestring(str(v2[0]))
					else:
						val = v2[0]
					print "\t\t", field, ": ",val ,"," , v2[1]


					
			print

		sys.stdout = sys.__stdout__

		f = raw_input("sql file to export (default rec.sql):")
		if f == "":
			f = "rec.sql"

			o = file(f, "w")
			sys.stdout = o

		#this section creates static types that should exist in target schema
		types = ['test_type_unified']
		for table in types:
			r,desc = self.execute("select * from %s" % table)
			for row in r:
				fields, values = [], []
				for (f,type ), v in zip ( [ (d[0],d[1]) for d in desc], row):
					fields.append(f)
					if str(type) == 'integer':
						values.append(str(v))
					else:
						values.append("'"+str(v) + "'")
				print "insert into %s ( %s) values ( %s);" % ( table, ", ".join(fields), ", ".join(values))
				
		
			
			

			
		print "drop table id_remap;"
		print "begin;"
		print "set constraints all deferred;"
		print "create temp table id_remap ( relname text, old_id integer, new_id integer);"
		sql = {}
		new_ids = {}
		for t, v in vals.items():
			sql[t] = {}
			for id, v2 in v.items():
				print "insert into id_remap values ('%s', %d);" % ( t, id)
			
			print "update id_remap set new_id = nextval('%s_%s_seq') where relname='%s';" % ( t, self._pks[t], t)

	
		# remove static application inserts
		for x in constants:
			if vals.has_key(x):
				del vals[x]

		stmts = {}
		for t, v in vals.items():
			stmts[t]= []
			for id , v2 in v.items():
				find_id = "select new_id from id_remap where relname='"+t+"' and old_id = " + str(id) 
				find_id = "coalesce(("+find_id+"))"
				if not new_ids.has_key(t) :
					new_ids[t] = {}
				new_ids[t][id] = find_id

				m = {}
				skip_fields= ["pk_audit"]

				for field, (val, type) in v2.items():
					if str(type) == 'integer' :
						m[field] = str(val)
						if str(val) in ["", "None"]:
							skip_fields.append(field)
							continue
						if self._pks[t] == field:
							m[field] = find_id
						elif field == "xfk_identity":
							m[field] = "( select new_id from id_remap where relname='identity' and old_id = %d)" % int(val) 
						elif self._many_to_one.get(t,{}).has_key(field):
							t2,pk = self._many_to_one[t][field]
							if not t2 in constants:
								t3 = t2
								if t2 == 'xlnk_identity':
									t3 = 'identity'
								m[field] = "coalesce((select %s from %s where %s = ( select new_id from id_remap where relname='%s' and old_id = %d)))" % ( pk, t2, pk ,t3, int(val))
						

					elif str(type) == 'bytea':
						m[field] = "decode('" + base64.encodestring(str(val)) +"','base64')"
					else:
						if str(val) == 'None':
							m[field] = 'null'
						else:
							if str(type) == 'interval':
								s = str(val).split(':')

								if s[-1].find('.') >= 0:
									s[-1] = s[-1].split('.')[0]

								m[field] = "'" + s[0] + " " + ":".join(s[1:]) + "'"
							else:
								m[field] = "'" + str(val) + "'"
				fields = []
				values = []
				for f,v in m.items():
					if f in skip_fields:
						continue
						
					fields.append(f)
					values.append(v)
				stmt = "insert into "+t+"  ("+ ', '.join(fields)+ ") values("+', '.join(values)+")" + ";" 
				stmts[t].append(stmt)		


		# reorder the statements for dependencies
		depends = {}
		for t1, fk, t2, pk in self.get_fk_details():
			if not depends.has_key(t1):
				depends[t1] = {} 
			depends[t1][t2] = 1
			
		ordered = []
		while len(stmts) > 0:
			for t, statements in stmts.items():
				found_dependency = 0
				for t2 in stmts.keys():
					if t <> t2 and depends.get(t,{}).has_key(t2):
						found_dependency = 1
						break	
				if not found_dependency:
					ordered.extend(statements)
					del stmts[t]
			
		for x in ordered:
			print x

		print "set constraints all immediate;"
		print "drop table id_remap;"
		
		print "commit;"
				

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
