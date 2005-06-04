--
-- PostgreSQL database dump
--

SET client_encoding = 'unicode';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'gm-dbo';

SET search_path = public, pg_catalog;

--
-- Data for TOC entry 3 (OID 217869)
-- Name: identity; Type: TABLE DATA; Schema: public; Owner: gm-dbo
--

INSERT INTO identity VALUES (9347, 0, '2005-05-24 17:13:14.660497+10', 'postgres', 8, NULL, 'm', NULL, '1920-01-20 08:00:00+10', NULL, 'US', NULL, 'Dr.');


--
-- TOC entry 2 (OID 217867)
-- Name: identity_pk_seq; Type: SEQUENCE SET; Schema: public; Owner: gm-dbo
--

SELECT pg_catalog.setval('identity_pk_seq', 15, true);


--
-- PostgreSQL database dump
--

SET client_encoding = 'unicode';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'gm-dbo';

SET search_path = public, pg_catalog;

--
-- Data for TOC entry 3 (OID 217904)
-- Name: names; Type: TABLE DATA; Schema: public; Owner: gm-dbo
--

INSERT INTO "names" VALUES (8, 8, true, 'McCoy', 'Leonard Horatio', NULL, NULL);
INSERT INTO "names" VALUES (9, 8, false, 'DeForest', 'Kelley', NULL, 'name of the actor');


--
-- TOC entry 2 (OID 217902)
-- Name: names_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gm-dbo
--

SELECT pg_catalog.setval('names_id_seq', 17, true);


--
-- PostgreSQL database dump
--

SET client_encoding = 'unicode';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'gm-dbo';

SET search_path = public, pg_catalog;

--
-- Data for TOC entry 3 (OID 217978)
-- Name: staff_role; Type: TABLE DATA; Schema: public; Owner: gm-dbo
--

INSERT INTO staff_role VALUES (32, 0, '2005-05-24 17:12:42.946233+10', 'gm-dbo', 1, 'doctor', NULL);
INSERT INTO staff_role VALUES (33, 0, '2005-05-24 17:12:42.948768+10', 'gm-dbo', 2, 'nurse', NULL);
INSERT INTO staff_role VALUES (34, 0, '2005-05-24 17:12:42.950852+10', 'gm-dbo', 3, 'manager', NULL);
INSERT INTO staff_role VALUES (35, 0, '2005-05-24 17:12:42.953672+10', 'gm-dbo', 4, 'secretary', NULL);
INSERT INTO staff_role VALUES (36, 0, '2005-05-24 17:12:42.955646+10', 'gm-dbo', 5, 'X-ray assistant', NULL);
INSERT INTO staff_role VALUES (37, 0, '2005-05-24 17:12:42.957797+10', 'gm-dbo', 6, 'lab technician', NULL);
INSERT INTO staff_role VALUES (38, 0, '2005-05-24 17:12:42.959708+10', 'gm-dbo', 7, 'medical student', NULL);
INSERT INTO staff_role VALUES (39, 0, '2005-05-24 17:12:42.961728+10', 'gm-dbo', 8, 'student nurse', NULL);
INSERT INTO staff_role VALUES (40, 0, '2005-05-24 17:12:42.963751+10', 'gm-dbo', 9, 'trainee - secretary', NULL);
INSERT INTO staff_role VALUES (41, 0, '2005-05-24 17:12:42.965657+10', 'gm-dbo', 10, 'trainee - X-ray', NULL);
INSERT INTO staff_role VALUES (42, 0, '2005-05-24 17:12:42.967972+10', 'gm-dbo', 11, 'trainee - lab', NULL);


--
-- TOC entry 2 (OID 217976)
-- Name: staff_role_pk_seq; Type: SEQUENCE SET; Schema: public; Owner: gm-dbo
--

SELECT pg_catalog.setval('staff_role_pk_seq', 11, true);


--
-- PostgreSQL database dump
--

SET client_encoding = 'unicode';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'gm-dbo';

SET search_path = public, pg_catalog;

--
-- Data for TOC entry 3 (OID 217990)
-- Name: staff; Type: TABLE DATA; Schema: public; Owner: gm-dbo
--

INSERT INTO staff VALUES (9349, 0, '2005-05-24 17:13:14.671073+10', 'postgres', 1, 8, 1, 'any-doc', 'LMcC', 'Enterprise Chief Medical Officer');


--
-- TOC entry 2 (OID 217988)
-- Name: staff_pk_seq; Type: SEQUENCE SET; Schema: public; Owner: gm-dbo
--

SELECT pg_catalog.setval('staff_pk_seq', 3, true);


