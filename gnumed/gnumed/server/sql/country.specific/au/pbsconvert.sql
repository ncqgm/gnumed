-- Script to help convert from PBS tables to gmdrugs.sql tables
-- Ian Haywood 1/11/01



COPY "amount_unit"  FROM stdin;
2	mL
1	each
3	g
4	m
5	cm
\.


COPY "drug_unit"  FROM stdin;
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
13	injection (iv/im/sc)
\.

COPY "drug_presentation"  FROM stdin;
1	tablet	4	1
2	chewable tablet	4	1
3	effervescent tablet	4	1
4	capsule	4	1
5	injection (unknown IV/IM/SC)	13	2
6	powder	4	3
7	wafer	4	1
8	suspension	4	2
9	lozenge	4	1
10	skin cream	9	3
19	vaginal cream	6	3
11	ointment	9	2
12	paste	9	5
13	solution	4	2
14	bandage	9	5
16	nasal spray	12	2	
17	bath oil	9	2
18	dressing	9	4
20	eye drops	7	2
21	ear drops	8	2
22	suppository	5	1
23	anal cream	5	3
24	aerosol	11	1
25	nebule	11	2
26	IM injection	2	2
27	IV solution	1	2
28	SC injection	3	2
\.


-- temporary table to convert PBS field formandstrength
CREATE TABLE convert (
       fs varchar (200), -- formandstrength string
       done BOOL, -- user has processed
       presentation INTEGER,
       amount FLOAT
       id SERIAL
);

-- link in list of drug amounts
CREATE TABLE link_amount (
       convert_id INTEGER,
       unit INTEGER,
       amount FLOAT,
       id SERIAL -- NB order is important
);
 
       
