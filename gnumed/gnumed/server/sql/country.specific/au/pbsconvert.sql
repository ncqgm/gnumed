-- Script to help convert from PBS tables to gmdrugs.sql tables
-- Ian Haywood 1/11/01



COPY "amount_units"  FROM stdin;
2	mL
1	each
3	g
4	m
5	cm
\.


COPY "drug_units"  FROM stdin;
1	t	mg
2	t	mL
3	t	g
4	t	cm
5	f	unit
6	t	mcg
\.


COPY "drug_route"  FROM stdin;
1	intravenous
2	intramuscular
3	subcutaneous
4	oral
5	suppository
6	pessary
7	opthalmological
8	otological
9	dermatological
10	otological/opthalmological
11	inhalant
12	rhinological
\.

COPY "presentation"  FROM stdin;
1	tablet
2	chewable tablet
3	effervescent tablet
4	capsule
5	injection
6	powder
7	wafer
8	suspension
9	lozenge
10	cream
11	ointment
12	paste
13	solution
14	bandage
15	tablet
16	spray
17	bath oil
18	dressing
\.


COPY "drug_form"  FROM stdin;
7	11	1	2	13
12	4	1	1	2
15	4	1	1	9
17	1	5	2	5
13	4	1	3	6
9	4	3	3	6
6	1	1	2	5
5	4	1	1	7
4	4	1	2	8
3	4	1	1	4
2	4	1	1	3
1	4	1	1	1
8	7	1	3	1
16	1	3	2	5
23	12	6	1	16
18	9	4	4	14
19	9	2	1	17
20	4	6	1	4
21	4	5	1	4
22	11	6	1	4
23	9	3	3	11
24	1	1	2	5
25	9	5	3	10
26	9	3	1	10
27	9	6	3	10
28	9	4	5	18
29	9	4	1	18
\.

-- temporary table to match pbs field formandstrength with drug_form

CREATE TABLE pbs_xref (
	drug_form_id INTEGER,
	pbs_regex varchar (100), -- RE for PBS field of form description
	packsize BOOL -- true if get packetsize as last int in the string.
);

COPY "pbs_xref"  FROM stdin;
7	Solution for inhalation [0-9]+ mg.*	f
9	Infant formula, powder.*	f
12	Chewable tablet [0-9]+ mg	f
15	Lozenge [0-9]+ mg.*	f
17	Injection [0-9]+ unit.*	f
13	Powder for syrup [0-9]+ mg	f
9	Powder [0-9]+ g.*	f
6	Injection [0-9]+ mg.*	f
5	Wafer [0-9]+ mg.*	f
4	Oral suspension [\\.,0-9]+ mg.*, [0-9] mL	f
3	Capsule [\\.,0-9]+ mg.*	f
3	Capsule equivalent to [\\.,0-9]+ mg.*	f
2	Effervescent tablet [0-9]+ mg.*|f!
1	Tablet .*[\\.,0-9]+ mg.*	f
1	Tablets .*[\\.,0-9]* mg.*, [0-9]+	t
8	Eye ointment [0-9]+ mg.*	f
9	Sachet containing oral powder [0-9]+ g	f
13	Powder for paediatric oral drops [0-9]+ mg.*	f
16	Injection [0-9]+ g.*	f
23	Aqueous nasal spray .*[0-9]+ micrograms.*	t
18	Bandage.*[\\.,0-9]+ cm x [\\.,0-9]+ m.*	t
19	Bath oil [0-9]+ mL	f
20	Capsule [\\.,0-9]+ microgram.*	f
21	Capsule [\\,,0-9]+ units	f
21	Capsule .*[\\,,0-9] BP units of lipase activity	f
22	Capsule containing powder for oral inhalation.*[0-9]+ micrograms.*	f
22	Capsule containing powder for oral inhalation.*[0-9]+ mg.*	f
23	Compound ointment.*[0-9]+ g	f
9	Compound powder.*[0-9]+ g	f
24	Concentrated injection [0-9]+ mg in [0-9]+ mL	t
25	Cream [\\,,0-9]+ units.*[0-9]+ g	t
26	Cream [0-9]+ g	f
27	Cream [0-9]+ mg.*[0-9]+ g	t
1	Crushable tablet [0-9]+ mg	f
1	Dispersible tablet [0-9]+.*mg	f
28	Dressing [\\.,0-9]+ cm x [\\.,0-9]+ cm	t
29	Dressings.*[\\.,0-9]+ cm x [\\.,0-9]+ cm, [0-9]+	t
\.

-- get formandstrength fields not processed
-- select formandstrength from pbsimport 
-- except 
-- select pbsimport.formandstrength from pbsimport, pbs_xref 
-- where pbsimport.formandstrength ~ pbs_xref.pbs_regex;

create view drug_form_denorm as select distinct
drug_route.description as drug_route,
drug_units.description as drug_units, 
amount_units.description as amount_units, 
presentation.name as presentation, 
pbs_xref.pbs_regex 
from drug_route, drug_units, amount_units, presentation, drug_form, pbs_xref 
where drug_route.id = drug_form.route and 
drug_units.id = drug_form.unit and  
amount_units.id = drug_form.amount_unit and 
presentation.id = drug_form.presentation and 
pbs_xref.drug_form_id = drug_form.id;  


-- get value of first int in a string
CREATE FUNCTION getfirstint (text)
    RETURNS float4
    AS '/home/ian/my_gnumed/getint.so'
    LANGUAGE 'c';

-- get value of last int in string 
CREATE FUNCTION getlastint (text)
    RETURNS float4
    AS '/home/ian/my_gnumed/getint.so'
    LANGUAGE 'c';
