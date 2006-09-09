"""
Copyright (C) 2006 author

    This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
	    the Free Software Foundation; either version 2 of the License, or
	        (at your option) any later version.

		    This program is distributed in the hope that it will be useful,
		        but WITHOUT ANY WARRANTY; without even the implied warranty of
			    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
			        GNU General Public License for more details.

"""

#BUG NOTES:

# Big Bug 1 (fixed):  the null character (\0) is in the data ,and will terminate strings
# and stop the dbapi working  so filter it out.


import struct
import sys, os
verbose = True 
import base64
import pwd_decrypt
import StringIO
import traceback
import zipfile
import string

from bmp_extract import Extract as MemoGet
# if the sql statements fail because of a dbf naming clash with the target
# database, then add that name to NAME_CLASH in uppercase.
# a _ will be prepended when that name is encountered.
NAME_CLASH=[ "USER", "DESC", "DEFAULT" ]

compressed_base64= True

base64_default_substring = ['doc00']

def get_pg_number_ddl( sz, deci):
	""" gets the postgres datatype for dbf N types """
	assert ( deci < sz)
	if deci == 0:
		return 'integer'
	else:
		return 'numeric(%d, %d)' % (sz,deci)
	

"""a map of dbf types to postgres types """
map_sqltype = { 'postgres': { 	'C': lambda sz, deci:  'varchar('+str(sz)+')' , 
				'D' :lambda sz, deci: 'timestamp' ,
				
				'M' : lambda sz, deci: 'text' ,
				'N':  get_pg_number_ddl , 
				'L': lambda sz, deci: 'boolean', 
				'I': lambda sz,deci : 'integer'	,
				'O': lambda sz,deci : 'double'
				}  }

"""what datatypes are quoted """
dml_quoted = { 'postgres':   	"CDML" }

quotes = '\',\",\`'.split(',')
def escape_q( s):
	s2 = []
	for x in s:
				
		if x == '\0':
			continue
		
		if x in quotes or x not in string.printable:
			s2.append('\\')
		s2.append(x)	
	return ''.join(s2)
				

def psycopg_dsn(dsn):
	elems = ['host','port', 'dbname', 'user', 'password']
	vals = dsn.split(':')
	l = []
	for i,x in enumerate(vals):
		if x <> '':
			l.append( "%s='%s'" % (elems[i], x) )
	
	return " ".join(l)
	
	
def nocase_in( word, list):
	w = word.strip().lower()
	l = [x.strip().lower() for x in list]
	return w in l
	
class Parser:
	def __init__(self, filename, output_stream = None):
		
		if output_stream is None:
			output_stream = sys.stdout

		self._filename = filename

		self._f= file(filename, 'rb')
		self._memogetter = None
		version,numrecs,lenheader=struct.unpack('<BxxxLH22x', self._f.read(32))
		self._numrecs, self._lenheader, self._version = numrecs,lenheader, version
		
		numfields = lenheader /32 - 1
		self._numfields = numfields
	
		sys.stdout = output_stream
		
		print "numrecs", numrecs
		print "numfields", numfields
		print "lenheader", lenheader

		self._indexes = {}
		self._parse_fields()

		self._password = file('pass.txt', 'r').read().strip()

	def get_numrecs(self):
		return self._numrecs

	def version(self):
		return self._version

	def _parse_fields(self):
		fields = []
		recsize = 1  # already offsetted for delete byte
		field_offset= {}
		for i in xrange(self._numfields):
			name, ftype, size, deci = struct.unpack('>11sc4xBB14x', self._f.read(32))
			name = name[:name.find('\x00')]
			print name, ftype, size, deci
			fields.append( (name , ftype, size, deci))
			field_offset[name] = recsize
			recsize += size

		self._field_offset = field_offset
		self._recsize = recsize
		self._fields = fields

		self._msize = dict( [ (name, size) for (name,ftype,size,deci) in self._fields] )

		assert(self._f.read(1)=='\r')
		self._extrachar =  hex(ord(self._f.read(1) )) # offset

		self._recno = 0

		self._datastart = self._f.tell()

		sys.stdout = sys.__stdout__
		
	def get_fields( self):
		"""returns a list of ( name, fieldtype, size, deci)"""
		l = []
		l.extend(self._fields)
		return l

	def get_ddl_sql(self, dialect = "postgres"):
		ddl_fields = []
		if not dialect or dialect is "postgres":
			for name, fieldtype, size,deci in self._fields:

				if name.upper() in NAME_CLASH:
					name = '_' + name

				ddl_field = " ".join ([ name , map_sqltype['postgres'][fieldtype](size,deci) ])
				ddl_fields.append(ddl_field)

		return " ".join( ["create table ", self.get_tablename(), " (\n" , ",\n".join(ddl_fields), "\n)" ])
				
		
	def get_memo_fields(self):
		l = []
		for name, ftype, size, deci in self._fields:
			if ftype.lower() == 'm':
				l.append(name)
		return l

	def get_index(self, field, update = False):
		if not self._msize.has_key(field):
			return None
		if not update and self._indexes.has_key(field):
			m2 = {}
			m2.update(self._indexes[field])
			return m2 
			
		self._f.seek(self._datastart)
		
		m= {}
		
		sz  = self._msize[field]
		offset =self._field_offset[field]
		
		for i in xrange(0, self._numrecs):
			pos =  i * self._recsize + self._datastart
			self._f.seek( pos)
			self._f.seek ( offset, 1)
			id = str(self._f.read(sz)).strip()
			if not m.has_key(id):
				m[id]= [ pos]
			else:
				m[id].append(pos)
		m2 = {}
		m2.update(m)
		self._indexes[field] = m2

		return m
	
	def get_rec_count(self, field, ival):
		if not ival:
			return 0

		l = self._get_list(field, str(ival).strip())

		if not l:
			return None

		return len(l)
		

	def _get_list( self, field, ival):
		"""gets the list of record positions sharing the same ival at field"""
		if not ival:
			return None

		ival = str(ival).strip()

		if not self._indexes.has_key(field):
			m = self.get_index(field)
		else:
			m = self._indexes[field]

		if not m or not m.has_key(ival):
			return None

		l = m[ival]
		return l
		
	def find_rec( self, field, ival, ipos = 0):
		"""finds the record on the list position ipos having ival at field"""

		l = self._get_list(field, ival)

		if not l:
			return None
		
		if   len(l) <= ipos:
			return None

		
		recpos  = l[ipos]

		self._f.seek(recpos+1)
		
		return self._read_rec()	
		

	def next(self, memo_data = False):
		if self._recno >= self._numrecs:
			return None, None
			
		m = {}
		self._f.read(1)
		
		d, m = self._read_rec(memo_data)

		self._recno += 1

		return d,m

		
		
	def _read_rec(self, get_memo = False):
		data = []
		m = {}
		for field in self._fields:
			(name, ftype, size, deci) = field
			d = self._f.read(size)
			if ftype == 'I':
				d = str( struct.unpack('<i', d) )
			elif ftype == 'O':
				d = str( struct.unpack('d', d) )
			elif ftype == 'M' and get_memo :
				d = self.get_memo_data(d )
				d = d.encode()
			data.append( (name,size,ftype, d))
			m[name] = {'size':size,'type': ftype,'data': d  }

		return data ,m

	def next_sql_insert(self, dialect = 'postgres', base64_memo = False, decrypt_memo= []):
		d,m = self.next()
		if d is None:
			return None
		f_val_pairs = []
		for f, attrs in m.items():
			size = attrs['size']
			t    = attrs['type']
			d    = attrs['data']

			if d:
				d = d.strip()

			if t == 'M':
				d = self.get_memo_data(d, is_base64=base64_memo)

				if nocase_in( '.'.join([self.get_tablename(),f]) ,decrypt_memo) \
				   or nocase_in(self.get_tablename() , decrypt_memo) :

					d = pwd_decrypt.decrypt(d, self._password)
			
			if  d.strip()  == '' or ord(d[0]) == 0 :
				d = None
				#import pdb
				#pdb.set_trace()

				
			if d:
				if dml_quoted['postgres'].find(t) >= 0:
					d = "'" + escape_q(d) + "'"

				if f.upper() not in NAME_CLASH:
					field = f.upper()
				else:
					field = "_"+f.upper()

				f_val_pair = ( field ,  d)
				f_val_pairs.append(f_val_pair)
		
		fields = ', '.join ( [fv[0] for fv in f_val_pairs] )
		vals  = ', '.join ( [ fv[1] for fv in f_val_pairs] )
		return " ".join( ['insert into ', self.get_tablename(), '(',fields, ')', 'values', '(', vals, ')' ] ) 

	
	def get_memo_data(self, offset_in_blocks, blocksize = 32, is_base64 = False):
	
		if self._memogetter == None:
			fn = os.path.splitext(self._filename)[0]
			fn = fn + '.FPT'
			if not os.path.exists(fn):
				fn = fn + '.fpt'

			self._memogetter = MemoGet(fn)
		
		memo = offset_in_blocks.strip()
		if memo == '':
			return memo

		try:	
			memo = self._memogetter.get_base( long(offset_in_blocks))	
			#import pdb
			#pdb.set_trace()
			if is_base64 and  compressed_base64:
					#also check if a zip file, and if not, convert memo2 to base64 zipfile
					fname = self._memogetter.get_zip_filename(memo)
					if not fname:
						# then zip it up
						s = StringIO.StringIO()
						z = zipfile.ZipFile(s,'w')
						z.writestr(str(offset_in_blocks).strip(), memo)
						z.close()
						memo = s.getvalue()
						memo2 = base64.encodestring(memo)
					else:
						# already in zip formate
						memo2 = base64.encodestring(memo)	
					memo = memo2

			elif is_base64 and not compressed_base64:
					fname = self._memogetter.get_zip_filename(memo)
					if fname:
						# unzip memo  
						s = StringIO.StringIO(memo)
						z = zipfile.ZipFile(s, 'r')
						memo = z.read(fname)
				
					memo = base64.encodestring(memo)
					
						
		except:
			print "offset_in_blocks =", offset_in_blocks , " should be long "
			print sys.exc_info()[0]
			traceback.print_tb(sys.exc_info()[2])

		
		return memo		
		
	
	def get_tablename(self):
		tablename = os.path.splitext( os.path.basename(self._filename) )[0]
		if tablename.upper() in NAME_CLASH:
			tablename = '_'+tablename

		return tablename
	
	def get_tablename_raw(self):
		tablename = os.path.splitext( os.path.basename(self._filename) )[0]
		return tablename
		
def save_ddl(pp):
	fn = raw_input('enter filename to save ddl:')
	f = file(fn, 'w')
	for p in pp.values():
		f.write(p.get_ddl_sql())
		f.write(';')
		f.write('\n')
	
	f.close()


if __name__ == "__main__":
	if len(sys.argv) == 1:
		print
		print "usage :\n\tpython "+sys.argv[0]+" src-dir -dsn <dbapi-dsn> -dbapi <dbapi python module name>  -create -data -from <tablename> -only tablename1,tablename2,tablename3 -memobase64 tablename4,tablename5 -decrypt tablename6,tabename7.field1 \n\n\t  where src-dir is the base directory of the dbf files  "
		print "\t -dsn <dsn>  use a dbapi connect dsn"
		print "( dsn format is  'host:port:database:user:pass'"
		print " dsn examples:"
		print "\t 'localhost::test1:testuser:password'     -  uses default port"
		print "\t '::test1:testuser:'            -  is default host, port, password "
		print ")"
		print
		print '\t -dbapi  <dbapi module> - selects particular db module to use e.g. pyPgSQL, psycopg '
		print
		print '\t -create: create database using dbapi'
		print
		print '\t -data:   load database with dbapi' 
		print
		print '\t -from <tablename>  : if an upload was interrupted , then all the data in table will be deleted, and postgres uploading resumes from the tablename ( currently dumping is per table). '
		print
		print '\t -only <comma separated list of tables>  - only insert these tables.'
		print
		print '-memobase64 <comma separated list of tables with memo fields requiring base64 encoding>'
		print '               memo fields will be stored as base64 encoded zip files. this is mainly for image data'
		print
		print '\t -decrypt  table,table.field  - decrypts all memo fields in a table, or if table.field specified, that memo field in the table.\n Uses a file pass.txt which holds the password. '
		
		print

		print "-base64tablename  substring1,substring2 -  requires a comma separated list of tablename substrings , where any tablename containing that substring has all its memo fields converted to base64"
		print
	arguments =[]
	arguments.extend(sys.argv)

	f = file('config.txt', 'r')
	for l in f:
		if l.strip() > 0 and l.find('=') > 0 and l.strip()[0] <> '#':
			words = l.split('=')
			words[0] = '-'+words[0]
			arguments.extend(words)
		

	if len(arguments) > 2 and arguments[2] == '-f':
		p = Parser(arguments[1])
		index = 1
		while 1:
			data, m = p.next()
			if not data:
				break
			print "REC_NO", index

			for k,x in m.items():
				print k,x
			print
			index += 1

	if len(arguments) > 3 and arguments[2] == '-i':
		field = arguments[3]
		print
		print 
		print p.get_index( field)	
			
	filedir = arguments[1]
	
	files = os.listdir( filedir)
	pp = {}
	for f in files:
		print f
		if f[-3:] == 'DBF':
			p = Parser(os.path.join(filedir,f))
			pp[p.get_tablename()] = p

	for k,p in pp.items():
		sql = p.get_ddl_sql()
		print
		print sql


	chosen_dbapi = None
	if '-dbapi' in arguments:
		i = arguments.index('-dbapi')
		chosen_dbapi = arguments[i+1]

	dbapi = None
	if '-dsn' in arguments:
		dsn = None
		if len(arguments) > 2 :
			dsn = arguments[3]
			
		if not dsn:
			print "ENTER the connection dsn for dbapi e.g. host:port:database:user:pass "
			dsn = raw_input()
		
		dbapi_mods =[ 
			('pyPgSQL.PgSQL', 'pyPgSQL', None ) , 
			('psycopg','', psycopg_dsn), 
			('pygresql','', None) 
			]	
			
		for m , from_package, convert_dsn  in dbapi_mods:
			try:
				if not chosen_dbapi or m.find(chosen_dbapi) >= 0:
					
					dbapi = __import__(m, globals(), locals(), from_package)
					if convert_dsn:
						dsn = convert_dsn(dsn)
					break
			except:
				print m, " import failed"

			
	if not dbapi:
		save_ddl(pp)
		sys.exit(-1)
	print dsn	
	c = dbapi.connect(dsn)
	cu = c.cursor()

	def create_tables():
		for p in pp.values():
			print "executing ", p.get_ddl_sql()
			try:
				cu.execute( p.get_ddl_sql() )
				c.commit()
			except Exception, msg:
				print msg
				traceback.print_tb(sys.exc_info()[2])
			


	if dbapi and '-create' in arguments:
		create_tables()

	print 
	print "Doing INSERTS"
	print

	memo_base64_list = [] 
	if '-memobase64' in arguments:
		i= arguments.index('-memobase64')
		try:
			memo_base64_list = [ x.strip().lower() for x in arguments[i+1].split(',')]
		except:
			print "-memobase64 requires a comma separated list of tables whose memo fields are stored base64"
			sys.exit(-1)
	
	if '-base64tablename' in arguments:
		i = arguments.index('-base64tablename')
		try:
			base64_default_substring.extend( [ x.strip().lower() for x in arguments[i+1].split(',')])
		except:
			print "-base64tablename requires a comma separated list of tablename substrings , where any tablename containing that substring has all its memo fields converted to base64"
			sys.exit(-1)

	only_tables = None
	if '-only' in arguments:
		i = arguments.index('-only')
		try:
			only_tables = arguments[i+1].split(',')
		except:
			print "-only requires a comma separated list of tables to insert only, other tables ignored."
			sys.exit(-1)
	decrypt_memo_tables = []
	if '-decrypt' in arguments:
		i = arguments.index('-decrypt')
		try:
			decrypt_memo_tables = arguments[i+1].split(',')
		except:
			print '-decrypt  followed by comma-separated list of tables'
	
	resume_from = None
	if '-from' in arguments:
		i = arguments.index('-from')
		try:
			resume_from = arguments[i+1]
			print "Deleting entries in table ", resume_from
			cu.execute('delete from '+resume_from)
			c.commit()
			print
			print "resuming from ", resume_from
			print
		except:
			print '-from <tablename> where tablename is where resume continues'
			resume_from = None
			
	if dbapi and  '-data' in arguments:
		# just in case some missing
		create_tables()
		for p in pp.values():
			
			print p.get_tablename()

			if only_tables and not nocase_in( p.get_tablename_raw() , only_tables):
				print "SKIPPING ", p.get_tablename_raw()
				continue

			if resume_from and not nocase_in( p.get_tablename_raw() ,[ resume_from]):
				print "skipping ", p.get_tablename_raw()
				continue
			else:
				resume_from = None

			print "INSERTING TABLE", p.get_tablename_raw()
			is_base64_memo = nocase_in( p.get_tablename_raw(),  memo_base64_list)
			if not is_base64_memo:
				normalized_tablename =  p.get_tablename_raw().strip().lower() 
				for x in base64_default_substring:
					x = x.strip().lower()
					if  normalized_tablename.find(x) >= 0:
						is_base64_memo = True
						break	
						
			print " tablename", p.get_tablename_raw() , " is base64_memo =", is_base64_memo
			
			while 1:
				#import pdb
				#pdb.set_trace()

							
				stmt = p.next_sql_insert( base64_memo= is_base64_memo, decrypt_memo = decrypt_memo_tables)
				if not stmt:
					break
				#print "executing ", stmt
				#sys.stdout.write(str(p._recno)+' ')
				sys.stdout.write('.')
				try:
					cu.execute(stmt)
					c.commit()
				except Exception, msg:
					
					print "SQL error? "
					print stmt[:100]
						
					print msg
					traceback.print_tb(sys.exc_info()[2])

					#import pdb
					#pdb.set_trace()
					try:
						c.rollback()
						cu = c.cursor()
					except:
						print "rollback failed"

					

	sys.exit(1)	
	

