--
-- PostgreSQL database dump
--

\connect - "gm-dbo"

SET search_path = public, pg_catalog;

--
-- Data for TOC entry 2 (OID 22970)
-- Name: vaccine; Type: TABLE DATA; Schema: public; Owner: gm-dbo
--

INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'Hepatitis B', 'Hep B', false, '00:00', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'diptheria-tetanus-acellular pertussis infant/child formulation', 'DTPa', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'diptheria-tetanus-acellular pertussis adult/adolescent formulation', 'dTpa', false, '12 years', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'Haemophilius influenzae type b', 'PRP-OMP', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'Haemophilius influenzae type b(PRP-T)', 'PRP-T', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'Haemophilius influenzae type b(HbOC)', 'HbOC', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'inactivated poliomyelitis vaccine', 'IPV', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (2, 'varicella-zoster vaccine', 'VZV', true, '1 year', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, '7-valent pneumococcal conjugate vaccine', '7vPCV', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, '23-valent pneumococcal polysaccharide vaccine', '23vPPV', false, '1 year 6 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'meningococcal C conjugate vaccine', 'menCCV', false, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (1, 'adult diptheria-tetanus', 'dT', false, '8 years', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (3, 'oral poliomyelitis vaccine', 'OPV', true, '2 mons', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (2, 'measles-mumps-rubella vaccine', 'MMR', true, '1 year', NULL, NULL);
INSERT INTO vaccine ( id_route, trade_name, short_name, is_live, min_age, max_age, "comment") VALUES (2, 'influenza vaccine', 'influenza', false, '6 mons', NULL, NULL);


--
-- TOC entry 1 (OID 22968)
-- Name: vaccine_pk_seq; Type: SEQUENCE SET; Schema: public; Owner: gm-dbo
--

SELECT pg_catalog.setval ('vaccine_pk_seq', 16, true);


