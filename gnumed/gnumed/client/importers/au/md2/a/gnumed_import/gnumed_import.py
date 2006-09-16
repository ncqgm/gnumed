"""
Copyright (C) 2006  author 

    This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
	    the Free Software Foundation; either version 2 of the License, or
	        (at your option) any later version.

		    This program is distributed in the hope that it will be useful,
		        but WITHOUT ANY WARRANTY; without even the implied warranty of
			    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
			        GNU General Public License for more details.

"""			

import sys
import string
import rtf2plain 
import base64
import zipfile
import StringIO

REASON_DOC_ENCOUNTER="document auto import AU_type_a_v_01"
URNO_ISSUER = "dbf importer type au-md v0.1"
URNO_TYPE = "ur_no"
def usage():
	print "*** USAGE:  ***"
	print "These conditions have to be met:-"
	print "- the source md2 database needs to be exported using something that converts dbf to postgres"
	print "   ../dbf_2_pg/   has python scripts for doing this." 
	print
	print "- gm-dbo must be allowed to access the source database ,"
	print "  for example,  logging into 'test1', the exported dbf-to-postgres database  as user 'postgres' ,"
	print "  and doing 'GRANT all on database test1  to \"gm-dbo\"'"
	
	print
	print "- postgres must login to database gnumed_v2 and GRANT CREATEROLE to gm-dbo "
	print "  by doing"
	print
	print "       update pg_catalog.pg_authid set rolcreaterole=true where rolname = 'gm-dbo';"
	print
	print "EXAMPLE USAGE:"
	print
	print """python gnumed_import.py -from localhost::test1:any-doc:any-doc   -to localhost::gnumed_v2:gm-dbo:gm-dbo """
	print """
	The above means "import from  postgresql database 'test1' using user any-doc with password any-doc, 
	into the target database 'gnumed_v2' which is a version 2 gnumed database, also on postgresql, 
	using the login gm-dbo password gm-dbo
	"""

	print "dsn is a comma separated string of the form   host:port:database:user:password "
	print "the argument for -from specifies a dsn where there is a postgres store of dbf tables"
	print "the argument for -to  specifies a dsn where ther is a gnumed_v2 postgres store"
	print
	print "other arguments are:"
	print "\t -start ur_no,  start processing from this ur_no"
	print "\n\t -nodemo , don't import demographics (still requires patient and dr tables in source database)"
	print"\n\t -noprogress, don't import or clean progress and history notes"
	print"\n\t -nodocs, don't import documents"
	print"\n\t -nopath , don't import pathology."
	print
	print """example :  to import only the pathology after a partial load, 
		python gnumed_import.py -from localhost::test1:any-doc:any-doc   -to localhost::gnumed_v2:gm-dbo:gm-dbo /
			-nodemo -noprogress -nodocs

		"""
		
		

	print "this script is fairly simple, and will need to be maintained whenever mappings from the dbf to gnumed_v2 change"
	
	
def get_dbapi(dbapi_n):
	"""gets a named dbapi, or tries a list of other dbapi if this fails. Returns the dbapi module"""
	dbapi_tab = { 
		'psycopg': ('psycopg'		,		''),
		'pyPgSQL': ('pyPgSQL.PgSQL'	, 	'pyPgSQL'),
		'pygresql': ('pygresql'		, 	'')
		}
	
	others = dbapi_tab.keys()
	others.remove(dbapi_n)
	
	l = [dbapi_n] + others
	dbapi = None
	for api_name in l:
		module_n, mod_parent = dbapi_tab[api_name]
		try:
			# __import__ returns the topmost package in the module path module_n, unless mod_parent is specified
			# in which case mod_parent acts as the xxx.yyy parameter in the statement 'from xxx.yyy import zzz'
			# so that module xxx.yyy.zzz is returned.
			
			dbapi = __import__(module_n, globals(), locals(), mod_parent)
			break
			
		except:
			print module_n , " from ", mod_parent , " not found"
	return dbapi


#for normalization of birthdate , as this is required in gnumed_v2 in order to insert an identity.
DEFAULT_BIRTHDATE = '1-1-1960'

# flags for partial loading
nodemo,nopath,noprogress, nodocs = False, False, False, False

#for finding the pg_user for the dr_id
global_dr_id_to_pg_user= {}
global_dr_orig_to_pg_user = {}
#confrom is the connection to a dumped dbf to postgres database, which has the source data.
#conto is the connection to a gnumed_v2 database, which will take the converted data.
confrom = None
conto = None
global orig_user
orig_user = 'gm-dbo'

quotes = "\" \' \`".split(' ')
def esc(s):
	"""this function escapes text input, so that internal string quotes won't end a single quoted format string field"""
	s = str(s)
	l = []
	for x in s:
		if not x in string.printable:
			continue
		if x in quotes:
			l.append('\\')
		if x == '%' : l.append('%')
		l.append(x)
	return ''.join(l)

#---------------------------------------------------


class pg_importer:
	"""an importer that reads from a postgresql imported dbf database"""
	def __init__(self, pat_block=100):
		"""object indirection to allow for direct dbf importer"""
		self.cu = confrom.cursor()
		self.patcount = update_patcount(self.cu)	
		self.first_pat = 0
		self.pat_block = pat_block
		self.demo_stmt = 'select ur_no, title, firstname, knownas, surname, sex, dob, decdate, deceased, address, city, postcode, phone, bus_phone, mob_phone,   mc_no, mc_index, mc_expiry, pens_no, dva_no, update from patients order by ur_no offset %d limit %d'

		self.background = {}
		self._setup_progress_index()
		self._setup_document_index()

	def _setup_progress_index(self):
		cu = self.cu
		stmt = "select count(*) from pg_indexes where indexname = 'idx_urno_progress'"
		cu.execute(stmt)
		[n] = cu.fetchone()
		if n == 0:
			stmt = "create index  idx_urno_progress  on progress using btree (ur_no)"
			print stmt
			cu.execute(stmt)

	def _setup_document_index(self):
		cu = self.cu
		stmt = "select indexname from pg_indexes where indexname = 'idx_urno_document'"
		cu.execute(stmt)
		if not cu.fetchone():
			confrom.commit()
			stmt = "create index idx_urno_document on document using btree (ur_no)"
			print stmt
			cu.execute(stmt)
			i =0 
			while True:
				i += 1
				tablename = 'doc%05d' % i
				stmt = "select tablename from pg_tables where lower(tablename) = '%s'" % tablename
				cu.execute(stmt)
				if not cu.fetchone():
					break

				stmt = "create index idx_recno_%s on %s using btree( rec_no) " % ( tablename, tablename)
				cu.execute(stmt)

			confrom.commit()
		

	def get_drs(self):

		stmt = """
		select dr_no, dr, 
				sex,dob, 
				phone, fax, email, 
				reg_no, prov_no, pres_no, 
				drcode as worktime_cat, category 
		from dr
		"""

		self.cu.execute(stmt)

		r  = self.cu.fetchall()
		print "**DEBUG**"
		print r
		return r	

		
	def get_next_demographics(self):
		if self.first_pat > self.patcount:
			return None
		stmt = self.demo_stmt % ( self.first_pat, self.pat_block)
		self.cu.execute(stmt)
		rows = self.cu.fetchall()
		self.first_pat += self.pat_block
		return rows

	def get_progress_notes(self, ur_no):

		stmt = """
		select dr_no ::int, 
				notes, exam, history, 
				reason, reasoncode, 
				visitdate, starttime, endtime, update 
				from 
					progress 
				where 
					ur_no = '%s' 
				order by 
					visitdate, starttime
					
				""" % esc(ur_no) 
		self.cu.execute(stmt)
		return self.cu.fetchall()

	def get_patient_history(self, ur_no):
		cu = self.cu
		stmt = """
		select dr_no ::int , delcode, month, year, condition, comment, update, side, active, hide , histcode ,
		case when ( month is null or length(btrim(month)) = 0) and length(btrim(year)) = 4 
			then ('01-01-'||replace(year, 'O', '0') ) ::date 
		 when length(month) > 8 then 
			to_date ( month, 'dd/MM/YYYY')
		else 
			 now() 
		end as date_noted
		from history where ur_no = '%s' order by year, month, update, dr_no, condition
		"""	
		real_stmt  = stmt % esc( ur_no)
		cu.execute(real_stmt)
		rows = cu.fetchall()
		return rows

	def get_allergies(self, ur_no):
		""" returns  [  dr_no, item ( drug), type ( reaction) , delcode ( deleted ?) , update ( date in YYYYMMDD of entry) ] """
		cu = self.cu
		stmt = """
			select dr_no::int, item , type, delcode, update from reaction where ur_no = '%s' 
			"""  % esc( ur_no)

		cu.execute ( stmt )
		return cu.fetchall()

	def get_all_background(self, ur_no):
		if self.background.has_key(ur_no):
			return self.background[ur_no]
		del self.background
		self.background = {}

		cu = self.cu
		stmt = """
			select allergy , warnings, married, fh, social, occupation, smoking, smokes, ceased, started, smokingex, alcoholex, alcohol from allergy where ur_no = '%s'
			""" % esc( ur_no)
		cu.execute(stmt)
		r = cu.fetchone()
		if r and len(r) == 13:
			self.background[ur_no] = r
			#[allergy, warnings, married, fh, social, occupation, smoking, smokes, ceased, started, smokingex, alcoholex, alcohol ] = r
			return r
		else:
			return None
		

	def is_nka( self, ur_no):
		bcgk = self.get_all_background(ur_no)
		if not bcgk:
			return False
		allergyblock = bcgk[0] 
		allergyblock = allergyblock[1:-1].split(',')
		if allergyblock[1] == '"Nil known"':
			return True
		else:
			return False
	

	def get_family_hx(self, ur_no):
		bcgk = self.get_all_background(ur_no)
		if not bcgk:
			return None
		return bcgk[3]
	
	def get_social_hx(self, ur_no):
		bcgk = self.get_all_background(ur_no)
		if not bcgk:
			return None
		return bcgk[4]

	def get_occupation(self, ur_no):
		bcgk = self.get_all_background(ur_no)
		if not bcgk:
			return None
		return bcgk[5]
		
	def get_smoking(self, ur_no):
		bcgk = self.get_all_background(ur_no)
		if not bcgk:
			return None
		return bcgk[6:11]
	
	def get_alcohol(self, ur_no):
		bcgk = self.get_all_background(ur_no)
		if not bcgk:
			return None
		return bcgk[11:]
		

	def get_specialty(self):
		stmt ="select distinct specialty from spec"
		cu = self.cu
		cu.execute(stmt)
		return cu.fetchall()

	def get_specialists(self):
		stmt = """
	select company , title, firstname, surname, address1, address2, address3, postcode, phone, phone_ah, phone_mob, email, pager, fax, pubkey, nogap, update, sp_no from spec
		"""
		cu = self.cu
		cu.execute(stmt)
		return cu.fetchall()


	def get_letters(self, ur_no):
		cu = self.cu
		stmt = """
		select ur_no, spec, dr, letdate, delcode, subject, update , settings, item from letters
		where ur_no = ur_no
		""" % esc(ur_no)
		cu.execute(stmt)
		ll = []
		 
		for r in cu.fetchall():
			l = []
			l.extend(r[:-1])
			l.append( base64.decodestring(r[-1]) )
			ll.append(l)
		return ll	

	def get_documents(self, ur_no):
		stmt = """
		select ur_no, doc_no, page_no, file_no, rec_no, update, docdate , _desc , type, filetype  from document where ur_no = '%s' order by doc_no, page_no
		""" % esc(ur_no)
		cu = self.cu

		cu.execute(stmt)
		desc = cu.fetchall()
		
		l = []
		for ur_no, doc_no, page_no, file_no, rec_no, update, docdate , _desc , type, filetype  in desc:
			l.append( [ ur_no, doc_no, page_no, file_no, rec_no, update, docdate , _desc , type, filetype ])

		
		return l

	def get_doc_content(self ,file_no, rec_no):
			cu = self.cu
			doc_obj_table = 'DOC%05d' % int(file_no)
			stmt = """
				select  item  from %s where rec_no = %d
				""" % ( doc_obj_table, int(rec_no) )
			print stmt
			cu.execute(stmt)

			r = cu.fetchone()
			if not r:
				return None
			return r[0]


	def get_pathol(self, ur_no):
			"""get the pathol result. labref is digit followed by a acronym for the test for pathology;
			for radiology , it may just be the labname.  resultid is just a long number,
			there are 5000 more labrefs than distinct labrefs, so labref may not change when
			a result replacing a previous result.  there are only 100 less distinct labids, so labids
			may be repeated only if received in duplicate , I'm guessing.
			reporttime is the minute in a 24 hour day the report is received (0 - 1440)

			"""

			stmt = """
				select ur_no, labname, labref, resultid, reqdate, reportdate, reporttime,testname, reporthead, reporttext, checkdate, checkedby, comment from pathol where ur_no = '%s' order by labref 
				""" % esc(ur_no)

			cu = self.cu
			cu.execute(stmt)
			return cu.fetchall()

#---------------------------------------------------
def insert_identity(cu, firstnames, surname, preferred,  dob, sex, title, dec_date):
	if dob is None:
		dob = ''
	# check for already existing identities
	stmt = "select  pk_identity from dem.v_basic_person where  coalesce('%s',dob ) between dob - '1 day'::interval  and   dob + '1 days'::interval and firstnames = '%s' and lastnames = '%s' " % ( dob, esc(firstnames), esc(surname) )

	cu.execute(stmt)
	rr = cu.fetchall()

	print "FOUND for ", stmt
	print rr

	# clean up duplicates 
	if len(rr) > 1:
		print "*" * 100 , "DUPLICATES FOUND, CLEANING"
		xfk = []
		for r in rr:
			# this redundant mapping may change 
			stmt = "select xfk_identity from clin.xlnk_identity where xfk_identity = %d" % r[0]
			cu.execute(stmt)
			x = cu.fetchone()
			if x:
				xfk.append(x[0])

		for fk in  xfk[1:] :
			stmt = """select h1.pk, h2.pk from clin.health_issue h1, clin.health_issue h2 where
			h1.id_patient = %d and h2.id_patient = %d and h1.description = h2.description"""
			stmt = stmt % ( fk, xfk[0] )
			cu.execute(stmt)
			for oldhi, newhi in cu.fetchall():
				stmt = "update clin.episode  set fk_health_issue = %d where  fk_health_issue =%d " 	% (newhi, oldhi )
				cu.execute(stmt)
				stmt = "delete from clin.health_issue where pk = %d " % oldhi
				cu.execute(stmt)

			stmt = "select xfk_identity from blobs.xlnk_identity where xfk_identity = %d" % xfk[0]
			cu.execute(stmt)
			if not cu.fetchone():
				stmt = "insert into blobs.xlnk_identity(xfk_identity, pupic) values ( %d, '%d')" % ( xfk[0], xfk[0] )
				cu.execute(stmt)
	
			stmts = [   
						"update clin.health_issue set id_patient = %d where id_patient = %d",
						"update clin.episode set fk_patient = %d where fk_patient = %d",
						"update clin.encounter set fk_patient = %d where fk_patient = %d",
						"update blobs.doc_med set patient_id = %d where patient_id = %d"   ]

			for stmt in stmts:
				stmt = stmt % ( int(xfk[0]), int(fk) )
				print stmt
				cu.execute(stmt)

			for (table, field)  in [ 	('clin.health_issue','id_patient') , 
									('clin.episode','fk_patient')     , 
									('clin.encounter', 'fk_patient')  ,
									( 'blobs.doc_med',  'patient_id')  ]:
						stmt = "delete from %s where %s = %d" % ( table, field, int(fk))
						cu.execute(stmt)
		
		for r in rr[1:]:
			# since identity has cascade restricted on delete, just remove the name for the moment
			stmt = "delete from dem.names where id_identity = %d " % r[0]
			cu.execute(stmt)

		conto.commit()

	if len(rr):
		return rr[0][0]
	
	if sex:	
		stmt_insert_id = "insert into dem.identity( gender, dob) values( '%s', '%s')" % ( esc(sex.lower()[0]), esc(dob))   
	else:
		stmt_insert_id = "insert into dem.identity (dob) values( '%s') " % esc(dob)

		
	print stmt_insert_id

	cu.execute(stmt_insert_id)

	cu.execute("""select currval('dem.identity_pk_seq')""")
	[id] = cu.fetchone()

	stmt_names  = "insert into dem.names(id_identity, firstnames, lastnames, preferred ) values( %d,'%s' ,'%s', '%s')" % ( id, esc(firstnames), esc(surname), esc(preferred) )
	print stmt_names
	
	cu.execute(stmt_names)
	
	if title and len(title):
		stmt_title = "update dem.identity set title = '%s' where pk = %d" % ( esc(title), id)
		print stmt_title
		cu.execute(stmt_title)

	if dec_date and len(str(dec_date)):
		stmt_dec = "update dem.identity set deceased = '%s' where pk = %d"% ( esc(dec_date), id)
		print stmt_dec
		cu.execute(stmt_dec)
		
	
	return id

#---------------------------------------------------


def find_or_insert_exttype(cu, exttype, issuer):
	stmt = "select pk from dem.enum_ext_id_types where name = '%s' and issuer = '%s' " % (esc(exttype), esc(issuer)) 
	print stmt
	cu.execute(stmt)
	r = cu.fetchone()	
	if not r or r == []:
		print "external type ", exttype, " not found. Inserting it"
		stmt ="insert into dem.enum_ext_id_types( name, issuer) values ('%s', '%s')" % (esc(exttype), esc(issuer))
		print stmt
		cu.execute(stmt)
		cu.execute("select max(pk) from dem.enum_ext_id_types")
		[pk_exttype] = cu.fetchone()
		print "the pk_exttype is ", pk_exttype
	else:
		[pk_exttype] = r

	return pk_exttype


#---------------------------------------------------
def find_ext_id(cu,  exttype, issuer,  text, firstnames, lastnames, dob):
	"""finds the external id pk """
	if dob is None:
		dob = 'i.dob'
	else:
		dob = "".join(["'",esc(dob),"'"])

	pk_exttype = find_or_insert_exttype( cu,  exttype, issuer)
	stmt = """
	select l.id from dem.names n, dem.identity i, dem.lnk_identity2ext_id l 

		where 
			n.firstnames = '%s' and n.lastnames = '%s' 
		and 
		(to_char(i.dob,'YYYYMMDD') 
		= to_char(%s::date, 'YYYYMMDD')  or i.dob between %s::date - '1 day'::interval and %s::date + '1 day'::interval )
		and l.external_id = '%s' and l.fk_origin = %d and l.id_identity = i.pk and n.id_identity = i.pk
""" % ( esc( firstnames), esc( lastnames), dob, dob,dob, esc( text), pk_exttype )
	print stmt
	cu.execute(stmt)
	r = cu.fetchone()
	return r and r[0] 



def insert_ext_id(cu, id, exttype, issuer , text):
	pk_exttype = find_or_insert_exttype(cu, exttype, issuer)
	stmt = "select id from dem.lnk_identity2ext_id where id_identity = %d and fk_origin = %d and external_id = '%s' " % (  id, pk_exttype, esc(text) )
	cu.execute(stmt)
	if cu.fetchone():
		print "*" * 50, " external id ", esc(text), " already found for id_identity ", id
		return True

	stmt = "insert into dem.lnk_identity2ext_id ( id_identity, fk_origin, external_id) values (%d, %d, '%s') " % ( id, pk_exttype, esc(text) )  
	print stmt
	cu.execute(stmt)

	return True
	

#---------------------------------------------------
def process_dr( dr_id, dr, sex,dob, phone, fax, email , reg_no, prov_no, pres_no, worktime, cat):
	print dr, sex, dob, phone, fax, email , reg_no, prov_no, pres_no, worktime, cat
	
	dr = dr.upper()
	names = dr.split(' ')
	
	if len(names) and  names[0][-1] == '.':
		names[0] = names[0][:-1]
	title = ''
	if len(names) and names[0] in ['DR', 'MR', 'MS', 'MISS' , 'PROF']:
		title = names[0]+'.'
		names = names[1:]
	print "names", names
	surname = names[-1]
	firstnames = ' '.join(names[:-1])
	print "first, sur", firstnames, surname
	
	username = '-'.join([firstnames] + [surname])

	global_dr_id_to_pg_user[int(dr_id)] = username

	global_dr_orig_to_pg_user[dr] = username

	print '*' * 100
	print "added to drid to pg_user ", dr_id, username
	print '*' * 100
	print
	
	cu = conto.cursor()
	cu.execute('begin')
	cu.execute("select upper(firstnames), upper(lastnames) from dem.v_staff")
	r = cu.fetchall()
	found = False
	for [fn, ln] in r:
		if str(fn).find(firstnames)>=0 and str(ln).find(surname) >=0:
			found = True
			break
	if found:
		print "skipping insert of ", firstnames, surname, " as already in dem.v_staff"
	else:
		if not dob:
			dob = DEFAULT_BIRTHDATE
		id = insert_identity ( cu, firstnames, surname,'', dob,sex , title, '')

		ext_ids = [ 	( 'HIC', 'Provider No.' , prov_no), 
				('HIC', 'Prescriber No.', pres_no),
				('Med Prac.Board of Vic.', "Registration No.", reg_no)
				]

		for issuer, exttype, number in ext_ids:
			if number and len(number):
				insert_ext_id( cu, id,  exttype, issuer, number)


		group = "gm-doctors"

		stmt = """select count(*) from pg_roles where rolname='%s'""" % esc(username)
		cu.execute(stmt)
		[n] = cu.fetchone()
		if n == 0:
			# need the check as dropping the database doesn't remove previously created roles
			stmt = """create user "%s" nologin in group "%s" """ % ( esc(username) , group)
			print stmt
			cu.execute(stmt)


		rolename = "doctor"
		stmt_insert_staff = "insert into dem.staff( fk_identity, fk_role, db_user, short_alias ) values ( %d, (select pk from dem.staff_role where name = '%s' ) , '%s', '%s') "  % ( id, rolename, username, username[0] + username.split('-')[-1]) 
		cu.execute(stmt_insert_staff)
		
		stmt_getstaff_id = "select currval('dem.staff_pk_seq')"
		cu.execute(stmt_getstaff_id)
		[id_staff] = cu.fetchone()
	
		

	
#-----------------------------------

def transfer_drs():
	for row in importer.get_drs():
		process_dr(*row)


#-----------------------------------
#-----------------------------------
id_related = 0

def setup_id_related(cu):
	
	stmt = "select count(description) from dem.relation_types where description = 'unspecified related'"
	cu.execute(stmt)
	[yes] = cu.fetchone()
	if not yes:
		stmt = "insert into dem.relation_types ( biological, biol_verified, description) values ( false,false,'unspecified related')"
		print stmt
		cu.execute(stmt)
		
		stmt = "select max(id) from dem.relation_types"
		
		cu.execute(stmt)
		[id_related] = cu.fetchone()
		
		stmt = "update dem.relation_types set inverse = %d where id = %d " % (id_related, id_related)
		cu.execute(stmt)

#-----------------------------------


pk_urno= 0

def setup_urno_ext_type(cu):
	global pk_urno
	res = None
	while not res or res == []:
		stmt = "select pk from dem.enum_ext_id_types where name = '%s' and issuer = '%s'"%(URNO_TYPE , URNO_ISSUER)
		cu.execute(stmt)
	 
		res = cu.fetchone()
		if not res or res == []:
			stmt_insert_urno_type = "insert into dem.enum_ext_id_types ( name, issuer) values (URNO_TYPE, '%s') " % URNO_ISSUER
			cu.execute(stmt_insert_urno_type)
			res = None


	pk_urno = res[0]
	print "pk_urno = ", res[0]
			
	
	
#-----------------------------------
def setup_transfer_patients_conditions():
	cu = conto.cursor()
	cu.execute('set datestyle to DMY')
	setup_id_related(cu)
	setup_urno_ext_type(cu)
	
	




#-----------------------------------
#-----------------------------------

def find_or_insert_address(cu, id, no, st, urb, pcode) :
	st = esc(st)
	urb = esc(urb)
	no = esc(no)
	if urb.find('MT') == 0 and urb[2] in ['.',' '] and len(urb) >= 4:
		urb = 'MOUNT ' + urb[3:]
		
		
	stmt_state = "select code, country from dem.state s, dem.urb u where u.name ilike '%s' and u.postcode ilike '%s' and u.id_state = s.id" % (urb , pcode)
	print stmt_state
	cu.execute(stmt_state)
	result = cu.fetchone()
	if not result:
		return False
	[statecode, countrycode] = result
	
	stmt_insert_address = "select dem.create_address( '%s', '%s', '%s', '%s', '%s', '%s' ) " % ( no, st, pcode, urb, statecode, countrycode )
	print stmt_insert_address
	cu.execute(stmt_insert_address)
	[id_address ] = cu.fetchone()
	stmt = "select id from dem.lnk_person_org_address where id_identity = %d and id_address = %d " % ( id, id_address)
	cu.execute(stmt)
	if cu.fetchone():
		return False

	stmt_insert_lnk_id_address = "insert into dem.lnk_person_org_address( id_identity, id_address, address_source) values ( %d, %d, 'import program')" % (id, id_address)
	print stmt_insert_lnk_id_address
	cu.execute(stmt_insert_lnk_id_address)
	 
	
	return True


related_map = {}


def find_patient( row):
	ur_no , firstname, surname, dob = row[0], row[2], row[4], row[6]
	cu = conto.cursor()
	pk_urno = find_ext_id( 	cu, URNO_TYPE, URNO_ISSUER, ur_no, firstname, surname, dob)
	print "DEBUG pk_urno, urno_type, urno_issuer, ur_no", pk_urno, URNO_TYPE, URNO_ISSUER, ur_no

	cu.execute("select id_identity from dem.lnk_identity2ext_id where id = %d" % pk_urno)
	r = cu.fetchone()
	return r and r[0] 




def process_patient(  ur_no, title, firstname, knownas, surname, sex, dob, decdate, deceased, address, city, postcode, phone, bus_phone, mob_phone,   mc_no, mc_index, mc_expiry, pens_no, dva_no, update):

	print ur_no, title, firstname, knownas, surname, sex, dob, decdate, deceased, address, city, postcode, phone, bus_phone, mob_phone,   mc_no, mc_index, mc_expiry, pens_no, dva_no, update
	
	cu = conto.cursor()
	
	if not dob:
		dob = DEFAULT_BIRTHDATE
	
		
	if mc_no:
		mc_index = str(mc_index)
		mc_expiry = str(mc_expiry)
		medicare = " ".join( [mc_no ,mc_index, 'exp', mc_expiry] )
	else:
		medicare = None
		
		
	l =  [  ( URNO_ISSUER, URNO_TYPE, ur_no), 
		( "HIC", "Medicare",  medicare ),
		( "Centrelink", "CRN", pens_no ), 
		( "Department of Veteran's Affairs", "DVA", dva_no ) ]

				
	id = insert_identity (cu, firstname, surname, knownas, dob, sex, title, decdate )		
		

	for issuer, exttype, number in l:
		if number and len(number):
			if not find_ext_id(cu, exttype, issuer, number, firstname, surname, dob):
				insert_ext_id(cu, id,  exttype, issuer ,  number)
		
	#address normalize. rules 
	# if first token is U include in number
	# while token contains number , include in number
	# the rest of tokens of address go in street

	def has_digit(t):
		if not t:
			return False

		for x in t:
			if x in string.digits: 
				return True
		return False

	in_number = True
	if address:	
		words = address.split(' ')
		number_part  = []
		street_part = []
		in_number = True
		for i, w in enumerate(words):
			if i == 0 and w[0] in ['u', 'U'] or w.lower() in ['appt', 'flat', 'lot', 'block' ] :
				number_part.append(w)
				continue
			
			if in_number and has_digit(w) or not w.isalpha() or w.lower in ['appt', 'flat', 'unit', 'lot', 'block']:
				number_part.append(w)
				continue
			
			in_number = False
			street_part.append(w)

		if not	find_or_insert_address( cu, id, ' '.join(number_part), ' '.join(street_part), city, postcode):
			print "THIS ADDRESS NOT INSERTED , ? DUPLICATE ", id, number_part, street_part, city, postcode

	
	phones = [ 	('homephone', phone	),
			('mobile', mob_phone	),
			('workphone', bus_phone )
		 	]

	for medium , url in phones:
		if url:
			# call the function dem.link_person_comm

			stmt_comm = "select dem.link_person_comm(%d, '%s', '%s', true)" % ( id, esc(medium) , esc(url))
			cu.execute( stmt_comm)
		
	return id

def get_dr_user(dr_id):
	"""gets the postgres user created in process_dr associated with the dr_id
		so that progress notes and history appear with the author
	"""
	
	to_user = global_dr_id_to_pg_user
	#<DEBUG>
	#print
	#print to_user
	#print
	if dr_id is None:
		dr_id = 1
	pg_user = to_user.get(int(dr_id), None)

	if not pg_user:
		pg_user = 'default'
	else:
		pg_user ="'"+esc(pg_user) + "'"

	print "*"*20, "pg_user is ", pg_user	
	
	return pg_user
#-------------------------------------------------
def clean_progress_notes(cu, id_patient):
	""" clean up duplicate encounters or duplicate episodes of a health issue
	"""

	"""to clean up  duplicate encounters , sequentially search the encounters
	for matching encounters. 
	"""
	stmt = "select distinct to_char(started,'YYYYMMDD')  from clin.encounter where fk_patient = %d" % id_patient
	cu.execute(stmt)
	rr = cu.fetchall()
	deletable_epi = []
	tables = ['blobs.doc_med', 'clin.clin_aux_note', 'clin.test_result', 'clin.lab_request', 'clin.clin_medication', 'clin.vaccination', 'clin.allergy', 'clin.clin_hx_family' ]
	for [started] in rr:
			stmt = "select pk from clin.encounter where fk_patient = %d and to_char(started,'YYYYMMDD') = '%s' order by pk" % ( id_patient, started)
			cu.execute(stmt)
			rr2 = cu.fetchall()
			if len(rr2) > 1:
				# possible duplicate encounters  found, they have the same start date
				duplicated_pk=[] 
				seen_narrative = {}

				"""go through the encounters, and find the sum of the md5 for the narratives for each encounter,
				and store this signature with the pk. If the signature is already in there,
				then the pk is aduplicate pk.
				"""
				for [pk] in rr2:
					stmt = "select distinct md5(narrative) from clin.clin_narrative where fk_encounter = %d order by md5(narrative)" % pk
					cu.execute(stmt)
					rr3 = cu.fetchall()
					sig = "".join([str(x[0]) for x in rr3])
					if not sig in seen_narrative:
						seen_narrative[sig] = pk
					else:
						duplicated_pk.append((pk, sig))

				for pk , sig in duplicated_pk:
					base_pk = seen_narrative[sig]
					for t in tables:
						stmt = "update %s set fk_encounter = %d where fk_encounter = %d" % (t,base_pk, pk)
						print stmt
						cu.execute(stmt)

					stmt = "select fk_episode from clin.clin_narrative n where n.fk_encounter = %d" % pk
					cu.execute(stmt)
					
					deletable_epi.extend( [ x[0] for x in cu.fetchall() ] )

					stmt = "delete from clin.clin_narrative where fk_encounter = %d " % pk
					print stmt
					cu.execute(stmt)

					stmt = "delete from clin.encounter where pk = %d " % pk
					print stmt
					cu.execute(stmt)
				
	unique_deletable_epi = {}
	for x in deletable_epi:
		unique_deletable_epi[x] = 1

	for pk_epi in unique_deletable_epi.keys():
		deletable = True
		for t in tables:
			stmt = "select count(*) from %s where fk_episode = %d" % (t, pk_epi)
			cu.execute(stmt)
			[cnt_ref] = cu.fetchone()
			if cnt_ref  > 0:
				deletable = False
				break

		if deletable:
			stmt = "delete from clin.episode where pk = %d" % pk_epi
			cu.execute(stmt)
			
	stmt = "delete from clin.health_issue where not exists( select ce.pk from clin.episode ce where ce.fk_health_issue = clin.health_issue.pk  )  and id_patient = %d" % id_patient 
	cu.execute(stmt)

	stmt = "select ce.pk, description, (select count(*) from clin.clin_narrative where fk_episode =ce.pk) from clin.episode ce where ce.fk_health_issue in (select pk from clin.health_issue where id_patient = %d)" % id_patient
	cu.execute(stmt)
	deletable_pk= [ ce_pk for ce_pk, description, cnt_narr in cu.fetchall() if cnt_narr == 0]

	for pk in deletable_pk:
		sum_others =0
		for t in tables:
			stmt = "select count(*) from %s where fk_episode = %d" % (t,pk)
			
			cu.execute(stmt)
			sum_others += cu.fetchone()[0]
		if sum_others == 0:	
				stmt = "delete from clin.episode where pk = %d" % pk
				print stmt
				cu.execute(stmt)
	
			

def process_patient_progress(ur_no, id_patient):
	# progress note maps to an encounter and episode

	# TODO need to add modified_by to all inserts to use non-login users as well
	
	cu2 = conto.cursor()



	pnotes = importer.get_progress_notes(ur_no)

	

	
	map_time_to_episode = {}
	
	last_datepart = None

	for r in pnotes:
		dr_id, notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update = r

		#<DEBUG> statements for detailed dump
		#print "PROCESSING progress =\n notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update"
		#print notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update
	
		print "process progress notes ", reason, visitdate, starttime, " : UR_NO *** ", ur_no, " ***"


		"""
parse the visitdate and starttime into normalized
times.
		"""

		datepart = ''
		if visitdate and str(visitdate).strip() <> '':
			print "visit date is ", visitdate
			datepart = str(visitdate).split(' ')[0]

		if datepart.strip() == '':
			if   update and len (update.strip()) >= 8:
				datepart = '-'.join ( [ update[6:8] , update[4:6] , update[:4] ] )
			elif last_datepart:
				datepart = last_datepart
			else:
				datepart = '1-1-2005'
			
		last_datepart = datepart
		
		if starttime is None:
			starttime = "00:00:00"
	
		if starttime.find('.') >= 0:
			starttime = ":".join(starttime.split('.'))

		started = ' '.join( [ datepart, starttime]).strip()

		if endtime is None:
			endtime = starttime
		
		if endtime.find('.') >= 0:
			endtime = ":".join(endtime.split('.'))
		lastaffirmed = ' '.join( [ datepart, endtime ] ).strip()

		if not reason or reason.strip() == '':
			reason = 'xxxDEFAULTxxx'

		"""
check encounter exists. 
Encounter exists if same patient, same reason for encounter, same started , last_affirmed times.
If encounter exists then skip encounter creation ( also episode and narrative creation
		"""

		stmt = "select pk from clin.encounter where fk_patient = %d and reason_for_encounter = '%s' and  coalesce( '%s'::date, started ::date)  between started - '1 hour'::interval and started + '1 hour'::interval    and coalesce(  '%s' ::date, last_affirmed ::date) between last_affirmed - '1 hour'::interval and last_affirmed + '1 hour'::interval " % ( id_patient, esc(reason), esc(started),  esc(lastaffirmed) )

		print stmt
		cu2.execute(stmt)
		rr = cu2.fetchall()
		exists = False
		for r in rr:
			pk_enc = r[0]
			stmt = "select pk from clin.clin_narrative cn where cn.fk_encounter = %d union select pk from blobs.doc_med b where b.fk_encounter = %d" % (pk_enc, pk_enc)
			cu2.execute(stmt)
			r2 = cu2.fetchall()
			if len(r2) == 0:
				stmt = "delete from clin.encounter where pk = %d " % pk_enc
				cu2.execute(stmt)
			else:
				exists = False
			
		if exists:
			# skip as encounter already entered
			continue
		
		auth_stmt = "set session authorization %s" % get_dr_user(dr_id)
		print auth_stmt
		cu2.execute(auth_stmt)

		# create an encounter
		stmt = "insert into clin.encounter (  fk_patient, reason_for_encounter, started, last_affirmed) values ( %d, '%s', '%s', '%s')" % ( id_patient, esc( reason), esc(started), esc(lastaffirmed) )

		print stmt

		cu2.execute(stmt)
		stmt = "select max(pk) from clin.encounter"
		cu2.execute(stmt)
		[pk_encounter] = cu2.fetchone()

		#create an unlinked episode

		stmt = "insert into clin.episode (  fk_patient, description, is_open) values ( %d, '%s', false)" % ( id_patient, esc(reason))

		print stmt

		cu2.execute(stmt)

		stmt = "select max(pk) from clin.episode"
		cu2.execute(stmt)
		
		[pk_episode] = cu2.fetchone()

		map_time_to_episode[str(visitdate) +' '+ str(starttime)] = (pk_episode , started, lastaffirmed) 
		# this is for linking episode later if required
		
		notes2 = rtf2plain.rtf2plain(notes)
		
		"""
parse the notes into the s o a p  categories. The notes have the 
text headings History, Examination, Assessment, Action/ Management.
Result is stored in a map with keys s o a p, and this is then read in "s o a p" order
and inserted as clin_narratives
		"""


		state = 's'
		cat = { 's': [], 'o': [], 'a': [], 'p': [] }
		cats = []
		for x in notes2.split('\n'):
			x = x.strip()
			n = x.find('Diagnosis') 
			if n> 0:
				cat[state].append( x[:n] )
			if n >=0:
				x = x[n:]
				state = 'a'
			
			n = x.find('History')
			if n > 0:
				cat[state].append(x[:n])

			if n >= 0:
				if cat['s'] <> [] :
					score  = 0
					for k in [ 'o', 'a', 'p' ]:
						if cat[k] <> []:
							score += 1
					if score >= 2:  
						# assume the second __history is another problem ? 
						cats.append(cat)
						cat =  { 's': [], 'o': [], 'a': [], 'p': [] }

				x =x [n:]
				state = 's'
				
			n = x.find('Examination')
			if n > 0:
				cat[state].append(x[:n])
			if n >= 0:
				x = x[n:]
				state = 'o'
			
			n = x.find('Action')
			if n < 0:
				n = x.find('Management')
			if n < 0:
				n = x.find('Review')
				
			# read text upto Action, Management or Review, and set as previous state	
			if n > 0:
				cat[state].append(x[:n])

			# set next state to 'p'	
			if n >= 0:
				x= x[n:]
				state = 'p'
			cat[state].append(x)
				
		cats.append(cat)
		
		narratives = []

		for cat in cats:
			for k in ['s', 'o', 'a', 'p' ] :
				narratives.append( (k, '\n'.join(cat[k]) ))
		

		"""
Check the narratives do not already exist by selecting for a narrative with
the same encounter and same md5 sum of narrative text. If exists, skip insertion
of narrative.
		"""

		for (soap_cat, narrative) in narratives:
			if narrative.strip() == '':
				continue
			query = "select count(*) from clin.clin_narrative where fk_encounter = %d  and soap_cat = '%s' and md5(narrative) = md5('%s')"
			r_qry = query % ( pk_encounter,  soap_cat, esc(narrative) )
			cu2.execute(r_qry)
			[cnt] = cu2.fetchone()
			if cnt > 0:
				print "*" * 100
				print "duplicate narrative found"
				print "*" * 100
				print "skipping"
				print
				continue
			stmt = "insert into clin.clin_narrative( fk_encounter, fk_episode, clin_when, soap_cat, narrative) values ( %d,%d,'%s','%s', '%s') " % ( pk_encounter, pk_episode, esc(started),soap_cat,  esc( narrative) )

			#<DEBUG>
			print stmt
			cu2.execute(stmt)


			
	"""
group the progress notes by the reason specified.
if there are more than 1 progress notes for a reason, 
insert a health issue from the reason text.
	"""
	by_reason = {}
	noreason = "reason for encounter unspecified"
	# insert as unlinked episode, and encounter with narrative
	for r in pnotes:
		dr_id, notes, exam, history, reason, reasoncode, visitdate, starttime, endtime,update  = r
		#print "row is ", r
		if reason and len(reason.strip()):
			reason = reason.strip().lower()
			l = by_reason.get(reason, [])
			l.append(r)
			by_reason[reason] = l	
		else:
			l = by_reason.get( noreason, [])
			l.append(r)
			by_reason[noreason] = l

	for reason, pnotes in by_reason.items():
		# arbitrary, 3 visits for same reason consitutes a health issue
		if len(pnotes) > 1:
			stmt = "select pk from clin.health_issue where id_patient = %d and description = '%s'" %  ( id_patient, esc(reason))
			cu2.execute(stmt)
			result = cu2.fetchone()
			if result and len(result):
				pk_issue = result[0]
			else:
			# insert a health issue
				stmt = "insert into clin.health_issue( id_patient, description) values (%d, '%s')" % ( id_patient, esc(reason))
				print stmt
				cu2.execute(stmt)
			
				stmt = "select max(pk) from clin.health_issue"
				cu2.execute(stmt)
				[pk_issue] = cu2.fetchone()
			
			for r in pnotes:
				dr_id,notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update = r
				
				(pk_episode, started, lastaffirmed) = map_time_to_episode.get( str(visitdate) + ' '+str(starttime), (None,None,None) )
				if pk_episode:
					stmt = "update clin.episode set fk_health_issue = %d, fk_patient = Null where pk = %d " % (pk_issue,pk_episode)
					print stmt
					cu2.execute(stmt)

					
	cu2.execute("set session authorization '%s'" % esc( orig_user) )

	return map_time_to_episode			
			
def ensure_xlnk_identity(id_patient):
	cu2 = conto.cursor()
	# ensure clin.xlnk_identity for id_patient exists
	while 1:
		stmt = "select count(*) from clin.xlnk_identity where xfk_identity = %d " % id_patient
		print stmt
		cu2.execute(stmt)
		[n]  = cu2.fetchone()
		print n
		if n == 1:
			break
		if n == 0:
			stmt = "insert into clin.xlnk_identity( xfk_identity , pupic) values ( %d , '%d')" % ( id_patient, id_patient)
			print
			cu2.execute(stmt)
	
		if n > 1:
			print """this should never occur,  unique constraint "xlnk_identity_xfk_identity_key" """

	
def process_patient_history( ur_no, pat_id) :

	cu2 = conto.cursor()

	stmt = "select dob ::date from dem.identity where pk = %d" % pat_id

	cu2.execute(stmt)
	[dob] = cu2.fetchone()


	rows = importer.get_patient_history(ur_no)


	for (dr_id, delcode, month, year, condition, comment, update, side, active, hide, histcode, date_noted) in rows:
		# skip if no condition text

		if not condition or condition.strip() == '':
			continue
		
		# normalize date

		if date_noted is None or str(date_noted).strip() == '':
			date_noted = 'now()'
		else:
			date_noted = "'" + esc(date_noted) +"'"

		
		# check if condition already exists for patient
		query ="""
		select pk from clin.health_issue where id_patient = %d and description = '%s' 
			""" % ( pat_id, esc(condition) )
			
		cu2.execute(query)
		res = cu2.fetchone()

		# doesn't already exist, so insert
		if  not res:
		
			stmt = """
			insert into clin.health_issue ( 
				description,  modified_when, age_noted, laterality , is_active, is_confidential , id_patient
			) 
			values (
				'%s',  to_timestamp('%s', 'YYYYMMddhhmiss' ) , age ( %s, '%s' ) , 
				 case when '%s'='B' then 'sd'  
				 	  when '%s'='L' then 's'  
					  when '%s'='R' then 'd' 
					  else 'na' end ,
				'%s', '%s' , %d
			) 
				"""
			fk_health_issue = "currval('clin.health_issue_pk_seq')"
		else:
			# update, if already exists
			fk_health_issue = str(res[0])
			stmt = """
				update clin.health_issue set description='%s',  modified_when = to_timestamp('%s', 'YYYYMMddhhmiss' ) , 
				age_noted = age ( %s, '%s') ,
				laterality =  case when '%s'='B' then 'sd'
				                      when '%s'='L' then 's'
									                        when '%s'='R' then 'd'
															                      else 'na' end ,
				is_active = '%s', is_confidential = '%s' where id_patient = %d and description = 
				""" + "'" + esc(condition) +"'"
		
		# set the author to be the original author
		pg_user = get_dr_user(dr_id)
		auth_stmt = "set session authorization %s" % pg_user  # pg_user already quoted , or is CURRENT_USER
		cu2.execute(auth_stmt)
		
		real_stmt = stmt	%  ( esc( condition),   esc(update) , date_noted, dob, esc(side) , esc(side),esc(side) , active, hide , pat_id ) 
	
		print real_stmt
		cu2.execute(real_stmt)

		# insert condition comment as an episode of health issue where the dr made a comment
		if comment and comment.strip() <> '':
			
			stmt2 = """
				insert into clin.episode (  modified_when, fk_health_issue, description, is_open) values
				( 
				 to_timestamp('%s', 'YYYYMMddhhmiss'), %s, '%s', false
				) """ %  (  esc(update), fk_health_issue, esc('Comment on health issue:') )

		
			cu2.execute(stmt2)
			stmt3 = """
insert into clin.encounter (  fk_patient, reason_for_encounter, started, last_affirmed) values ( %d, '%s',  '%s', '%s')
					""" % ( pat_id, esc( 'auto' ), esc(date_noted), esc(date_noted) )

			cu2.execute(stmt3)

			stmt4 = """
				insert into clin.clin_narrative(  modified_when, fk_encounter, fk_episode, clin_when, soap_cat, narrative) values ( '%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'), '%s','%s', '%s') 	
				""" % ( esc(date_noted) , esc(date_noted) , 's', esc(comment) )
			
			cu2.execute(stmt4)
	
		# restore the session author to default
		cu2.execute("set session authorization '%s'" % esc( orig_user) )
	

def create_doc_encounter(cu2, pat_id):
				stmt = """
					insert into clin.encounter( fk_patient, reason_for_encounter, fk_type) 
					values (%d, '%s', 9)

				""" % ( pat_id, REASON_DOC_ENCOUNTER)
				
				cu2.execute(stmt)

				"""get the new clin encounter index"""

				stmt2 = """select max(pk) from clin.encounter"""

				cu2.execute(stmt2)
				[pk_encounter] = cu2.fetchone()
		
				return pk_encounter

def create_doc_episode(cu2, pat_id):
				"""create a new episode """

				stmt = """
					insert into clin.episode ( fk_patient, description)
					values ( %d, '%s')
				
				""" % ( pat_id, REASON_DOC_ENCOUNTER)

				cu2.execute(stmt)

				"""get the new clin episode index """

				stmt3 = """select max(pk) from clin.episode where fk_patient = %d """ % pat_id

				cu2.execute(stmt3)

				[pk_episode] = cu2.fetchone()
				return pk_episode

def ensure_blobs_xlnk_identity(cu2, pat_id):
				stmt = "select xfk_identity from blobs.xlnk_identity where xfk_identity = %d" % pat_id
				cu2.execute(stmt)

				if not cu2.fetchone():
					stmt = """
						insert into blobs.xlnk_identity ( xfk_identity, pupic) values ( %d, coalesce( (select pupic from dem.identity where pk = %d), '%d'::text) ) 
							"""
					stmt = stmt % ( pat_id, pat_id, pat_id)

					cu2.execute(stmt)

def get_intended_reviewer( cu2, db_user = None):
	if db_user:
		db_user = "'%s'" % db_user
	else:
		db_user = "current_user"

	cu2.execute("select pk from dem.staff where db_user = %s" % db_user)
	r = cu2.fetchone()
	if not r:
		cu2.execute('select pk from dem.staff where db_user = \'any-doc\'')
		r = cu2.fetchone()
	
	return r[0]


def process_patient_documents(ur_no, pat_id):
	print
	print '*' * 100
	print "DEBUG : processing patient documents", ur_no, pat_id
	print '*' * 100
	print
	docs = importer.get_documents(ur_no)
	last_doc_no = -1

	cu2 = conto.cursor()

	pk_staff = get_intended_reviewer(cu2) 

	ensure_blobs_xlnk_identity(cu2, pat_id)


	doc_pks = {}


 	for ur_no, doc_no, page_no, file_no, rec_no, update, docdate , _desc , type, filetype  in docs:

		# check if docobj doesn't already exist

		ext_ref = '/'.join([ur_no, str(doc_no)]) 

		stmt = """
		select pk from blobs.doc_med
		where 
			patient_id = %d
				and
			ext_ref = '%s'
		"""  %  ( pat_id, esc(ext_ref))

		cu2.execute(stmt)
		r = cu2.fetchone()
		if  r:
			doc_pks[doc_no] = r[0]


		
		if not doc_pks.has_key(doc_no):
				# create a new encounter and episode for the document
				# get new_doc_id
				# insert into blobs.doc_med  , patient_id, fk_encounter, fk_episode, type, comment, date, ext_ref
				# get last_doc_no
				pk_encounter = create_doc_encounter(cu2,pat_id)
				pk_episode = create_doc_episode(cu2, pat_id)

				"""get the date to be docdate, update, or now() , whichever is valid first in that order."""

				date = None
				if docdate:
					docdate = str(docdate).strip()
				if  docdate and docdate <> '' and len(docdate.split(' ')) == 2:
					date = docdate.split(' ')[0]
				if update:
					update = str(update).strip()
				if not date and update and update <> '' and len(update) >= 8:
					date = update[:8]

				if not date:
					date = 'now()'
				else: 
					date = "".join(["'",date,"'"])

				"""with the above data - pat_id, pk_encounter, pk_episode, description, date, and the
				external reference which is ur_no/document no. ,  create a new blobs.doc_med of type
				'referral report other'.
				"""


				stmt = """
				insert into blobs.doc_med ( patient_id, fk_encounter, fk_episode, 
						comment, date, ext_ref,
						type 
						)
				values
				( %d, %d, %d, 
					'%s', %s, '%s' ,
				(select pk from blobs.doc_type where name = 'referral report other')
				)
				""" %  ( pat_id, pk_encounter, pk_episode, 		esc(_desc), date, esc(ext_ref) ) 

				cu2.execute(stmt)

				cu2.execute('select max(pk) from blobs.doc_med where patient_id = %d' % pat_id)
				res = cu2.fetchone()
				if not res:
					print "NO DOCUMENTS FOR THIS PATIENT, ",pat_id, " ,  FAILURE ?"
					continue
				else:
					pk_doc = res[0]
					last_doc_no = doc_no

					doc_pks[doc_no] = pk_doc
		

			

		stmt = "select pk from blobs.doc_obj where doc_id = %d and seq_idx = %d" % ( doc_pks[doc_no], page_no )

		cu2.execute(stmt)

		pks = cu2.fetchall()

		if len(pks) == 1:
			print "*" * 50, " WARNING: doc object ", page_no, ext_ref, " already found. NOT INSERTED "
			continue

		elif len(pks) > 1:
			
			print "*" * 50, " WARNING: doc object ", page_no, ext_ref, " has  ",len(pks), " copies. ADDITIONAL COPIES DELETED. "
			
			stmt  = "delete from blobs.doc_obj where pk in  (%s) " % ",".join([str(x[0]) for x in pks[1:] ] )
			print stmt
			cu2.execute(stmt)

			continue

		elif len(pks) == 0:		
			text = importer.get_doc_content( file_no, rec_no)
			
			if not text:
				print "*" * 50, " NO document contents found for ", ext_ref, page_no
				continue

			"""assume text is base64 encoded. check after decoding if not zipped, then unzip."""
					
			decoded = base64.decodestring( text) 

			try:
				s = StringIO.StringIO(decoded)
				z = zipfile.ZipFile(s, 'r' )
				x = z.read( z.namelist()[0])
				decoded = x
			
			except:
				"""not a zipfile"""
				pass

			if _desc is None :
				_desc = ""

			# insert into blobs.doc_obj  , seq_idx, doc_id, data , fk_intended_reviewer ( dem.staff.pk )

			stmt = """ insert into blobs.doc_obj 
			( seq_idx, doc_id, fk_intended_reviewer, comment, data ) 
			values (  %d,  %d , %d , '%s', decode ( '%s', 'base64'))
				"""
			
			stmt = stmt % ( page_no, doc_pks[doc_no], pk_staff, esc(_desc), esc(base64.encodestring(decoded)) )

			cu2.execute(stmt)
		
			print "DEBUG successfully inserted doc_ob _desc, pk_doc,doc_no, page_no , ext_ref", _desc, doc_pks[doc_no], doc_no, page_no, ext_ref

	conto.commit()

def process_patient_pathol(ur_no, pat_id):
	
	results = importer.get_pathol(ur_no)

	cu2 = conto.cursor()



	ensure_blobs_xlnk_identity(cu2, pat_id)

	types = { 
				"discharge": "discharge summary other"	,
				"pathology" : "referral report pathology",
				"radiology" : "referral report radiology",
				"imaging" 	: "referral report radiology"
				}
	
	default_type = types["pathology"]

	curr_enc = None
	last_reportdate = None
	last_labname = None


	for ur_no, labname, labref, resultid, reqdate, reportdate, reporttime, testname, reporthead, reporttext, checkdate, checkedby, comment in results:
		
		# normalize labname
		ww = labname.split(' ')
		cnt_blanks = 0
		ww2 = []
		for w in ww:
			if w <> '':
				ww2.append(w.lower())
			else:
				cnt_blanks += 1
				if cnt_blanks > 4:
					#skip rest
					break
				else:
					ww2.append('')

		labname = ' '.join(ww2).strip()

		#get the doc_type
		doctype = None
		for w in ww2:
			if w in types:
				doctype = types[w]
				break
		if not doctype:
			doctype = default_type 
		
		#get to doc date
		for x in (reportdate, reqdate, '2010/01/01'):
			date = x
			if date:
				break
		
		date = str(date).split(' ')[0] + ' ' + '%02d:%02d' % ( reporttime/60 , reporttime % 60 )
		

		ext_refs = [ ('labname', labname), ('labref', labref),\
					('resultid', resultid), ('reqdate',reqdate),\
					('reportdate', reportdate), ('reporttime', reporttime),\
					('testname', testname ), ('checkdate', checkdate), ('checkedby', checkedby)\
					]
		ext_ref = '____'.join( [ '::'.join([k,str(v)]) for  k, v in ext_refs] )

		# check if ext_ref already exists
		stmt = "select pk from blobs.doc_med m where m.patient_id = %d and m.ext_ref = '%s'"
		stmt = stmt % ( pat_id, esc(ext_ref))

		cu2.execute(stmt)
		r=  cu2.fetchone()
		doc_med_pk = r and r[0]

		if not doc_med_pk and (not curr_enc or reportdate <> last_reportdate or labname <> last_labname) :
			pk_encounter = create_doc_encounter(cu2, pat_id)
			pk_episode = create_doc_episode(cu2, pat_id)
			last_labname = labname
			last_reportdate = reportdate

		if not doc_med_pk:
			stmt = """
				insert into blobs.doc_med ( patient_id, fk_encounter, fk_episode, 
						comment, date, ext_ref,
						type 
						)
				values
				( %d, %d, %d, 
					'%s', '%s', '%s' ,
				(select pk from blobs.doc_type where name = '%s')
				)
				"""
			stmt = stmt % ( pat_id, pk_encounter, pk_episode, esc(testname) + " :: "+ esc(labname), date, esc(ext_ref), doctype)

			cu2.execute(stmt)

			
		pk_staff = get_intended_reviewer(cu2, global_dr_orig_to_pg_user.get(checkedby.upper(), None) ) 

		if doc_med_pk:
			stmt = """update blobs.doc_obj 
set fk_intended_reviewer = %%d, comment = '%%s', data = '%%s' 
		where doc_id = %d and seq_idx=1""" % doc_med_pk 
		else:
			stmt = """ insert into blobs.doc_obj 
	( seq_idx, doc_id, fk_intended_reviewer, comment, data ) 
	values ( 1,   currval('blobs.doc_med_pk_seq') , %d , '%s', '%s')
			"""
		
		reporttext = "\n".join(reporttext.split('par '))
		
		stmt = stmt  % (  pk_staff, esc(comment), esc("\n\n".join([reporthead or '', reporttext])))

		cu2.execute(stmt)
		
		if doc_med_pk:
			print "UPDATED"
		else:
			print "INSERTED"
		print "\t", ext_ref

	conto.commit()



#-----------------------------------
blocksize = 100
patcount = 0

def update_patcount(cu):
	stmt = "select count(ur_no) from patients"
	cu.execute(stmt)
	[patcount] = cu.fetchone()
	return patcount

def transfer_patients(startref = None):

		log_processed = file("processed.txt","w")

		started = startref == None
		rr = importer.get_next_demographics()
		totalpats = 1		
		while rr <> None:
			for r in rr:
				print "processing patient #", totalpats
				ur_no = r[0]
				if not started and ur_no.lower() <> startref.lower():
					print "skipping ", ur_no
				elif  not started:
					started = True

				if started:
					if nodemo:
						id_patient = find_patient(r)
					else:
						id_patient = process_patient( *r)

					if id_patient:
						ensure_xlnk_identity(id_patient)
						if not noprogress:	
							process_patient_progress( ur_no, id_patient )
							process_patient_history( ur_no , id_patient )
							clean_progress_notes( conto.cursor(), id_patient)
						if not nodocs:
							process_patient_documents(ur_no, id_patient)
						if not nopath:
							process_patient_pathol( ur_no, id_patient)
						log_processed.write(ur_no+"\n")
						
					
				totalpats += 1
				conto.commit()
			rr = importer.get_next_demographics()
		

def do_patient_relations():
	print "setting up identity relations"
	
	cu = confrom.cursor()
	patcount = update_patcount(cu)

	cu2 = conto.cursor()
	totalpats =0

	while totalpats < patcount:
		pass
		stmt = "select ur_no, link_to from patients  offset %d limit %d" % (totalpats, blocksize)
		print stmt
		cu.execute(stmt)
		rr = cu.fetchall()
		for r in rr:
			if link_to and link_to.strip() <> '':
			
				# link identities in lnk_person2relative using ur_no stored in lnk_identity2ext_id
				
				# pk_urno is from setup_urno_ext_type()  and id_related is from setup_id_related() and are globals
				
				stmt = """insert into dem.lnk_person2relative ( id_identity, id_relative, id_relation_type)
					values (( select id_identity from dem.lnk_identity2ext_id  where external_id = '%s' and fk_origin = %d), (select id_identity from dem.lnk_identity2ext_id  where external_id = '%s' and fk_origin = %d), %d) 
					""" % ( r[0], pk_urno, r[1], pk_urno, id_related)
					
				print stmt
				
				cu2.execute(stmt)

			
		
			totalpats += 1

	conto.commit()

if __name__== "__main__":

	arguments = sys.argv	
	if len(arguments) == 1:
		usage()
		sys.exit(-1)
	try:
		dsnfrom = None
		if "-from" in arguments:
			i = arguments.index('-from')
			dsnfrom = arguments[i+1]

		dsnto = None
		if "-to" in arguments:
			i = arguments.index('-to')
			dsnto = arguments[i+1]
			
		dbapi_n = 'pyPgSQL'

		if "-dbapi" in arguments:
			i = arguments.index('-dbapi')
			dbapi_n = arguments[i+1]

		if dbapi_n == 'pyPgSQL' and dsnto:
			global orig_user
			orig_user = dsnto.split(':')[-2]

		dbapi = get_dbapi(dbapi_n)	
		
		if not dbapi:
			print "Error: no dbapi found"
			sys.exit(-1)
		
		print "dsn from ", dsnfrom
		print "dsn to ", dsnto
		confrom = dbapi.connect(dsnfrom)
		conto   = dbapi.connect(dsnto)
		


		if "-block" in arguments:
			i = arguments.index('-block')
			blocksize = int ( arguments[i+1] )

		if "-start" in arguments:
			startref = arguments[arguments.index('-start')+1]
		else:
			startref = None

		nodemo = "-nodemo" in arguments
		noprogress = "-noprogress" in arguments
		nodocs = "-nodocs" in arguments
		nopath = "-nopath" in arguments


		global importer	
		importer = pg_importer()
		
		transfer_drs()
		
		#while 1:	
		#	dr_id = raw_input('press enter to continue, or enter a dr_id')
		#	print get_dr_user(dr_id)
		#	if dr_id == '':
		#		break

		setup_transfer_patients_conditions()
		
		transfer_patients(startref)
		do_patient_relations()
	except:
		print "AN ERROR HAS OCCURED"
		print "="*50
		print "USAGE FOLLOWED BY ERROR:"
		usage()	
		print
		print
		if conto:
			y = raw_input("COMMIT CHANGES TO TARGET DATABASE ? ")
			y = y.strip().lower()
			if y == 'y':
				conto.commit()
			else:
				conto.rollback()
		raise 
	
	
		
	
