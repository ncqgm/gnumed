--
-- PostgreSQL database dump
--

\connect - "gm-dbowner"

SET search_path = public, pg_catalog;

--
-- Data for TOC entry 2 (OID 22970)
-- Name: vaccine; Type: TABLE DATA; Schema: public; Owner: gm-dbowner
--

INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES (1, 'Hepatitis B', 'Hep B', false, true, '00:00', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'diptheria-tetanus-acellular pertussis infant/child formulation', 'DTPa', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'diptheria-tetanus-acellular pertussis adult/adolescent formulation', 'dTpa', false, true, '12 years', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'Haemophilius influenzae type b', 'PRP-OMP', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'Haemophilius influenzae type b(PRP-T)', 'PRP-T', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'Haemophilius influenzae type b(HbOC)', 'HbOC', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'inactivated poliomyelitis vaccine', 'IPV', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES (2, 'varicella-zoster vaccine', 'VZV', true, true, '1 year', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, '7-valent pneumococcal conjugate vaccine', '7vPCV', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, '23-valent pneumococcal polysaccharide vaccine', '23vPPV', false, true, '1 year 6 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'meningococcal C conjugate vaccine', 'menCCV', false, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 1, 'adult diptheria-tetanus', 'dT', false, true, '8 years', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 3, 'oral poliomyelitis vaccine', 'OPV', true, true, '2 mons', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 2, 'measles-mumps-rubella vaccine', 'MMR', true, true, '1 year', NULL, NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, is_licensed, min_age, max_age, last_batch_no, "comment") VALUES ( 2, 'influenza vaccine', 'influenza', false, true, '6 mons', NULL, NULL, NULL);


--
-- TOC entry 1 (OID 22968)
-- Name: vaccine_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gm-dbowner
--

SELECT pg_catalog.setval ('vaccine_id_seq', 16, true);


