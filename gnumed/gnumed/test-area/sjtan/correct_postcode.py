"""a febrl import script.
reads a febrl dbgen csv file , and outputs a gnumed compatible postcode/urb combination correct file to standard output , can be redirected to another csv file"""

# run in the dbgen directory
csv='../dbgen/dataset1.csv'

import pgdb
import datetime

def validate_date( dobnum):
	if len(dobnum) < 8:
		return '20040101'
	y, m, d =  int(dobnum[0:4]), int(dobnum[4:6]), int(dobnum[6:]) 
	
	"""	thirty days has september, 
		april , june and november; 
		all the rest have 31, 
		except february which has 28"""
		
	if m < 1 : m = 1 
	elif m > 12 : m = 12

	if m in [9, 4, 6, 11]: days = range(1,31) 
	elif m == 2: days = range(1,29)
	else: days = range(1, 32)

	if d < days[0] : d = days[0]
	elif d > days[-1]: d= days[-1]
	
	return datetime.datetime(y,m,d).strftime('%Y%m%d')	


c=pgdb.connect('localhost:gnumed')
cu = c.cursor()
pcodes = {}
states = {}
citys = {}
title = 1
for l in file(csv):
	
	#print l
	if title:
		title = 0
		print l.strip()
		continue
	[rec_id, firstnames, lastnames, number, street1, street2, city, postcode, state, dobnum, tel] = [x.strip() for x in l.split(',')]
	#print type(postcode), postcode
	if len(postcode) == 0:
		continue
	pcode = int(postcode)
	if not pcodes.has_key(pcode):
		cu.execute("select urb.name, state.code from urb, state where postcode= %d and state.id = urb.id_state" % pcode)
		l = cu.fetchall()
		pcodes[pcode] = [ x[0].strip() for x in l]
		states[pcode] = [ x[1].strip() for x in l]
	city = city.upper()
	if not city in pcodes[pcode] and len(pcodes[pcode]):
		#print "city", city, " doesn't match ", pcode, pcodes[pcode]
			city = pcodes[pcode][0]
	elif not city in pcodes[pcode] and len(pcodes[pcode]) == 0:
		cu.execute("select urb.postcode, state.code from urb, state where urb.name = '%s' and state.id = urb.id_state" % city)
		l = cu.fetchone()
		if not l:
			continue
		if len(l) == 2:
			pcode, state = int(l[0]), l[1]
			states[pcode] = [state]

		
	state = state.upper()
	if not state in states[pcode] and len(states[pcode]):
		#print "state ", state, " isn't in ", states[pcode]
		state = states[pcode][0]

		
	dobnum = validate_date(dobnum)

	print ', '.join( [ rec_id, firstnames, lastnames, number, street1, street2, city, postcode, state, dobnum, tel] )


	

	

	
	
