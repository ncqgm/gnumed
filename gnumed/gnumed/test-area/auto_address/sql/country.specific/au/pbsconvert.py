#!/usr/bin/python2

# python script to hand-generate conversion table for the field
# pbsimport.formandstrength

import pg

db = pg.connect ("gmdrugs")

todo = db.query ("SELECT id, fs FROM convert WHERE not done ORDER BY id").getresult ();


for id, fs in todo:
    print "No: %d F. and S.: %s\n" % (id, fs)
    x = raw_input ("Presentation:")
    if x != '':
        present = int (x)
        amount_unit, = db.query ("SELECT amount_unit FROM drug_presentation WHERE id=%d" % present).getresult ()[0]
	if present == 14:
		# bandages/dressings
		packsize = input ("Packsize: ")
		amount = 0
	else:
		packsize = 1
        	if amount_unit != 1:
            		amount = input ("Amount:")
        	else:
            		amount = 0
        	x = raw_input ("No. Substances (1):")
        	if x == '':
            		numsubst = 1
        	else:
            		numsubst = int (x)
        	for i in range (1, numsubst+1):
            		subst_amount = input ("Amount of Subst %d:" % i)
            		unit = raw_input ("Unit of Subst %d:" % i)
            		unit_id, = db.query ("SELECT id FROM drug_unit WHERE description='%s'" % unit).getresult ()[0]
            		db.query ("INSERT INTO link_amount VALUES (%d, %d, %d)" % (id, unit_id, subst_amount))
    else:
        present = 0 # fs doesn't make sense to translate
        amount = 0
    db.query ("UPDATE convert SET done='t', presentation=%d, amount=%d WHERE id=%d" % (present, amount, id))
                  
                  
    
