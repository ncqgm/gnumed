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


#confrom is the connection to a dumped dbf to postgres database, which has the source data.
#conto is the connection to a gnumed_v2 database, which will take the converted data.
confrom = None
conto = None

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
		l.append(x)
	return ''.join(l)

#---------------------------------------------------
#---------------------------------------------------
def insert_identity(cu, firstnames, surname, preferred,  dob, sex, title, dec_date):

	if dob == None:
		dob = "1-1-1960"
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
def check_ext_id(cu,  pk_exttype, text, firstnames, lastnames, dob):
	stmt = "select count(*) from dem.names n, dem.identity i, dem.lnk_identity2ext_id l where n.firstnames = '%s' and n.lastnames = '%s' and i.dob = '%s' and l.external_id = '%s' and l.fk_origin = %d and l.id_identity = i.pk and n.id_identity = i.pk" % ( esc( firstnames), esc( lastnames), esc(dob), esc( text), pk_exttype )
	print stmt
	cu.execute(stmt)
	[n] = cu.fetchone()
	if n > 0:
		return False
	return True


def insert_ext_id(cu, id, pk_exttype, text):
	stmt = "insert into dem.lnk_identity2ext_id ( id_identity, fk_origin, external_id) values (%d, %d, '%s') " % ( id, pk_exttype, esc(text) )  
	print stmt
	cu.execute(stmt)

	return True
	

#---------------------------------------------------
def process_dr( dr, sex,dob, phone, fax, email , reg_no, prov_no, pres_no, worktime, cat):
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
				insert_ext_id( cu, id, find_or_insert_exttype( cu, exttype, issuer), number)


		group = "gm-doctors"
		username = '-'.join([firstnames] + [surname])

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
	cu = confrom.cursor()
	cu.execute('select dr, sex,dob, phone, fax, email, reg_no, prov_no, pres_no, drcode as worktime_cat, category from dr')
	r  = cu.fetchall()
	
	for row in r:
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

urno_issuer = "dbf importer type au-md v0.1"

pk_urno= 0

def setup_urno_ext_type(cu):
	global pk_urno
	res = None
	while not res or res == []:
		stmt = "select pk from dem.enum_ext_id_types where name = 'ur_no' and issuer = '%s'"% urno_issuer
		cu.execute(stmt)
	 
		res = cu.fetchone()
		if not res or res == []:
			stmt_insert_urno_type = "insert into dem.enum_ext_id_types ( name, issuer) values ('ur_no', '%s') " % urno_issuer
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

	stmt_insert_lnk_id_address = "insert into dem.lnk_person_org_address( id_identity, id_address, address_source) values ( %d, %d, 'import program')" % (id, id_address)
	print stmt_insert_lnk_id_address
	cu.execute(stmt_insert_lnk_id_address)
	 
	
	return True


related_map = {}

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
		
		
	l =  [  ( urno_issuer, 'ur_no', ur_no), 
		( "HIC", "Medicare",  medicare ),
		( "Centrelink", "CRN", pens_no ), 
		( "Department of Veteran's Affairs", "DVA", dva_no ) ]

	for issuer, exttype, number in l:
		if number and len(number):
			if not check_ext_id(cu,  find_or_insert_exttype(cu, exttype, issuer ),  number, firstname, surname, dob):
				return None
				
	id = insert_identity (cu, firstname, surname, knownas, dob, sex, title, decdate )		
		

	for issuer, exttype, number in l:
		if number and len(number):
			insert_ext_id(cu, id,  find_or_insert_exttype(cu, exttype, issuer ),  number)
		
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
			print "FAILED TO INSERT THIS ADDRESS ", id, number_part, street_part, city, postcode

	
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

#-------------------------------------------------
def process_patient_progress(ur_no, id_patient):
	# progress note maps to an encounter and episode

	# TODO need to add modified_by to all inserts to use non-login users as well
	
	cu = confrom.cursor()
	
	stmt = "select count(*) from pg_indexes where indexname = 'idx_urno_progress'"
	cu.execute(stmt)
	[n] = cu.fetchone()
	if n == 0:
		stmt = "create index  idx_urno_progress  on progress using btree (ur_no)"
		print stmt
		cu.execute(stmt)

	prog_stmt = "select notes, exam, history, reason, reasoncode, visitdate, starttime, endtime, update from progress where ur_no = '%s' order by visitdate, starttime" % esc(ur_no) 

	print prog_stmt
	cu.execute(prog_stmt)
	rr = cu.fetchall()

	by_reason = {}
	
	noreason = "reason for encounter unspecified"
	
	# insert as unlinked episode, and encounter with narrative
	for r in rr:
		notes, exam, history, reason, reasoncode, visitdate, starttime, endtime,update  = r
		if reason and len(reason.strip()):
			reason = reason.strip().lower()
			l = by_reason.get(reason, [])
			l.append(r)
			by_reason[reason] = l	
		else:
			l = by_reason.get( noreason, [])
			l.append(r)
			by_reason[noreason] = l

	
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

	
	map_time_to_episode = {}
	
	last_datepart = None
	for r in rr:
		notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update = r
		print "PROCESSING progress =\n notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update"
		print notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update
		
		
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

		# check encounter exists
		stmt = "select count(*) from clin.encounter where fk_patient = %d and rfe = '%s' and started = '%s' and last_affirmed = '%s' " % ( id_patient, esc(reason), esc(started), esc(lastaffirmed) )
		print stmt
		cu2.execute(stmt)
		[n] = cu2.fetchone()
		if n > 0:
			# skip as encounter already entered
			continue
		# create an encounter
		stmt = "insert into clin.encounter ( fk_patient, rfe, started, last_affirmed) values ( %d, '%s', '%s', '%s')" % ( id_patient, esc( reason), esc(started), esc(lastaffirmed) )

		print stmt

		cu2.execute(stmt)
		stmt = "select max(pk) from clin.encounter"
		cu2.execute(stmt)
		[pk_encounter] = cu2.fetchone()

		#create an unlinked episode

		stmt = "insert into clin.episode ( fk_patient, description, is_open) values (%d, '%s', false)" % ( id_patient, esc(reason))

		print stmt

		cu2.execute(stmt)

		stmt = "select max(pk) from clin.episode"
		cu2.execute(stmt)
		
		[pk_episode] = cu2.fetchone()

		map_time_to_episode[str(visitdate) +' '+ str(starttime)] = (pk_episode , started, lastaffirmed) 
		# this is for linking episode later if required
		
		notes2 = rtf2plain.rtf2plain(notes)
			
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
				
			if n > 0:
				cat[state].append(x[:n])
			if n >= 0:
				x= x[n:]
				state = 'p'
			cat[state].append(x)
				
		cats.append(cat)
		
		narratives = []

		for cat in cats:
			for k in ['s', 'o', 'a', 'p' ] :
				narratives.append( (k, '\n'.join(cat[k]) ))
		
		#create the narrative
		for (soap_cat, narrative) in narratives:
			if narrative.strip() == '':
				continue
			stmt = "insert into clin.clin_narrative( fk_encounter, fk_episode, clin_when, soap_cat, narrative) values (%d,%d,'%s','%s', '%s') " % ( pk_encounter, pk_episode, esc(started),soap_cat,  esc( narrative) )


			print stmt
			cu2.execute(stmt)
			
		
		#stmt = "insert into clin.clin_narrative( fk_encounter, fk_episode, clin_when, soap_cat, narrative) values (%d,%d,'%s','s', '%s') " % ( pk_encounter, pk_episode, esc(started), esc( rtf2plain.rtf2plain(notes)) )

		#print stmt
		#cu2.execute(stmt)
		
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
				notes, exam, history, reason, reasoncode, visitdate, starttime, endtime , update = r
				
				(pk_episode, started, lastaffirmed) = map_time_to_episode.get( str(visitdate) + ' '+str(starttime), (None,None,None) )
				if pk_episode:
					stmt = "update clin.episode set fk_health_issue = %d, fk_patient = Null where pk = %d " % (pk_issue,pk_episode)
					print stmt
					cu2.execute(stmt)

					

	return map_time_to_episode			
			
		
	
#-----------------------------------
blocksize = 100
patcount = 0

def update_patcount(cu):
	stmt = "select count(ur_no) from patients"
	cu.execute(stmt)
	[patcount] = cu.fetchone()
	return patcount

def transfer_patients():
	cu = confrom.cursor()
	patcount = update_patcount(cu)	
	
	totalpats = 0

	
	
	stmt = 'select ur_no, title, firstname, knownas, surname, sex, dob, decdate, deceased, address, city, postcode, phone, bus_phone, mob_phone,   mc_no, mc_index, mc_expiry, pens_no, dva_no, update from patients offset %d limit %d'
	
	while totalpats < patcount:
		get_pat_stmt = stmt % (totalpats, blocksize) 

		print get_pat_stmt
		cu.execute(get_pat_stmt)
		rr = cu.fetchall()
		
		for r in rr:
			print "processing patient #", totalpats
			id = process_patient( *r)
			if id:
				process_patient_progress( r[0], id )
			totalpats += 1
			conto.commit()
		

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

	
	try:
		dsnfrom = None
		if "-from" in sys.argv:
			i = sys.argv.index('-from')
			dsnfrom = sys.argv[i+1]

		dsnto = None
		if "-to" in sys.argv:
			i = sys.argv.index('-to')
			dsnto = sys.argv[i+1]

		dbapi_n = 'pyPgSQL'

		if "-dbapi" in sys.argv:
			i = sys.argv.index('-dbapi')
			dbapi_n = sys.argv[i+1]


		dbapi = get_dbapi(dbapi_n)	
		
		if not dbapi:
			print "Error: no dbapi found"
			sys.exit(-1)
		
		print "dsn from ", dsnfrom
		print "dsn to ", dsnto
		confrom = dbapi.connect(dsnfrom)
		conto   = dbapi.connect(dsnto)
		


		if "-block" in sys.argv:
			i = sys.argv.index('-block')
			blocksize = int ( sys.argv[i+1] )
			
		
		transfer_drs()
		
		setup_transfer_patients_conditions()
		
		transfer_patients()
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
	
	
		
	
