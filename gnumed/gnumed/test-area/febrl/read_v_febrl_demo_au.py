"""outputs csv compatible form of contents of view v_febrl_demo_read_au  """

import pgdb
title = 'rec_id, given_name, surname, street_number, address_1, address_2, suburb, postcode, state, date_of_birth, soc_sec_id'

c = pgdb.connect('localhost:gnumed')
cu = c.cursor()

cu.execute('select id, firstnames, lastnames, number, street, street2, city, postcode, state,dob, soc_sec_id from v_febrl_demo_read_au')
r = cu.fetchall()
print title
for l in r:
	print ', '.join(l)



