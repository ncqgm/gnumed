--
-- Selected TOC Entries:
--
\connect - syan

set datestyle to european;
--
-- TOC Entry ID 2 (OID 31684)
--
-- Name: identity_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "identity_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 4 (OID 31703)
--
-- Name: identity Type: TABLE Owner: syan
--

CREATE TABLE "identity" (
	"id" integer DEFAULT nextval('"identity_id_seq"'::text) NOT NULL,
	"pupic" character(24),
	"gender" character(2) DEFAULT '?',
	"karyotype" character(10),
	"dob" date,
	"cob" character(2),
	"deceased" date,
	CONSTRAINT "identity_gender" CHECK (((((((gender = 'm'::bpchar) OR (gender = 'f'::bpchar)) OR (gender = 'h'::bpchar)) OR (gender = 'tm'::bpchar)) OR (gender = 'tf'::bpchar)) OR (gender = '?'::bpchar))),
	Constraint "identity_pkey" Primary Key ("id")
)
INHERITS ("audit_identity");

--
-- TOC Entry ID 10 (OID 31703)
--
-- Name: TABLE "identity" Type: COMMENT Owner: 
--

COMMENT ON TABLE "identity" IS 'represents the unique identity of a person';

--
-- TOC Entry ID 5 (OID 31707)
--
-- Name: COLUMN "identity"."pupic" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."pupic" IS 'Portable Unique Person Identification Code as per gnumed white papers';

--
-- TOC Entry ID 6 (OID 31708)
--
-- Name: COLUMN "identity"."gender" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."gender" IS '(m)ale, (f)emale, (h)ermaphrodite, (tm)transsexual phaenotype male, (tf)transsexual phaenotype female, (?)unknown';

--
-- TOC Entry ID 7 (OID 31710)
--
-- Name: COLUMN "identity"."dob" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."dob" IS 'date of birth';

--
-- TOC Entry ID 8 (OID 31711)
--
-- Name: COLUMN "identity"."cob" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."cob" IS 'country of birth as per date of birth, coded as 2 character ISO code';

--
-- TOC Entry ID 9 (OID 31712)
--
-- Name: COLUMN "identity"."deceased" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."deceased" IS 'date when a person has died (if)';

--
-- Data for TOC Entry ID 11 (OID 31703)
--
-- Name: identity Type: TABLE DATA Owner: syan
--


COPY "identity"  FROM stdin;
11	2	\N	m 	\N	30-8-1944	\N	\N	\N
14	4	\N	m 	\N	1/2/2000	\N	\N	\N
16	5	\N	m 	\N	30-7-1966	\N	\N	\N
18	6	\N	m 	\N	10-10-1933	\N	\N	\N
24	8	                        	m 	\N	1-1-2002	\N	\N	\N
33	11	1213423423              	m 	\N	1/1/1950	\N	\N	\N
36	12	230-2000-1              	m 	\N	20-12-1999	\N	\N	\N
27	9	4444555551              	f 	\N	12-12-1989	\N	\N	\N
39	13	444-55055               	m 	\N	17-6-2000	\N	\N	\N
21	7	1111-2222               	f 	\N	1-Nov-1999	\N	\N	\N
30	10	111-2222                	m 	\N	1-1-1933	\N	\N	\N
\.
--
-- TOC Entry ID 12 (OID 31783)
--
-- Name: "RI_ConstraintTrigger_31782" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "names" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'names', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 13 (OID 31785)
--
-- Name: "RI_ConstraintTrigger_31784" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "names" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'names', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 14 (OID 31891)
--
-- Name: "RI_ConstraintTrigger_31890" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 15 (OID 31893)
--
-- Name: "RI_ConstraintTrigger_31892" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 16 (OID 31897)
--
-- Name: "RI_ConstraintTrigger_31896" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_relative', 'id');

--
-- TOC Entry ID 17 (OID 31899)
--
-- Name: "RI_ConstraintTrigger_31898" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_relative', 'id');

--
-- TOC Entry ID 18 (OID 31954)
--
-- Name: "RI_ConstraintTrigger_31953" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "identities_addresses" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'identities_addresses', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 19 (OID 31956)
--
-- Name: "RI_ConstraintTrigger_31955" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "identities_addresses" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'identities_addresses', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 3 (OID 31684)
--
-- Name: identity_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"identity_id_seq"', 13, 't');

