
--
-- TOC Entry ID 78 (OID 38099)
--
-- Name: clin_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "clin_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 219 (OID 38118)
--
-- Name: ix_type_link Type: TABLE Owner: syan
--

CREATE TABLE "ix_type_link" (
	"ix" integer,
	"type" integer
);

--
-- TOC Entry ID 220 (OID 38129)
--
-- Name: clin_record Type: TABLE Owner: syan
--

CREATE TABLE "clin_record" (
	"clin_id" integer DEFAULT nextval('clin_id_seq'::text) NOT NULL,
	"rec_time" date,
	"rec_place_id" integer,
	"rec_source_id" integer,
	"description" character varying(40),
	"extra" text,
	"author" character varying(32),
	Constraint "clin_record_pkey" Primary Key ("clin_id")
);

--
-- TOC Entry ID 221 (OID 38163)
--
-- Name: basic_context Type: TABLE Owner: syan
--

CREATE TABLE "basic_context" (
	"patient" integer,
	"started" date,
	"place" character varying(40)
)
INHERITS ("clin_record");

--
-- TOC Entry ID 222 (OID 38199)
--
-- Name: durable Type: TABLE Owner: syan
--

CREATE TABLE "durable" (
	"duration" integer,
	"dur_unit" character varying(10),
	"fin" date
)
INHERITS ("basic_context");

--
-- TOC Entry ID 223 (OID 38239)
--
-- Name: phx_durable Type: TABLE Owner: syan
--

CREATE TABLE "phx_durable" (
	"disease_id" integer
)
INHERITS ("durable");

--
-- TOC Entry ID 224 (OID 38281)
--
-- Name: phx_event Type: TABLE Owner: syan
--

CREATE TABLE "phx_event" (
	"disease_id" integer
)
INHERITS ("basic_context");

--
-- TOC Entry ID 225 (OID 38319)
--
-- Name: procedure Type: TABLE Owner: syan
--

CREATE TABLE "procedure" (
	"problem_id" integer,
	"proc_type_id" integer
)
INHERITS ("basic_context");

--
-- TOC Entry ID 226 (OID 38358)
--
-- Name: sequelae Type: TABLE Owner: syan
--

CREATE TABLE "sequelae" (
	"proc_id" integer DEFAULT 0,
	"phx_event" integer DEFAULT 0
)
INHERITS ("phx_durable");

--
-- TOC Entry ID 227 (OID 38405)
--
-- Name: meds Type: TABLE Owner: syan
--

CREATE TABLE "meds" (
	"drug_info" integer,
	"brand" integer DEFAULT 0
)
INHERITS ("basic_context");

--
-- TOC Entry ID 228 (OID 38445)
--
-- Name: med_dose Type: TABLE Owner: syan
--

CREATE TABLE "med_dose" (
	"dose" integer,
	"unit" character varying(20),
	"timing" integer,
	"meds_id" integer
)
INHERITS ("durable");

--
-- TOC Entry ID 229 (OID 38490)
--
-- Name: med_timing Type: TABLE Owner: syan
--

CREATE TABLE "med_timing" (
	"descript" character varying(30)
)
INHERITS ("clin_record");

--
-- TOC Entry ID 230 (OID 38524)
--
-- Name: med_qty Type: TABLE Owner: syan
--

CREATE TABLE "med_qty" (
	"qty" integer,
	"repeats" integer,
	"meds_id" integer
)
INHERITS ("durable");

--
-- TOC Entry ID 231 (OID 38568)
--
-- Name: allergy Type: TABLE Owner: syan
--

CREATE TABLE "allergy" (
	"drug" character varying(40),
	"drug_ref" integer
)
INHERITS ("phx_event");

--
-- TOC Entry ID 232 (OID 38609)
--
-- Name: sochx Type: TABLE Owner: syan
--

CREATE TABLE "sochx" (
	"informant" character varying(30)
)
INHERITS ("basic_context");

--
-- TOC Entry ID 233 (OID 38647)
--
-- Name: fhx Type: TABLE Owner: syan
--

CREATE TABLE "fhx" (
	"relative" character varying(30),
	"relation_type_id" integer,
	"relation_rec_id" integer,
	"age" integer,
	"disease_id" integer
)
INHERITS ("basic_context");

--
-- TOC Entry ID 234 (OID 38689)
--
-- Name: habit_type Type: TABLE Owner: syan
--

CREATE TABLE "habit_type" (
	"ht_id" integer DEFAULT nextval('habit_type_seq'::text) NOT NULL,
	"name" character varying(30),
	Constraint "habit_type_pkey" Primary Key ("ht_id")
)
INHERITS ("clin_record");

--
-- TOC Entry ID 235 (OID 38728)
--
-- Name: habit Type: TABLE Owner: syan
--

CREATE TABLE "habit" (
	"habit_id" integer DEFAULT nextval('habit_seq'::text) NOT NULL,
	"type" integer,
	"amt" numeric(4,1),
	"unit" character varying(10),
	Constraint "habit_pkey" Primary Key ("habit_id")
)
INHERITS ("durable");

--
-- TOC Entry ID 236 (OID 38777)
--
-- Name: ix_type Type: TABLE Owner: syan
--

CREATE TABLE "ix_type" (
	"dept" character varying(30)
)
INHERITS ("clin_record");

--
-- TOC Entry ID 237 (OID 38811)
--
-- Name: ixphx Type: TABLE Owner: syan
--

CREATE TABLE "ixphx" (
	"reason" character varying(40)
)
INHERITS ("phx_event");

--
-- TOC Entry ID 238 (OID 38851)
--
-- Name: problem Type: TABLE Owner: syan
--

CREATE TABLE "problem" (
	"rx_summary" character varying(40)
)
INHERITS ("durable");

--
-- TOC Entry ID 239 (OID 38893)
--
-- Name: problem_phx_link Type: TABLE Owner: syan
--

CREATE TABLE "problem_phx_link" (
	"phx_id" integer,
	"prob_id" integer
)
INHERITS ("clin_record");

--
-- TOC Entry ID 240 (OID 39021)
--
-- Name: person_view3 Type: VIEW Owner: syan
--

CREATE VIEW "person_view3" as SELECT n.firstnames, n.lastnames, i.dob, i.gender, i.id, a.street, a.addendum, p.phone1, p.phone2, i.pupic FROM identity i, "names" n, address a, identities_addresses ia, phone p WHERE ((((i.id = ia.id_identity) AND (a.id = ia.id_address)) AND (n.id_identity = i.id)) AND (p.id_identity = i.id));

--
-- TOC Entry ID 241 (OID 39062)
--
-- Name: meds_view Type: VIEW Owner: syan
--

CREATE VIEW "meds_view" as SELECT m.clin_id, dp.name AS drug, md.dose, du.description AS unit, dr.description AS route, mt.descript AS freq, mq.qty, mq.repeats, md.started, md.fin AS ceased, m.patient AS patient_id FROM meds m, drug_presentation dp, med_dose md, amount_unit du, drug_route dr, med_timing mt, med_qty mq WHERE ((((((m.drug_info = dp.id) AND (m.clin_id = md.meds_id)) AND (m.clin_id = mq.meds_id)) AND (dp.route = dr.id)) AND (dp.amount_unit = du.id)) AND (md.timing = mt.clin_id));

--
-- TOC Entry ID 242 (OID 39161)
--
-- Name: person_view2 Type: VIEW Owner: syan
--

CREATE VIEW "person_view2" as SELECT n.firstnames, n.lastnames, to_char("timestamp"(i.dob), 'DD-MM-YYYY'::text) AS dob, i.gender, i.id, a.street, a.addendum, p.phone1, p.phone2, i.pupic FROM identity i, "names" n, address a, identities_addresses ia, phone p WHERE ((((i.id = ia.id_identity) AND (a.id = ia.id_address)) AND (n.id_identity = i.id)) AND (p.id_identity = i.id));

--
-- TOC Entry ID 243 (OID 39285)
--
-- Name: revocation Type: TABLE Owner: syan
--

CREATE TABLE "revocation" (
	"revoked" integer NOT NULL,
	"replacing_id" integer
)
INHERITS ("clin_record");

--
-- TOC Entry ID 244 (OID 39336)
--
-- Name: phx_view Type: VIEW Owner: syan
--

CREATE VIEW "phx_view" as SELECT to_char("timestamp"(p.started), 'DD-MON-YYYY'::text) AS date, '' AS fin, p.description, p.place, p.extra, p.patient AS patient_id, p.clin_id FROM phx_event p UNION SELECT to_char("timestamp"(phx_durable.started), 'DD-MON-YYYY'::text) AS date, to_char("timestamp"(phx_durable.fin), 'DD-MON-YYYY'::text) AS fin, phx_durable.description, phx_durable.place, phx_durable.extra, phx_durable.patient AS patient_id, phx_durable.clin_id FROM phx_durable;

