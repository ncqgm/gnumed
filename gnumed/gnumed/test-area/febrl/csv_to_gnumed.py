"""run correct_postcodes.py on say datase1.csv and redirect output to the file named in the csv variable below"""

#the file name that captured the standard output of correct_csv.py or output of read_v_febrl-demo-au.py
csv='../dbgen/file-gnumed-dataset2.csv'

soc_sec_org = 'Centrelink'
import pgdb

def escape_quote(txt, j=0 , k=0):
	if k == 0:
		k = len(txt)

	for i in range(j, k):
		if txt[i] == "'" and i > 0 and txt[i-1] != '\\':
			txt = txt[:i] + '\\'+txt[i:]
			return escape_quote(txt, i + 2, len(txt))
	return txt	

c = pgdb.connect('localhost:gnumed')
cu = c.cursor()
title = 1
for l in file(csv):
	if title:
		title = 0
		continue
	print l
	[rec_id, firstnames, lastnames, number, street1, street2, city, postcode, state, dobnum, soc_sec_id] = [x.strip() for x in l.split(',')]
	if dobnum <> '':
		dob = int(dobnum)
	else:
		dob = 20040101
	c.commit()
	cu.execute("select nextval('identity_id_seq')")
	[id] = cu.fetchone()
	
	cu.execute("insert into identity ( id, dob) values( %d, '%d')" % (id, dob) )
	cu.execute("insert into names( lastnames, firstnames, id_identity) values( '%s', '%s', %d)"  % ( escape_quote(lastnames), escape_quote(firstnames), id) )
	cu.execute("update names set active='t' where id_identity=%d" % id)

	cu.execute("insert into v_basic_address( number, street, street2, city, postcode, state, country) values ( '%s', '%s', '%s', '%s', '%s', '%s', 'AU' ) " % ( number, escape_quote(street1), escape_quote(street2), escape_quote(city.upper()), postcode, state.upper()) )
	cu.execute("select currval('address_id_seq')")
	[id_address] = cu.fetchone()
	cu.execute("insert into lnk_person_org_address( id_identity, id_address, id_type) values( %d, %d, 1) " % ( id, id_address) )

	cu.execute("insert into lnk_identity2ext_id ( external_id, fk_origin, id_identity) values ( '%s', (select pk from enum_ext_id_types where issuer= '%s'), %d)" % ( soc_sec_id, soc_sec_org, id) )

	# CHANGE THIS TO COMMENT TO PUT TEST DATA IN GNUMED DB. ONLY ON A TEST DATABASE, AS NOT REVERSIBLE.
	c.commit()
	#c.rollback()


	
	
	


