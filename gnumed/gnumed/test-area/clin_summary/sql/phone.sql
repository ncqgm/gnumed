--
-- Selected TOC Entries:
--
\connect - syan
--
-- TOC Entry ID 2 (OID 32139)
--
-- Name: phone_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "phone_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 4 (OID 32158)
--
-- Name: phone Type: TABLE Owner: syan
--

CREATE TABLE "phone" (
	"audit_id" integer DEFAULT nextval('"audit_identity_audit_id_seq"'::text),
	"id" integer DEFAULT nextval('"phone_id_seq"'::text) NOT NULL,
	"phone1" character varying(20),
	"phone2" character varying(20),
	"phone3" character varying(20),
	"id_identity" integer,
	Constraint "phone_pkey" Primary Key ("id")
);

--
-- Data for TOC Entry ID 5 (OID 32158)
--
-- Name: phone Type: TABLE DATA Owner: syan
--


COPY "phone"  FROM stdin;
54	13	\N	\N	\N	2
55	14	\N	\N	\N	4
56	15	\N	\N	\N	5
57	16	\N	\N	\N	6
58	17	\N	\N	\N	8
59	18	\N	\N	\N	11
60	19	\N	\N	\N	12
61	20	\N	\N	\N	9
63	22	\N	\N	\N	13
64	23	444-4000	555-5000	\N	10
62	21	111	3333	\N	7
\.
--
-- TOC Entry ID 3 (OID 32139)
--
-- Name: phone_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"phone_id_seq"', 23, 't');

