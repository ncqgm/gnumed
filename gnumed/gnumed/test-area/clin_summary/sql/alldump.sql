--
-- Selected TOC Entries:
--
\connect - syan
--
-- TOC Entry ID 254 (OID 35677)
--
-- Name: "plpgsql_call_handler" () Type: FUNCTION Owner: syan
--

CREATE FUNCTION "plpgsql_call_handler" () RETURNS opaque AS '/usr/lib/plpgsql.so', 'plpgsql_call_handler' LANGUAGE 'C';

--
-- TOC Entry ID 255 (OID 35678)
--
-- Name: plpgsql Type: PROCEDURAL LANGUAGE Owner: 
--

CREATE TRUSTED PROCEDURAL LANGUAGE 'plpgsql' HANDLER "plpgsql_call_handler" LANCOMPILER 'PL/pgSQL';

--
-- TOC Entry ID 2 (OID 35679)
--
-- Name: clinician_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "clinician_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 80 (OID 35698)
--
-- Name: clinician Type: TABLE Owner: syan
--

CREATE TABLE "clinician" (
	"name" text NOT NULL,
	"bio" text,
	"photo" text,
	"id" integer DEFAULT nextval('"clinician_id_seq"'::text) NOT NULL
);

--
-- TOC Entry ID 84 (OID 35698)
--
-- Name: TABLE "clinician" Type: COMMENT Owner: 
--

COMMENT ON TABLE "clinician" IS 'Table of all clinicians';

--
-- TOC Entry ID 81 (OID 35700)
--
-- Name: COLUMN "clinician"."name" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "clinician"."name" IS 'Full name';

--
-- TOC Entry ID 82 (OID 35701)
--
-- Name: COLUMN "clinician"."bio" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "clinician"."bio" IS 'Short CV for display on Website, in HTML';

--
-- TOC Entry ID 83 (OID 35702)
--
-- Name: COLUMN "clinician"."photo" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "clinician"."photo" IS 'Photograph as JPEG';

--
-- TOC Entry ID 4 (OID 35731)
--
-- Name: session_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "session_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 85 (OID 35750)
--
-- Name: session Type: TABLE Owner: syan
--

CREATE TABLE "session" (
	"clinician" integer NOT NULL,
	"start" time NOT NULL,
	"finish" time NOT NULL,
	"day" smallint NOT NULL,
	"consult_time" interval NOT NULL,
	"id" integer DEFAULT nextval('"session_id_seq"'::text) NOT NULL
);

--
-- TOC Entry ID 90 (OID 35750)
--
-- Name: TABLE "session" Type: COMMENT Owner: 
--

COMMENT ON TABLE "session" IS 'All sessions of all doctors in the clinic';

--
-- TOC Entry ID 86 (OID 35753)
--
-- Name: COLUMN "session"."start" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "session"."start" IS 'Time the session starts (the first appointment)';

--
-- TOC Entry ID 87 (OID 35754)
--
-- Name: COLUMN "session"."finish" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "session"."finish" IS 'Time the session finishes (no appointments after this)';

--
-- TOC Entry ID 88 (OID 35755)
--
-- Name: COLUMN "session"."day" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "session"."day" IS 'Day of the week on which the clinic is held, 0=Sunday, 1=Monday, etc.';

--
-- TOC Entry ID 89 (OID 35756)
--
-- Name: COLUMN "session"."consult_time" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "session"."consult_time" IS 'The spacing of the appointments';

--
-- TOC Entry ID 91 (OID 35771)
--
-- Name: holiday Type: TABLE Owner: syan
--

CREATE TABLE "holiday" (
	"clinician" integer NOT NULL,
	"start" timestamp with time zone NOT NULL,
	"finish" timestamp with time zone NOT NULL
);

--
-- TOC Entry ID 94 (OID 35771)
--
-- Name: TABLE "holiday" Type: COMMENT Owner: 
--

COMMENT ON TABLE "holiday" IS 'Details of holidays about to be taken. Should be used even for short time, 
i.e. an afernoon off';

--
-- TOC Entry ID 92 (OID 35774)
--
-- Name: COLUMN "holiday"."start" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "holiday"."start" IS 'Date and time from which appointments are not accepted';

--
-- TOC Entry ID 93 (OID 35775)
--
-- Name: COLUMN "holiday"."finish" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "holiday"."finish" IS 'Date and time from which appointments can be booked';

--
-- TOC Entry ID 95 (OID 35786)
--
-- Name: appointment Type: TABLE Owner: syan
--

CREATE TABLE "appointment" (
	"patient_name" character varying(50) NOT NULL,
	"session" integer NOT NULL,
	"time" timestamp with time zone NOT NULL,
	"length" smallint NOT NULL,
	"booked" timestamp with time zone NOT NULL,
	"patient_ur" integer
);

--
-- TOC Entry ID 102 (OID 35786)
--
-- Name: TABLE "appointment" Type: COMMENT Owner: 
--

COMMENT ON TABLE "appointment" IS 'All appointments made';

--
-- TOC Entry ID 96 (OID 35788)
--
-- Name: COLUMN "appointment"."patient_name" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "appointment"."patient_name" IS 'Name of patient as surname,, first name. For speed so don''t have to query
patient server all the time.';

--
-- TOC Entry ID 97 (OID 35789)
--
-- Name: COLUMN "appointment"."session" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "appointment"."session" IS 'ID of session under which pt is booked';

--
-- TOC Entry ID 98 (OID 35790)
--
-- Name: COLUMN "appointment"."time" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "appointment"."time" IS 'date/time of booking';

--
-- TOC Entry ID 99 (OID 35791)
--
-- Name: COLUMN "appointment"."length" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "appointment"."length" IS 'length of booking 1=normal booking, 2=double-length consult,, 0=dummy entry 
for a previous double consult.';

--
-- TOC Entry ID 100 (OID 35792)
--
-- Name: COLUMN "appointment"."booked" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "appointment"."booked" IS 'Time booking was made. Set by trigger';

--
-- TOC Entry ID 101 (OID 35793)
--
-- Name: COLUMN "appointment"."patient_ur" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "appointment"."patient_ur" IS 'UR code, reference to central patient table. What should the type be??. Can be NULL 
for new patients';

--
-- TOC Entry ID 103 (OID 35808)
--
-- Name: list Type: TABLE Owner: syan
--

CREATE TABLE "list" (
	"time" time,
	"session" integer
);

--
-- TOC Entry ID 106 (OID 35808)
--
-- Name: TABLE "list" Type: COMMENT Owner: 
--

COMMENT ON TABLE "list" IS 'Auto-generated list, with one entry for each ''slot'' available in the 
doctor''s timetable.';

--
-- TOC Entry ID 104 (OID 35810)
--
-- Name: COLUMN "list"."time" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "list"."time" IS 'Time during the day of consult.';

--
-- TOC Entry ID 105 (OID 35811)
--
-- Name: COLUMN "list"."session" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "list"."session" IS 'ID of session referred to';

--
-- TOC Entry ID 256 (OID 35822)
--
-- Name: "list_create" () Type: FUNCTION Owner: syan
--

CREATE FUNCTION "list_create" () RETURNS opaque AS '
DECLARE
	curr TIME;
BEGIN
	IF TG_OP = ''DELETE'' OR TG_OP = ''UPDATE'' THEN
	-- delete entries in list.
	   DELETE FROM list WHERE list.session = OLD.id;
	END IF;
	IF TG_OP = ''INSERT'' OR TG_OP = ''UPDATE'' THEN
	   curr := NEW.start;    
	   WHILE curr < NEW.finish LOOP
		 INSERT INTO list VALUES (curr, NEW.id);
		 curr := curr + NEW.consult_time;
	   END LOOP;
	   RETURN NEW;
	END IF;
	RETURN NULL;
END;
' LANGUAGE 'plpgsql';

--
-- TOC Entry ID 257 (OID 35823)
--
-- Name: "new_appointment" () Type: FUNCTION Owner: syan
--

CREATE FUNCTION "new_appointment" () RETURNS opaque AS '
DECLARE
	double_time TIMESTAMP;
	consult_length INTERVAL;
	dummy RECORD;
BEGIN
	IF TG_OP = ''DELETE'' OR TG_OP = ''UPDATE'' THEN
	   IF OLD.length > 1 THEN
	      double_time:=OLD.time; -- delete all the extras on this appt
	      SELECT consult_time INTO consult_length FROM session
	      WHERE session.id = OLD.session; 
	      FOR i IN 2..OLD.length LOOP
	      -- go through and delete the extras for double appt.
		  double_time := double_time + consult_length;
		  -- this will recur, but that''s OK. Note length=0
		  DELETE FROM appointment
			 WHERE patient_name = OLD.patient_name 
			 AND session = OLD.session 
			 AND time = double_time
			 AND length = 0
			AND (patient_ur ISNULL OR patient_ur = OLD.patient_ur);
	      END LOOP;
	   END IF;  
	END IF; 
	IF TG_OP = ''INSERT'' OR TG_OP = ''UPDATE'' THEN 
	   -- check not double-booked.
	   SELECT * INTO dummy FROM appointment WHERE 
	       session = NEW.session AND
	       time = NEW.time;
	   IF FOUND THEN
		 RAISE EXCEPTION ''Double booked'';
	   END IF; 
	   -- make sure appointment actually exists
	   SELECT * INTO dummy FROM list WHERE
	       list.session = NEW.session AND
	       list.time = time (NEW.time);
	   IF NOT FOUND THEN
	      RAISE EXCEPTION ''No such time'';
	   END IF; 
	   -- check not on holiday
	   SELECT * INTO dummy FROM holiday, session WHERE
	       holiday.clinician = session.clinician
	       AND session.id = NEW.session
	       AND holiday.start < NEW.time 
	       AND holiday.finish > NEW.time;
	   IF FOUND THEN
	      RAISE EXCEPTION ''Doctor on holiday'';
	   END IF; 
	   -- add doubles in appointment book
	   IF NEW.length > 1 THEN
	      SELECT consult_time INTO consult_length FROM session
	      WHERE session.id = NEW.session;
	      double_time := NEW.time;
	      FOR i IN 2..NEW.length LOOP
		  double_time := double_time + consult_length;
		  -- this will recur, but that''s OK. Note length=0
		  INSERT INTO appointment VALUES (NEW.patient_name, 
			 NEW.session, double_time, 0);
	      END LOOP;
	   END IF;
	   NEW.booked := now (); -- mark booking time 
	   RETURN NEW;
	END IF;
	RETURN OLD; -- only get here if TG_OP = ''DELETE''
END;
' LANGUAGE 'plpgsql';

--
-- TOC Entry ID 258 (OID 35824)
--
-- Name: "book" (integer,date,time) Type: FUNCTION Owner: syan
--

CREATE FUNCTION "book" (integer,date,time) RETURNS text AS '
DECLARE
	clinician ALIAS FOR $1;
	appt_date ALIAS FOR $2;
	appt_time ALIAS FOR $3;
	appt datetime;
	patient text;
	dummy RECORD; -- SELECTs *must be* "SELECT INTO" even if we don''t care about the result. 
BEGIN
	appt := timestamp (appt_date, appt_time);
	-- find if booked to other patient
	SELECT appointment.patient_name INTO patient FROM appointment, session
	WHERE appointment.time = appt AND
	      appointment.session = session.id AND
	      session.clinician = clinician;
	IF FOUND THEN
	   RETURN patient;
	END IF;
	-- check not on holiday
	SELECT * INTO dummy FROM holiday WHERE
	       holiday.clinician = clinician
	       AND holiday.start < appt 
	       AND holiday.finish > appt; 
	IF FOUND THEN
	   RETURN NULL;
	END IF; 
	-- find if slot actually exist.
	SELECT * INTO dummy FROM list, session WHERE
	       session.clinician = clinician AND
	       float8 (session.day) = extract (dow from appt_date) AND
	       -- extract returns float8 for the day of week (????)
	       -- needs to match on other side of =
	       session.id = list.session AND
	       list.time = appt_time;
	IF FOUND THEN
	   RETURN ''FREE'';
	ELSE
	   RETURN NULL;
	END IF;
END;' LANGUAGE 'plpgsql';

--
-- TOC Entry ID 259 (OID 35824)
--
-- Name: FUNCTION "book" ( integer,date,time ) Type: COMMENT Owner: 
--

COMMENT ON FUNCTION "book" ( integer,date,time ) IS 'Returns the name of a patient booked for a particular doctor at a particular
time. If no patient booked, returns the string ''FREE''. If no booking is 
possible, (because of holiday or no session) returns NULL';

--
-- TOC Entry ID 260 (OID 35826)
--
-- Name: "isfree" (integer,date,time) Type: FUNCTION Owner: syan
--

CREATE FUNCTION "isfree" (integer,date,time) RETURNS boolean AS '
DECLARE
	sessionx ALIAS FOR $1;
	appt_date ALIAS FOR $2;
	appt_time ALIAS FOR $3;
	appt datetime;
	patient text; -- PL/SQL allows SELECT..INTO but not plain select, need dummy variable.
BEGIN
	appt:= timestamp (appt_date, appt_time);
	SELECT appointment.patient_name INTO patient FROM appointment
	WHERE appointment.time = appt AND
	      appointment.session = sessionx;
	RETURN NOT FOUND;
END;' LANGUAGE 'plpgsql';

--
-- TOC Entry ID 261 (OID 35826)
--
-- Name: FUNCTION "isfree" ( integer,date,time ) Type: COMMENT Owner: 
--

COMMENT ON FUNCTION "isfree" ( integer,date,time ) IS 'Checks if a patient is booked for the specified time. Returns true if no 
patient booked, false if booked.';

--
-- TOC Entry ID 262 (OID 35828)
--
-- Name: "isnotonholiday" (integer,date,time) Type: FUNCTION Owner: syan
--

CREATE FUNCTION "isnotonholiday" (integer,date,time) RETURNS boolean AS '
DECLARE
	clinician ALIAS FOR $1;
	appt_date ALIAS FOR $2;
	appt_time ALIAS FOR $3;
	appt datetime;
	dummy RECORD;
BEGIN
	appt :=timestamp (appt_date, appt_time); 
	SELECT * INTO dummy FROM holiday WHERE
	       holiday.clinician = clinician
	       AND holiday.start <= appt -- date within holiday range.
	       AND holiday.finish > appt; 
	RETURN NOT FOUND;
END;' LANGUAGE 'plpgsql';

--
-- TOC Entry ID 263 (OID 35828)
--
-- Name: FUNCTION "isnotonholiday" ( integer,date,time ) Type: COMMENT Owner: 
--

COMMENT ON FUNCTION "isnotonholiday" ( integer,date,time ) IS 'Returns true if doctor is NOT on holiday at the specified time.';

--
-- TOC Entry ID 264 (OID 35830)
--
-- Name: "get_first_avail" (integer,date) Type: FUNCTION Owner: syan
--

CREATE FUNCTION "get_first_avail" (integer,date) RETURNS timestamp with time zone AS '
DECLARE
	clinician ALIAS FOR $1;
	start ALIAS FOR $2;
	day FLOAT8;
	avail_epoch INTEGER; -- time as UNIX type
	start_epoch INTEGER;
	avail_date DATE;
	avail_time TIME;
	dummy RECORD; -- PL/SQL allows SELECT..INTO but not select.
BEGIN
	SELECT * INTO dummy FROM session WHERE session.clinician = clinician;
	IF NOT FOUND THEN
	   RAISE EXCEPTION ''clinician has no session'';
	   -- check sessions listed, (otherwise infinite loop!)
	END IF;
	start_epoch = extract (epoch from start); -- convert to UNIX time (SQL
	-- time cannot be incremented without weird bugs)
	avail_epoch := start_epoch; 
	day := extract (dow from start); -- find day of week.
	LOOP
		avail_date := date (avail_epoch); -- convert to SQL time
		SELECT min (list.time) INTO avail_time FROM list, session WHERE
		       session.clinician = clinician AND -- doctor''s sessions
		       float8 (session.day) = day AND -- right day of week
		       list.session = session.id AND -- slots of session
		       isfree (session.id, avail_date, list.time) AND -- check is free
		       isnotonholiday (clinician, avail_date, list.time) AND -- check not on holiday
		       timestamp (avail_date, list.time) > now (); -- must not be before now (), free appts past are unless.
		IF NOT avail_time ISNULL THEN -- appt found!
		   RETURN timestamp (avail_date, avail_time);
		END IF;
		day := day + 1.0; -- next day of week
		IF day = 7.0 THEN
		   day := 0.0;
		END IF;
		avail_epoch := avail_epoch + 86400; -- (one day in seconds) increment day.
		IF avail_epoch - start_epoch > 315360000 THEN -- 10 years 
		   -- in seconds. Prevents infinite loops. 
		   RAISE EXCEPTION ''10 years into the future: stop'';
		END IF;
	END LOOP;
END;' LANGUAGE 'plpgsql';

--
-- TOC Entry ID 265 (OID 35830)
--
-- Name: FUNCTION "get_first_avail" ( integer,date ) Type: COMMENT Owner: 
--

COMMENT ON FUNCTION "get_first_avail" ( integer,date ) IS 'Starting at date, the function searches forward through time until
a time is found available for an appointment.
WARNING: potentially very slow.';

--
-- TOC Entry ID 107 (OID 35843)
--
-- Name: first_available Type: VIEW Owner: syan
--

CREATE VIEW "first_available" as SELECT clinician.name, get_first_avail(clinician.id, date(now())) AS get_first_avail FROM clinician;

--
-- TOC Entry ID 108 (OID 35832)
--
-- Name: VIEW "first_available" Type: COMMENT Owner: 
--

COMMENT ON VIEW "first_available" IS 'Convience view for a list of all doctors and when they are available.';

--
-- TOC Entry ID 6 (OID 35845)
--
-- Name: doc_type_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "doc_type_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 109 (OID 35864)
--
-- Name: doc_type Type: TABLE Owner: syan
--

CREATE TABLE "doc_type" (
	"id" integer DEFAULT nextval('"doc_type_id_seq"'::text) NOT NULL,
	"name" character varying(40),
	Constraint "doc_type_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 8 (OID 35879)
--
-- Name: db_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "db_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 110 (OID 35898)
--
-- Name: db Type: TABLE Owner: syan
--

CREATE TABLE "db" (
	"id" integer DEFAULT nextval('"db_id_seq"'::text) NOT NULL,
	"name" character(35),
	"port" integer DEFAULT 5432,
	"host" character varying(255) DEFAULT 'localhost',
	"opt" character varying(255) DEFAULT '',
	"tty" character varying(255) DEFAULT '',
	Constraint "db_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 114 (OID 35898)
--
-- Name: TABLE "db" Type: COMMENT Owner: 
--

COMMENT ON TABLE "db" IS 'basic database information';

--
-- TOC Entry ID 111 (OID 35901)
--
-- Name: COLUMN "db"."name" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "db"."name" IS 'name of the database';

--
-- TOC Entry ID 112 (OID 35902)
--
-- Name: COLUMN "db"."port" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "db"."port" IS 'port number of the server hosting this database';

--
-- TOC Entry ID 113 (OID 35903)
--
-- Name: COLUMN "db"."host" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "db"."host" IS 'host name or IP number of the server hosting this database';

--
-- TOC Entry ID 10 (OID 35925)
--
-- Name: distributed_db_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "distributed_db_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 115 (OID 35944)
--
-- Name: distributed_db Type: TABLE Owner: syan
--

CREATE TABLE "distributed_db" (
	"id" integer DEFAULT nextval('"distributed_db_id_seq"'::text) NOT NULL,
	"name" character(35),
	Constraint "distributed_db_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 116 (OID 35944)
--
-- Name: TABLE "distributed_db" Type: COMMENT Owner: 
--

COMMENT ON TABLE "distributed_db" IS 'Enumerates all possibly available distributed servers. Naming needs approval by gnumed administrators!';

--
-- TOC Entry ID 12 (OID 35960)
--
-- Name: config_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "config_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 117 (OID 35979)
--
-- Name: config Type: TABLE Owner: syan
--

CREATE TABLE "config" (
	"id" integer DEFAULT nextval('"config_id_seq"'::text) NOT NULL,
	"profile" character(25) DEFAULT 'default',
	"username" character(25) DEFAULT "current_user"(),
	"ddb" integer,
	"db" integer,
	"crypt_pwd" character varying(255),
	"crypt_algo" character varying(255) DEFAULT 'RIJNDAEL',
	"pwd_hash" character varying(255),
	"hash_algo" character varying(255) DEFAULT 'RIPEMD160',
	Constraint "config_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 126 (OID 35979)
--
-- Name: TABLE "config" Type: COMMENT Owner: 
--

COMMENT ON TABLE "config" IS 'minimal gnumed database configuration information';

--
-- TOC Entry ID 118 (OID 35982)
--
-- Name: COLUMN "config"."profile" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."profile" IS 'one user may have different configuration profiles depending on role, need and location';

--
-- TOC Entry ID 119 (OID 35983)
--
-- Name: COLUMN "config"."username" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."username" IS 'user name as used within the gnumed system';

--
-- TOC Entry ID 120 (OID 35984)
--
-- Name: COLUMN "config"."ddb" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."ddb" IS 'reference to one of the allowed distrbuted servers';

--
-- TOC Entry ID 121 (OID 35985)
--
-- Name: COLUMN "config"."db" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."db" IS 'reference to the implementation details of the distributed server';

--
-- TOC Entry ID 122 (OID 35986)
--
-- Name: COLUMN "config"."crypt_pwd" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."crypt_pwd" IS 'password for user and database, encrypted';

--
-- TOC Entry ID 123 (OID 35987)
--
-- Name: COLUMN "config"."crypt_algo" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."crypt_algo" IS 'encryption algorithm used for password encryption';

--
-- TOC Entry ID 124 (OID 35988)
--
-- Name: COLUMN "config"."pwd_hash" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."pwd_hash" IS 'hash of the unencrypted password';

--
-- TOC Entry ID 125 (OID 35989)
--
-- Name: COLUMN "config"."hash_algo" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "config"."hash_algo" IS 'algorithm used for password hashing';

--
-- TOC Entry ID 14 (OID 36014)
--
-- Name: class_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "class_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 127 (OID 36033)
--
-- Name: class Type: TABLE Owner: syan
--

CREATE TABLE "class" (
	"id" integer DEFAULT nextval('"class_id_seq"'::text) NOT NULL,
	"name" character varying(60),
	"pharmacology" text,
	"superclass" integer,
	Constraint "class_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 16 (OID 36065)
--
-- Name: substance_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "substance_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 128 (OID 36084)
--
-- Name: substance Type: TABLE Owner: syan
--

CREATE TABLE "substance" (
	"id" integer DEFAULT nextval('"substance_id_seq"'::text) NOT NULL,
	"name" character varying(60),
	"pharmacology" text,
	"class" integer,
	Constraint "substance_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 18 (OID 36116)
--
-- Name: pregnancy_cat_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "pregnancy_cat_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 129 (OID 36135)
--
-- Name: pregnancy_cat Type: TABLE Owner: syan
--

CREATE TABLE "pregnancy_cat" (
	"id" integer DEFAULT nextval('"pregnancy_cat_id_seq"'::text) NOT NULL,
	"code" character(3),
	"description" text,
	"comment" text,
	Constraint "pregnancy_cat_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 20 (OID 36167)
--
-- Name: breastfeeding_cat_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "breastfeeding_cat_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 130 (OID 36186)
--
-- Name: breastfeeding_cat Type: TABLE Owner: syan
--

CREATE TABLE "breastfeeding_cat" (
	"id" integer DEFAULT nextval('"breastfeeding_cat_id_seq"'::text) NOT NULL,
	"code" character(3),
	"description" text,
	"comment" text,
	Constraint "breastfeeding_cat_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 131 (OID 36218)
--
-- Name: obstetric_codes Type: TABLE Owner: syan
--

CREATE TABLE "obstetric_codes" (
	"drug_id" integer,
	"preg_code" integer,
	"brst_code" integer
);

--
-- TOC Entry ID 22 (OID 36230)
--
-- Name: amount_unit_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "amount_unit_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 132 (OID 36249)
--
-- Name: amount_unit Type: TABLE Owner: syan
--

CREATE TABLE "amount_unit" (
	"id" integer DEFAULT nextval('"amount_unit_id_seq"'::text) NOT NULL,
	"description" character varying(20),
	Constraint "amount_unit_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 133 (OID 36249)
--
-- Name: TABLE "amount_unit" Type: COMMENT Owner: 
--

COMMENT ON TABLE "amount_unit" IS 'Example: ml, each, ..';

--
-- TOC Entry ID 24 (OID 36265)
--
-- Name: drug_unit_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "drug_unit_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 134 (OID 36284)
--
-- Name: drug_unit Type: TABLE Owner: syan
--

CREATE TABLE "drug_unit" (
	"id" integer DEFAULT nextval('"drug_unit_id_seq"'::text) NOT NULL,
	"is_si" boolean DEFAULT 'y',
	"description" character varying(20),
	Constraint "drug_unit_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 136 (OID 36284)
--
-- Name: TABLE "drug_unit" Type: COMMENT Owner: 
--

COMMENT ON TABLE "drug_unit" IS 'true if it is a System International (SI) compliant unit';

--
-- TOC Entry ID 135 (OID 36287)
--
-- Name: COLUMN "drug_unit"."is_si" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "drug_unit"."is_si" IS 'Example: mg, mcg, ml, U, IU, ...';

--
-- TOC Entry ID 26 (OID 36303)
--
-- Name: drug_route_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "drug_route_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 137 (OID 36322)
--
-- Name: drug_route Type: TABLE Owner: syan
--

CREATE TABLE "drug_route" (
	"id" integer DEFAULT nextval('"drug_route_id_seq"'::text) NOT NULL,
	"description" character varying(60),
	"abbrev" character varying(10),
	Constraint "drug_route_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 138 (OID 36322)
--
-- Name: TABLE "drug_route" Type: COMMENT Owner: 
--

COMMENT ON TABLE "drug_route" IS 'Examples: oral, i.m., i.v., s.c.';

--
-- TOC Entry ID 28 (OID 36338)
--
-- Name: drug_presentation_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "drug_presentation_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 139 (OID 36357)
--
-- Name: drug_presentation Type: TABLE Owner: syan
--

CREATE TABLE "drug_presentation" (
	"id" integer DEFAULT nextval('"drug_presentation_id_seq"'::text) NOT NULL,
	"name" character varying(30),
	"route" integer,
	"amount_unit" integer,
	Constraint "drug_presentation_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 30 (OID 36374)
--
-- Name: drug_package_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "drug_package_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 140 (OID 36393)
--
-- Name: drug_package Type: TABLE Owner: syan
--

CREATE TABLE "drug_package" (
	"id" integer DEFAULT nextval('"drug_package_id_seq"'::text) NOT NULL,
	"presentation" integer,
	"packsize" integer,
	"amount" double precision,
	"max_rpts" integer,
	"description" character varying(100),
	Constraint "drug_package_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 141 (OID 36412)
--
-- Name: link_subst_package Type: TABLE Owner: syan
--

CREATE TABLE "link_subst_package" (
	"package" integer,
	"substance" integer,
	"unit" integer,
	"amount" double precision
);

--
-- TOC Entry ID 32 (OID 36425)
--
-- Name: drug_manufacturer_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "drug_manufacturer_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 142 (OID 36444)
--
-- Name: drug_manufacturer Type: TABLE Owner: syan
--

CREATE TABLE "drug_manufacturer" (
	"id" integer DEFAULT nextval('"drug_manufacturer_id_seq"'::text) NOT NULL,
	"name" character varying(60),
	Constraint "drug_manufacturer_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 143 (OID 36444)
--
-- Name: TABLE "drug_manufacturer" Type: COMMENT Owner: 
--

COMMENT ON TABLE "drug_manufacturer" IS 'Name of a drug company. Details like address etc. in separate table';

--
-- TOC Entry ID 34 (OID 36460)
--
-- Name: brand_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "brand_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 144 (OID 36479)
--
-- Name: brand Type: TABLE Owner: syan
--

CREATE TABLE "brand" (
	"id" integer DEFAULT nextval('"brand_id_seq"'::text) NOT NULL,
	"drug_manufacturer_id" integer NOT NULL,
	"brand_name" character varying(60),
	Constraint "brand_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 145 (OID 36495)
--
-- Name: link_brand_drug Type: TABLE Owner: syan
--

CREATE TABLE "link_brand_drug" (
	"brand_id" integer,
	"drug_id" integer,
	"price" money
);

--
-- TOC Entry ID 36 (OID 36507)
--
-- Name: drug_flags_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "drug_flags_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 146 (OID 36526)
--
-- Name: drug_flags Type: TABLE Owner: syan
--

CREATE TABLE "drug_flags" (
	"id" integer DEFAULT nextval('"drug_flags_id_seq"'::text) NOT NULL,
	"description" character varying(60),
	"comment" text,
	Constraint "drug_flags_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 147 (OID 36526)
--
-- Name: TABLE "drug_flags" Type: COMMENT Owner: 
--

COMMENT ON TABLE "drug_flags" IS 'important searchable information relating to a drug such as sugar free, gluten free, ...';

--
-- TOC Entry ID 148 (OID 36558)
--
-- Name: link_flag_package Type: TABLE Owner: syan
--

CREATE TABLE "link_flag_package" (
	"flag_id" integer,
	"pack_id" integer
);

--
-- TOC Entry ID 38 (OID 36569)
--
-- Name: payor_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "payor_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 149 (OID 36588)
--
-- Name: payor Type: TABLE Owner: syan
--

CREATE TABLE "payor" (
	"id" integer DEFAULT nextval('"payor_id_seq"'::text) NOT NULL,
	"country" character(2),
	"name" character varying(50),
	"state" boolean
);

--
-- TOC Entry ID 150 (OID 36602)
--
-- Name: restriction Type: TABLE Owner: syan
--

CREATE TABLE "restriction" (
	"drug_id" integer,
	"payor_id" integer,
	"indication" text,
	"authority" boolean
);

--
-- TOC Entry ID 40 (OID 36630)
--
-- Name: severity_code_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "severity_code_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 151 (OID 36649)
--
-- Name: severity_code Type: TABLE Owner: syan
--

CREATE TABLE "severity_code" (
	"id" integer DEFAULT nextval('"severity_code_id_seq"'::text) NOT NULL,
	"code" character(3),
	"description" text,
	Constraint "severity_code_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 152 (OID 36649)
--
-- Name: TABLE "severity_code" Type: COMMENT Owner: 
--

COMMENT ON TABLE "severity_code" IS 'e.g. (contraindicated) (potentially life threatening) (not advisable) (caution) ...';

--
-- TOC Entry ID 42 (OID 36681)
--
-- Name: interaction_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "interaction_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 153 (OID 36700)
--
-- Name: interaction Type: TABLE Owner: syan
--

CREATE TABLE "interaction" (
	"id" integer DEFAULT nextval('"interaction_id_seq"'::text) NOT NULL,
	"comment" text,
	"severity" integer,
	Constraint "interaction_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 154 (OID 36731)
--
-- Name: link_drug_interaction Type: TABLE Owner: syan
--

CREATE TABLE "link_drug_interaction" (
	"drug_id" integer NOT NULL,
	"class" boolean,
	"interaction_id" integer NOT NULL,
	"comment" text
);

--
-- TOC Entry ID 44 (OID 36759)
--
-- Name: disease_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "disease_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 155 (OID 36778)
--
-- Name: disease Type: TABLE Owner: syan
--

CREATE TABLE "disease" (
	"id" integer DEFAULT nextval('"disease_id_seq"'::text) NOT NULL,
	"name" character varying(100),
	"icd10" character(1)[]
);

--
-- TOC Entry ID 156 (OID 36782)
--
-- Name: COLUMN "disease"."icd10" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "disease"."icd10" IS 'ICD-10 code, if applicable';

--
-- TOC Entry ID 46 (OID 36807)
--
-- Name: indication_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "indication_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 157 (OID 36826)
--
-- Name: indication Type: TABLE Owner: syan
--

CREATE TABLE "indication" (
	"id" integer DEFAULT nextval('"indication_id_seq"'::text) NOT NULL,
	"drug" integer,
	"course" integer,
	"frequency" character(5) DEFAULT 'mane',
	"paed_dose" double precision,
	"min_dose" double precision,
	"max_dose" double precision,
	"comment" text,
	"line" integer,
	CONSTRAINT "indication_frequency" CHECK ((((((frequency = 'mane'::bpchar) OR (frequency = 'nocte'::bpchar)) OR (frequency = 'bd'::bpchar)) OR (frequency = 'tds'::bpchar)) OR (frequency = 'qid'::bpchar))),
	Constraint "indication_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 158 (OID 36865)
--
-- Name: link_disease_interaction Type: TABLE Owner: syan
--

CREATE TABLE "link_disease_interaction" (
	"disease_id" integer NOT NULL,
	"interaction_id" integer NOT NULL,
	"comment" text
);

--
-- TOC Entry ID 159 (OID 36865)
--
-- Name: TABLE "link_disease_interaction" Type: COMMENT Owner: 
--

COMMENT ON TABLE "link_disease_interaction" IS 'allows any number of drug-disease interactions for any given drug';

--
-- TOC Entry ID 48 (OID 36893)
--
-- Name: side_effect_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "side_effect_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 160 (OID 36912)
--
-- Name: side_effect Type: TABLE Owner: syan
--

CREATE TABLE "side_effect" (
	"id" integer DEFAULT nextval('"side_effect_id_seq"'::text) NOT NULL,
	"drug_id" integer NOT NULL,
	"class" boolean,
	"disease" integer,
	"comment" text,
	"frequency" integer,
	"severity" integer
);

--
-- TOC Entry ID 50 (OID 36944)
--
-- Name: audit_gis_audit_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "audit_gis_audit_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 161 (OID 36963)
--
-- Name: audit_gis Type: TABLE Owner: syan
--

CREATE TABLE "audit_gis" (
	"audit_id" integer DEFAULT nextval('"audit_gis_audit_id_seq"'::text) NOT NULL,
	Constraint "audit_gis_pkey" Primary Key ("audit_id")
);

--
-- TOC Entry ID 162 (OID 36963)
--
-- Name: TABLE "audit_gis" Type: COMMENT Owner: 
--

COMMENT ON TABLE "audit_gis" IS 'not for direct use - must be inherited by all auditable tables';

--
-- TOC Entry ID 163 (OID 36978)
--
-- Name: country Type: TABLE Owner: syan
--

CREATE TABLE "country" (
	"code" character(2) NOT NULL,
	"name" character varying(60),
	"deprecated" date,
	Constraint "country_pkey" Primary Key ("code")
);

--
-- TOC Entry ID 166 (OID 36978)
--
-- Name: TABLE "country" Type: COMMENT Owner: 
--

COMMENT ON TABLE "country" IS 'a countries name and international code';

--
-- TOC Entry ID 164 (OID 36980)
--
-- Name: COLUMN "country"."code" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "country"."code" IS 'international two character country code as per ISO 3166-1';

--
-- TOC Entry ID 165 (OID 36982)
--
-- Name: COLUMN "country"."deprecated" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "country"."deprecated" IS 'date when this state ceased officially to exist (if applicable)';

--
-- TOC Entry ID 52 (OID 36996)
--
-- Name: state_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "state_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 167 (OID 37015)
--
-- Name: state Type: TABLE Owner: syan
--

CREATE TABLE "state" (
	"id" integer DEFAULT nextval('"state_id_seq"'::text) NOT NULL,
	"code" character(10),
	"country" character(2),
	"name" character varying(60),
	"deprecated" date,
	Constraint "state_pkey" Primary Key ("id")
)
INHERITS ("audit_gis");

--
-- TOC Entry ID 170 (OID 37015)
--
-- Name: TABLE "state" Type: COMMENT Owner: 
--

COMMENT ON TABLE "state" IS 'state codes (country specific)';

--
-- TOC Entry ID 168 (OID 37019)
--
-- Name: COLUMN "state"."code" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "state"."code" IS '3 character long state code';

--
-- TOC Entry ID 169 (OID 37020)
--
-- Name: COLUMN "state"."country" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "state"."country" IS '2 character ISO 3166-1 country code';

--
-- TOC Entry ID 54 (OID 37040)
--
-- Name: urb_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "urb_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 171 (OID 37059)
--
-- Name: urb Type: TABLE Owner: syan
--

CREATE TABLE "urb" (
	"id" integer DEFAULT nextval('"urb_id_seq"'::text) NOT NULL,
	"statecode" integer,
	"postcode" character(8),
	"name" character varying(60),
	Constraint "urb_pkey" Primary Key ("id")
)
INHERITS ("audit_gis");

--
-- TOC Entry ID 175 (OID 37059)
--
-- Name: TABLE "urb" Type: COMMENT Owner: 
--

COMMENT ON TABLE "urb" IS 'cities, towns, dwellings ...';

--
-- TOC Entry ID 172 (OID 37063)
--
-- Name: COLUMN "urb"."statecode" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "urb"."statecode" IS 'reference to information about country and state';

--
-- TOC Entry ID 173 (OID 37064)
--
-- Name: COLUMN "urb"."postcode" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "urb"."postcode" IS 'the postcode';

--
-- TOC Entry ID 174 (OID 37065)
--
-- Name: COLUMN "urb"."name" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "urb"."name" IS 'the name of the city/town/dwelling';

--
-- TOC Entry ID 56 (OID 37084)
--
-- Name: street_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "street_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 176 (OID 37103)
--
-- Name: street Type: TABLE Owner: syan
--

CREATE TABLE "street" (
	"id" integer DEFAULT nextval('"street_id_seq"'::text) NOT NULL,
	"id_urb" integer,
	"name" character varying(60),
	Constraint "street_pkey" Primary Key ("id")
)
INHERITS ("audit_gis");

--
-- TOC Entry ID 179 (OID 37103)
--
-- Name: TABLE "street" Type: COMMENT Owner: 
--

COMMENT ON TABLE "street" IS 'street names, specific for distinct "urbs"';

--
-- TOC Entry ID 177 (OID 37107)
--
-- Name: COLUMN "street"."id_urb" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "street"."id_urb" IS 'reference to information postcode, city, country and state';

--
-- TOC Entry ID 178 (OID 37108)
--
-- Name: COLUMN "street"."name" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "street"."name" IS 'name of this city/town/dwelling';

--
-- TOC Entry ID 58 (OID 37126)
--
-- Name: address_type_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "address_type_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 180 (OID 37145)
--
-- Name: address_type Type: TABLE Owner: syan
--

CREATE TABLE "address_type" (
	"id" integer DEFAULT nextval('"address_type_id_seq"'::text) NOT NULL,
	"name" character(10) NOT NULL,
	Constraint "address_type_pkey" Primary Key ("id")
)
INHERITS ("audit_gis");

--
-- TOC Entry ID 181 (OID 37164)
--
-- Name: address_external_ref Type: TABLE Owner: syan
--

CREATE TABLE "address_external_ref" (
	"id" integer NOT NULL,
	"refcounter" integer DEFAULT 0,
	Constraint "address_external_ref_pkey" Primary Key ("id")
);

--
-- TOC Entry ID 182 (OID 37179)
--
-- Name: address_info Type: TABLE Owner: syan
--

CREATE TABLE "address_info" (
	"address_id" integer,
	"gps" character(30),
	"gps_grid" character(30),
	"mapref" character(30),
	"map" character(30),
	"howto_get_there" text,
	"comments" text
)
INHERITS ("audit_gis");

--
-- TOC Entry ID 60 (OID 37214)
--
-- Name: link_amount_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "link_amount_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 183 (OID 37233)
--
-- Name: link_amount Type: TABLE Owner: syan
--

CREATE TABLE "link_amount" (
	"convert_id" integer,
	"unit" integer,
	"amount" double precision,
	"id" integer DEFAULT nextval('"link_amount_id_seq"'::text) NOT NULL
);

--
-- TOC Entry ID 184 (OID 37247)
--
-- Name: pbsimport Type: TABLE Owner: syan
--

CREATE TABLE "pbsimport" (
	"drugtypecode" character(2),
	"atccode" character(7),
	"atctype" character(1),
	"atcprintopt" character(1),
	"pbscode" character(4),
	"restrictionflag" character(1),
	"cautionflag" character(1),
	"noteflag" character(1),
	"maxquantity" integer,
	"numrepeats" integer,
	"manufacturercode" character(2),
	"packsize" integer,
	"brandpricepremium" money,
	"thergrouppremium" money,
	"cwprice" money,
	"cwdprice" money,
	"thergroupprice" money,
	"thergroupdprice" money,
	"manufactprice" money,
	"manufactdprice" money,
	"maxvalsafetynet" money,
	"bioequivalence" character(1),
	"brandname" text,
	"genericname" text,
	"formandstrength" text
);

--
-- TOC Entry ID 62 (OID 37296)
--
-- Name: audit_identity_audit_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "audit_identity_audit_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 185 (OID 37315)
--
-- Name: audit_identity Type: TABLE Owner: syan
--

CREATE TABLE "audit_identity" (
	"audit_id" integer DEFAULT nextval('"audit_identity_audit_id_seq"'::text) NOT NULL,
	Constraint "audit_identity_pkey" Primary Key ("audit_id")
);

--
-- TOC Entry ID 186 (OID 37315)
--
-- Name: TABLE "audit_identity" Type: COMMENT Owner: 
--

COMMENT ON TABLE "audit_identity" IS 'not for direct use - must be inherited by all auditable tables';

--
-- TOC Entry ID 64 (OID 37330)
--
-- Name: identity_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "identity_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 187 (OID 37349)
--
-- Name: names Type: TABLE Owner: syan
--

CREATE TABLE "names" (
	"id" integer DEFAULT nextval('"names_id_seq"'::text) NOT NULL,
	"id_identity" integer,
	"active" boolean DEFAULT 't',
	"lastnames" character varying(80),
	"firstnames" character varying(255),
	"aka" character varying(80),
	"preferred" character varying(80),
	"title" character varying(80),
	Constraint "names_pkey" Primary Key ("id")
)
INHERITS ("audit_identity");

--
-- TOC Entry ID 193 (OID 37349)
--
-- Name: TABLE "names" Type: COMMENT Owner: 
--

COMMENT ON TABLE "names" IS 'all the names an identity is known under';

--
-- TOC Entry ID 188 (OID 37354)
--
-- Name: COLUMN "names"."active" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "names"."active" IS 'true if the name is still in use';

--
-- TOC Entry ID 189 (OID 37355)
--
-- Name: COLUMN "names"."lastnames" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "names"."lastnames" IS 'all last names of an identity in legal order';

--
-- TOC Entry ID 190 (OID 37356)
--
-- Name: COLUMN "names"."firstnames" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "names"."firstnames" IS 'all first names of an identity in legal order';

--
-- TOC Entry ID 191 (OID 37357)
--
-- Name: COLUMN "names"."aka" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "names"."aka" IS 'also known as ...';

--
-- TOC Entry ID 192 (OID 37358)
--
-- Name: COLUMN "names"."preferred" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "names"."preferred" IS 'the preferred first name, the name a person is usually called';

--
-- TOC Entry ID 66 (OID 37381)
--
-- Name: relation_types_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "relation_types_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 194 (OID 37400)
--
-- Name: relation_types Type: TABLE Owner: syan
--

CREATE TABLE "relation_types" (
	"id" integer DEFAULT nextval('"relation_types_id_seq"'::text) NOT NULL,
	"biological" boolean,
	"biol_verified" boolean DEFAULT 'f'::bool,
	"description" character varying(40),
	Constraint "relation_types_pkey" Primary Key ("id")
)
INHERITS ("audit_identity");

--
-- TOC Entry ID 198 (OID 37400)
--
-- Name: TABLE "relation_types" Type: COMMENT Owner: 
--

COMMENT ON TABLE "relation_types" IS 'types of biological and social relationships between an identities';

--
-- TOC Entry ID 195 (OID 37404)
--
-- Name: COLUMN "relation_types"."biological" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation_types"."biological" IS 'true id the relationship is biological (proven or reasonable assumption), else false';

--
-- TOC Entry ID 196 (OID 37405)
--
-- Name: COLUMN "relation_types"."biol_verified" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation_types"."biol_verified" IS 'ONLY set to true if there is genetic proof for this relationship';

--
-- TOC Entry ID 197 (OID 37406)
--
-- Name: COLUMN "relation_types"."description" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation_types"."description" IS 'plain text description of relationship';

--
-- TOC Entry ID 68 (OID 37426)
--
-- Name: relation_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "relation_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 199 (OID 37445)
--
-- Name: relation Type: TABLE Owner: syan
--

CREATE TABLE "relation" (
	"id" integer DEFAULT nextval('"relation_id_seq"'::text) NOT NULL,
	"id_identity" integer,
	"id_relative" integer,
	"id_relation_type" integer,
	"started" date,
	"ended" date,
	Constraint "relation_pkey" Primary Key ("id")
)
INHERITS ("audit_identity");

--
-- TOC Entry ID 204 (OID 37445)
--
-- Name: TABLE "relation" Type: COMMENT Owner: 
--

COMMENT ON TABLE "relation" IS 'biological and social relationships between an identity and other identities';

--
-- TOC Entry ID 200 (OID 37449)
--
-- Name: COLUMN "relation"."id_identity" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation"."id_identity" IS 'primary identity to whom the relationship applies';

--
-- TOC Entry ID 201 (OID 37450)
--
-- Name: COLUMN "relation"."id_relative" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation"."id_relative" IS 'referred identity of this relationship (e.g. "child" if id_identity points to the father and id_relation_type points to "parent")';

--
-- TOC Entry ID 202 (OID 37452)
--
-- Name: COLUMN "relation"."started" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation"."started" IS 'date when this relationship begun';

--
-- TOC Entry ID 203 (OID 37453)
--
-- Name: COLUMN "relation"."ended" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "relation"."ended" IS 'date when this relationship ended. Biological relationships do not end!';

--
-- TOC Entry ID 70 (OID 37473)
--
-- Name: identities_addresses_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "identities_addresses_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 205 (OID 37492)
--
-- Name: identities_addresses Type: TABLE Owner: syan
--

CREATE TABLE "identities_addresses" (
	"id" integer DEFAULT nextval('"identities_addresses_id_seq"'::text) NOT NULL,
	"id_identity" integer,
	"id_address" integer,
	"address_source" character(80),
	Constraint "identities_addresses_pkey" Primary Key ("id")
)
INHERITS ("audit_identity");

--
-- TOC Entry ID 209 (OID 37492)
--
-- Name: TABLE "identities_addresses" Type: COMMENT Owner: 
--

COMMENT ON TABLE "identities_addresses" IS 'a many-to-many pivot table linking addresses to identities';

--
-- TOC Entry ID 206 (OID 37496)
--
-- Name: COLUMN "identities_addresses"."id_identity" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identities_addresses"."id_identity" IS 'identity to whom the address belongs';

--
-- TOC Entry ID 207 (OID 37497)
--
-- Name: COLUMN "identities_addresses"."id_address" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identities_addresses"."id_address" IS 'address belonging to this identity';

--
-- TOC Entry ID 208 (OID 37498)
--
-- Name: COLUMN "identities_addresses"."address_source" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identities_addresses"."address_source" IS 'URL of some sort allowing to reproduce where the address is sourced from';

--
-- TOC Entry ID 72 (OID 37517)
--
-- Name: address_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "address_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 210 (OID 37536)
--
-- Name: address Type: TABLE Owner: syan
--

CREATE TABLE "address" (
	"id" integer DEFAULT nextval('"address_id_seq"'::text) NOT NULL,
	"addrtype" integer DEFAULT 1,
	"number" integer,
	"street" character(50),
	"addendum" text,
	Constraint "address_pkey" Primary Key ("id")
)
INHERITS ("audit_gis");

--
-- TOC Entry ID 74 (OID 37574)
--
-- Name: names_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "names_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 76 (OID 37593)
--
-- Name: phone_id_seq Type: SEQUENCE Owner: syan
--

CREATE SEQUENCE "phone_id_seq" start 1 increment 1 maxvalue 2147483647 minvalue 1  cache 1 ;

--
-- TOC Entry ID 211 (OID 37612)
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
-- TOC Entry ID 212 (OID 37632)
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
-- TOC Entry ID 218 (OID 37632)
--
-- Name: TABLE "identity" Type: COMMENT Owner: 
--

COMMENT ON TABLE "identity" IS 'represents the unique identity of a person';

--
-- TOC Entry ID 213 (OID 37636)
--
-- Name: COLUMN "identity"."pupic" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."pupic" IS 'Portable Unique Person Identification Code as per gnumed white papers';

--
-- TOC Entry ID 214 (OID 37637)
--
-- Name: COLUMN "identity"."gender" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."gender" IS '(m)ale, (f)emale, (h)ermaphrodite, (tm)transsexual phaenotype male, (tf)transsexual phaenotype female, (?)unknown';

--
-- TOC Entry ID 215 (OID 37639)
--
-- Name: COLUMN "identity"."dob" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."dob" IS 'date of birth';

--
-- TOC Entry ID 216 (OID 37640)
--
-- Name: COLUMN "identity"."cob" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."cob" IS 'country of birth as per date of birth, coded as 2 character ISO code';

--
-- TOC Entry ID 217 (OID 37641)
--
-- Name: COLUMN "identity"."deceased" Type: COMMENT Owner: 
--

COMMENT ON COLUMN "identity"."deceased" IS 'date when a person has died (if)';

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
	"freq" character varying(30)
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

--
-- TOC Entry ID 245 (OID 58976)
--
-- Name: drug_view2 Type: VIEW Owner: syan
--

CREATE VIEW "drug_view2" as SELECT s.name, ls.amount, du.description AS unit, dp.name AS presentation, dr.description, dpk.packsize, 'x', dpk.amount AS "no", dpk.max_rpts FROM substance s, link_subst_package ls, drug_unit du, drug_presentation dp, drug_route dr, drug_package dpk WHERE (((((ls.package = dpk.id) AND (ls.unit = du.id)) AND (ls.substance = s.id)) AND (dp.route = dr.id)) AND (dpk.presentation = dp.id));

--
-- TOC Entry ID 246 (OID 216801)
--
-- Name: allergy_view Type: VIEW Owner: syan
--

CREATE VIEW "allergy_view" as SELECT to_char("timestamp"(allergy.started), 'DD-MON-YYYY'::text) AS date, allergy.drug, allergy.extra, allergy.patient AS patient_id, allergy.clin_id FROM allergy;

--
-- Data for TOC Entry ID 266 (OID 35698)
--
-- Name: clinician Type: TABLE DATA Owner: syan
--


COPY "clinician"  FROM stdin;
\.
--
-- Data for TOC Entry ID 267 (OID 35750)
--
-- Name: session Type: TABLE DATA Owner: syan
--


COPY "session"  FROM stdin;
\.
--
-- Data for TOC Entry ID 268 (OID 35771)
--
-- Name: holiday Type: TABLE DATA Owner: syan
--


COPY "holiday"  FROM stdin;
\.
--
-- Data for TOC Entry ID 269 (OID 35786)
--
-- Name: appointment Type: TABLE DATA Owner: syan
--


COPY "appointment"  FROM stdin;
\.
--
-- Data for TOC Entry ID 270 (OID 35808)
--
-- Name: list Type: TABLE DATA Owner: syan
--


COPY "list"  FROM stdin;
\.
--
-- Data for TOC Entry ID 271 (OID 35864)
--
-- Name: doc_type Type: TABLE DATA Owner: syan
--


COPY "doc_type"  FROM stdin;
1	ultrasound
2	CT scan
3	MRT scan
4	referral letter
5	discharge summary
6	neuro exam
\.
--
-- Data for TOC Entry ID 272 (OID 35898)
--
-- Name: db Type: TABLE DATA Owner: syan
--


COPY "db"  FROM stdin;
\.
--
-- Data for TOC Entry ID 273 (OID 35944)
--
-- Name: distributed_db Type: TABLE DATA Owner: syan
--


COPY "distributed_db"  FROM stdin;
1	default                            
2	transactions                       
3	demographica                       
4	geographica                        
5	pharmaceutica                      
6	pathologica                        
7	radiologica                        
8	blobs                              
9	medicalhx                          
10	progressnotes                      
11	educativa                          
12	reference                          
13	modules                            
\.
--
-- Data for TOC Entry ID 274 (OID 35979)
--
-- Name: config Type: TABLE DATA Owner: syan
--


COPY "config"  FROM stdin;
\.
--
-- Data for TOC Entry ID 275 (OID 36033)
--
-- Name: class Type: TABLE DATA Owner: syan
--


COPY "class"  FROM stdin;
1	cardiovascular	\N	\N
2	beta blocker	\N	1
3	ACE inhibitor	\N	1
\.
--
-- Data for TOC Entry ID 276 (OID 36084)
--
-- Name: substance Type: TABLE DATA Owner: syan
--


COPY "substance"  FROM stdin;
1	atenolol	\N	2
2	enalopril	\N	3
\.
--
-- Data for TOC Entry ID 277 (OID 36135)
--
-- Name: pregnancy_cat Type: TABLE DATA Owner: syan
--


COPY "pregnancy_cat"  FROM stdin;
\.
--
-- Data for TOC Entry ID 278 (OID 36186)
--
-- Name: breastfeeding_cat Type: TABLE DATA Owner: syan
--


COPY "breastfeeding_cat"  FROM stdin;
\.
--
-- Data for TOC Entry ID 279 (OID 36218)
--
-- Name: obstetric_codes Type: TABLE DATA Owner: syan
--


COPY "obstetric_codes"  FROM stdin;
\.
--
-- Data for TOC Entry ID 280 (OID 36249)
--
-- Name: amount_unit Type: TABLE DATA Owner: syan
--


COPY "amount_unit"  FROM stdin;
2	mL
1	each
3	g
4	m
5	cm
6	dose
8	mg
\.
--
-- Data for TOC Entry ID 281 (OID 36284)
--
-- Name: drug_unit Type: TABLE DATA Owner: syan
--


COPY "drug_unit"  FROM stdin;
1	t	mg
2	t	mL
3	t	g
4	t	cm
5	f	unit
6	t	mcg
7	t	mmol
\.
--
-- Data for TOC Entry ID 282 (OID 36322)
--
-- Name: drug_route Type: TABLE DATA Owner: syan
--


COPY "drug_route"  FROM stdin;
1	intravenous	\N
2	intramuscular	\N
3	subcutaneous	\N
4	oral	\N
5	suppository	\N
6	pessary	\N
7	opthalmological	\N
8	otological	\N
9	dermatological	\N
10	otological/opthalmological	\N
11	inhalant	\N
12	rhinological	\N
13	injection (iv/im/sc)	\N
\.
--
-- Data for TOC Entry ID 283 (OID 36357)
--
-- Name: drug_presentation Type: TABLE DATA Owner: syan
--


COPY "drug_presentation"  FROM stdin;
1	tablet	4	1
4	capsule	4	1
5	injection (unknown IV/IM/SC)	13	2
6	powder	4	3
2	inhalant powder	11	3
7	wafer	4	1
8	suspension	4	2
9	lozenge	4	1
10	skin cream	9	3
19	vaginal cream	6	3
11	ointment	9	2
12	paste	9	5
13	solution	4	2
14	bandage	9	5
16	nasal spray	12	6
17	bath oil	9	2
18	dressing	9	4
20	eye drops	7	2
21	ear drops	8	2
22	suppository	5	1
23	anal cream	5	3
24	aerosol	11	2
25	nebule	11	2
26	IM injection	2	2
27	IV solution	1	2
28	SC injection	3	2
29	buccal spray	4	6
30	eye ointment	7	3
31	vaginal pessary	6	1
32	ear ointment	8	3
\.
--
-- Data for TOC Entry ID 284 (OID 36393)
--
-- Name: drug_package Type: TABLE DATA Owner: syan
--


COPY "drug_package"  FROM stdin;
1	1	1	30	5	atenolol
\.
--
-- Data for TOC Entry ID 285 (OID 36412)
--
-- Name: link_subst_package Type: TABLE DATA Owner: syan
--


COPY "link_subst_package"  FROM stdin;
1	1	1	50
\.
--
-- Data for TOC Entry ID 286 (OID 36444)
--
-- Name: drug_manufacturer Type: TABLE DATA Owner: syan
--


COPY "drug_manufacturer"  FROM stdin;
\.
--
-- Data for TOC Entry ID 287 (OID 36479)
--
-- Name: brand Type: TABLE DATA Owner: syan
--


COPY "brand"  FROM stdin;
\.
--
-- Data for TOC Entry ID 288 (OID 36495)
--
-- Name: link_brand_drug Type: TABLE DATA Owner: syan
--


COPY "link_brand_drug"  FROM stdin;
\.
--
-- Data for TOC Entry ID 289 (OID 36526)
--
-- Name: drug_flags Type: TABLE DATA Owner: syan
--


COPY "drug_flags"  FROM stdin;
\.
--
-- Data for TOC Entry ID 290 (OID 36558)
--
-- Name: link_flag_package Type: TABLE DATA Owner: syan
--


COPY "link_flag_package"  FROM stdin;
\.
--
-- Data for TOC Entry ID 291 (OID 36588)
--
-- Name: payor Type: TABLE DATA Owner: syan
--


COPY "payor"  FROM stdin;
\.
--
-- Data for TOC Entry ID 292 (OID 36602)
--
-- Name: restriction Type: TABLE DATA Owner: syan
--


COPY "restriction"  FROM stdin;
\.
--
-- Data for TOC Entry ID 293 (OID 36649)
--
-- Name: severity_code Type: TABLE DATA Owner: syan
--


COPY "severity_code"  FROM stdin;
\.
--
-- Data for TOC Entry ID 294 (OID 36700)
--
-- Name: interaction Type: TABLE DATA Owner: syan
--


COPY "interaction"  FROM stdin;
\.
--
-- Data for TOC Entry ID 295 (OID 36731)
--
-- Name: link_drug_interaction Type: TABLE DATA Owner: syan
--


COPY "link_drug_interaction"  FROM stdin;
\.
--
-- Data for TOC Entry ID 296 (OID 36778)
--
-- Name: disease Type: TABLE DATA Owner: syan
--


COPY "disease"  FROM stdin;
\.
--
-- Data for TOC Entry ID 297 (OID 36826)
--
-- Name: indication Type: TABLE DATA Owner: syan
--


COPY "indication"  FROM stdin;
\.
--
-- Data for TOC Entry ID 298 (OID 36865)
--
-- Name: link_disease_interaction Type: TABLE DATA Owner: syan
--


COPY "link_disease_interaction"  FROM stdin;
\.
--
-- Data for TOC Entry ID 299 (OID 36912)
--
-- Name: side_effect Type: TABLE DATA Owner: syan
--


COPY "side_effect"  FROM stdin;
\.
--
-- Data for TOC Entry ID 300 (OID 36963)
--
-- Name: audit_gis Type: TABLE DATA Owner: syan
--


COPY "audit_gis"  FROM stdin;
\.
--
-- Data for TOC Entry ID 301 (OID 36978)
--
-- Name: country Type: TABLE DATA Owner: syan
--


COPY "country"  FROM stdin;
\.
--
-- Data for TOC Entry ID 302 (OID 37015)
--
-- Name: state Type: TABLE DATA Owner: syan
--


COPY "state"  FROM stdin;
\.
--
-- Data for TOC Entry ID 303 (OID 37059)
--
-- Name: urb Type: TABLE DATA Owner: syan
--


COPY "urb"  FROM stdin;
\.
--
-- Data for TOC Entry ID 304 (OID 37103)
--
-- Name: street Type: TABLE DATA Owner: syan
--


COPY "street"  FROM stdin;
\.
--
-- Data for TOC Entry ID 305 (OID 37145)
--
-- Name: address_type Type: TABLE DATA Owner: syan
--


COPY "address_type"  FROM stdin;
1	1	home      
2	2	work      
3	3	parents   
4	4	holidays  
5	5	temporary 
\.
--
-- Data for TOC Entry ID 306 (OID 37164)
--
-- Name: address_external_ref Type: TABLE DATA Owner: syan
--


COPY "address_external_ref"  FROM stdin;
\.
--
-- Data for TOC Entry ID 307 (OID 37179)
--
-- Name: address_info Type: TABLE DATA Owner: syan
--


COPY "address_info"  FROM stdin;
\.
--
-- Data for TOC Entry ID 308 (OID 37233)
--
-- Name: link_amount Type: TABLE DATA Owner: syan
--


COPY "link_amount"  FROM stdin;
\.
--
-- Data for TOC Entry ID 309 (OID 37247)
--
-- Name: pbsimport Type: TABLE DATA Owner: syan
--


COPY "pbsimport"  FROM stdin;
\.
--
-- Data for TOC Entry ID 310 (OID 37315)
--
-- Name: audit_identity Type: TABLE DATA Owner: syan
--


COPY "audit_identity"  FROM stdin;
\.
--
-- Data for TOC Entry ID 311 (OID 37349)
--
-- Name: names Type: TABLE DATA Owner: syan
--


COPY "names"  FROM stdin;
12	2	2	t	T	Si	\N	\N	\N
15	4	4	t	s	a	\N	\N	\N
17	5	5	t	long	harry	\N	\N	\N
19	6	6	t	dirty	harry	\N	\N	\N
25	8	8	t	a	h	\N	\N	\N
34	12	11	t	Follows	Fred	\N	\N	\N
37	13	12	t	Flintstone	Fred	\N	\N	\N
28	10	9	t	Wong	Gary	\N	\N	\N
40	14	13	t	Blowg	Joe	\N	\N	\N
22	7	7	t	Head	Sally	\N	\N	\N
66	15	14	t	Head	Belly	\N	\N	\N
31	11	10	t	Head	Frank	\N	\N	\N
70	16	15	t	Head	Butt	\N	\N	\N
\.
--
-- Data for TOC Entry ID 312 (OID 37400)
--
-- Name: relation_types Type: TABLE DATA Owner: syan
--


COPY "relation_types"  FROM stdin;
1	1	t	f	parent
2	2	t	f	sibling
3	3	t	f	halfsibling
4	4	f	f	stepparent
5	5	f	f	married
6	6	f	f	defacto
7	7	f	f	divorced
8	8	f	f	separated
9	9	f	f	legal_guardian
\.
--
-- Data for TOC Entry ID 313 (OID 37445)
--
-- Name: relation Type: TABLE DATA Owner: syan
--


COPY "relation"  FROM stdin;
\.
--
-- Data for TOC Entry ID 314 (OID 37492)
--
-- Name: identities_addresses Type: TABLE DATA Owner: syan
--


COPY "identities_addresses"  FROM stdin;
20	1	6	1	prototype1                                                                      
23	2	7	2	prototype1                                                                      
26	3	8	3	NewPersonStoreCommand.py.v0.1                                                   
29	4	9	4	NewPersonStoreCommand.py.v0.1                                                   
32	5	10	5	NewPersonStoreCommand.py.v0.1                                                   
35	6	11	6	NewPersonStoreCommand.py.v0.1                                                   
38	7	12	7	NewPersonStoreCommand.py.v0.1                                                   
41	8	13	8	NewPersonStoreCommand.py.v0.1                                                   
67	9	14	9	NewPersonStoreCommand.py.v0.1                                                   
71	10	15	10	NewPersonStoreCommand.py.v0.1                                                   
\.
--
-- Data for TOC Entry ID 315 (OID 37536)
--
-- Name: address Type: TABLE DATA Owner: syan
--


COPY "address"  FROM stdin;
208	1	1	\N	17 rylie st                                       	Balwyn
210	3	1	\N	a                                                 	b
213	6	1	\N	23 Foundation Ave                                 	PhilVille
214	7	1	\N	34 Vilma Rd                                       	Vermont
211	4	1	\N	24 Victor rd                                      	Broadford
215	8	1	\N	32 Victor st                                      	Grealle
209	2	1	\N	23 Truman Rd                                      	New Park
216	9	1	\N	22 Han Hui Rd                                     	City West
212	5	1	\N	22 Leningrad Ave                                  	Russia West
217	10	1	\N	1/3 Lonie Rd                                      	
\.
--
-- Data for TOC Entry ID 316 (OID 37612)
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
62	21	111	3333	\N	7
68	24	111-220	222-333	\N	14
64	23	444-4000	555-5000	\N	10
72	25	03 3203333		\N	15
\.
--
-- Data for TOC Entry ID 317 (OID 37632)
--
-- Name: identity Type: TABLE DATA Owner: syan
--


COPY "identity"  FROM stdin;
11	2	\N	m 	\N	1944-08-30	\N	\N
14	4	\N	m 	\N	2000-02-01	\N	\N
16	5	\N	m 	\N	1966-07-30	\N	\N
18	6	\N	m 	\N	1933-10-10	\N	\N
24	8	                        	m 	\N	2002-01-01	\N	\N
33	11	1213423423              	m 	\N	1950-01-01	\N	\N
36	12	230-2000-1              	m 	\N	1999-12-20	\N	\N
27	9	4444555551              	f 	\N	1989-12-12	\N	\N
39	13	444-55055               	m 	\N	2000-06-17	\N	\N
21	7	1111-2222               	f 	\N	1945-01-11	\N	\N
65	14	99999991                	m 	\N	2002-02-03	\N	\N
30	10	111-2222                	m 	\N	1933-11-11	\N	\N
69	15	                        	m 	\N	1980-01-01	\N	\N
\.
--
-- Data for TOC Entry ID 318 (OID 38118)
--
-- Name: ix_type_link Type: TABLE DATA Owner: syan
--


COPY "ix_type_link"  FROM stdin;
\.
--
-- Data for TOC Entry ID 319 (OID 38129)
--
-- Name: clin_record Type: TABLE DATA Owner: syan
--


COPY "clin_record"  FROM stdin;
\.
--
-- Data for TOC Entry ID 320 (OID 38163)
--
-- Name: basic_context Type: TABLE DATA Owner: syan
--


COPY "basic_context"  FROM stdin;
\.
--
-- Data for TOC Entry ID 321 (OID 38199)
--
-- Name: durable Type: TABLE DATA Owner: syan
--


COPY "durable"  FROM stdin;
\.
--
-- Data for TOC Entry ID 322 (OID 38239)
--
-- Name: phx_durable Type: TABLE DATA Owner: syan
--


COPY "phx_durable"  FROM stdin;
12	2002-03-28	\N	\N	cholecystectomy	open	7	1990-01-04	panch	\N	\N	1990-02-14	\N	syan
19	2002-03-29	\N	\N	appendicitis	clean	7	1999-10-01		\N	\N	1999-10-12	\N	syan
24	2002-03-29	\N	\N	appendicitis	 	7	1999-10-01		\N	\N	1999-10-12	\N	syan
25	2002-03-29	\N	\N	appendicitis	 	7	1999-10-01		\N	\N	1999-10-12	\N	syan
30	2002-03-29	\N	\N	appendicitis	dirty	7	1999-10-01		\N	\N	1999-10-12	\N	syan
35	2002-03-30	\N	\N	appendicitis	complicated	7	1999-10-01		\N	\N	1999-10-12	\N	syan
\.
--
-- Data for TOC Entry ID 323 (OID 38281)
--
-- Name: phx_event Type: TABLE DATA Owner: syan
--


COPY "phx_event"  FROM stdin;
1	2002-03-28	\N	\N	asthma	else	\N	2002-01-02	something	\N	\N
2	2002-03-28	\N	\N	asthma		7	2002-01-01		\N	\N
3	2002-03-28	\N	\N	diabetes		7	2002-02-02	st vs	\N	\N
4	2002-03-28	\N	\N	AMI	45%	7	1997-01-01	Maroondah	\N	\N
5	2002-03-28	\N	\N	appendicitis		7	1999-10-01		\N	\N
6	2002-03-28	\N	\N	# humerus		7	1998-01-01	Hamilton	\N	\N
8	2002-03-28	\N	\N	pneumonia	bilateral	7	1990-01-01	Frankston	\N	\N
16	2002-03-29	\N	\N	asthma	mild	7	2002-01-01		\N	syan
18	2002-03-29	\N	\N	# scaphoid R	ouch	7	2000-01-01	Frankston	\N	syan
23	2002-03-29	\N	\N	AMI	25%	7	1997-01-01	Maroondah	\N	syan
32	2002-03-29	\N	\N	femur #		7	1966-01-01	Sydney	\N	syan
33	2002-03-29	\N	\N	# scaphoid R	plaster	7	2000-01-01	Frankston	\N	syan
46	2002-04-02	\N	\N	femur #	This	7	1966-01-01	Sydney	\N	syan
48	2002-04-02	\N	\N	femur #	uti, atelectasis\
rehab p[roblem\
	7	1966-01-01	Sydney	\N	syan
50	2002-04-02	\N	\N	asthma	mild\
FEV1 change 32%	10	2002-01-01	lmo	\N	syan
51	2002-04-02	\N	\N	asthma	mild\
FEV1 change 32%	10	2002-01-01	lmo	\N	syan
53	2002-04-02	\N	\N	gout	last urate 2/2/2003	10	2002-01-01		\N	syan
54	2002-04-02	\N	\N	gout	last urate 2/2/2003\
now another line	10	2002-01-01		\N	syan
56	2002-04-02	\N	\N	asthma	mild\
FEV1 change 32%	10	2002-01-01	lmo	\N	syan
58	2002-04-02	\N	\N	asthma	mild FEV1 \
change 32%	10	2002-01-01	lmo	\N	syan
60	2002-04-02	\N	\N	asthma	mild FEV1 change 32%	10	2002-01-01	lmo	\N	syan
62	2002-04-02	\N	\N	asthma	mild FEV1 change 32% \
dont new line too early?	10	2002-01-01	lmo	\N	syan
64	2002-04-07	\N	\N	pneumonia	bilateral	7	1990-01-01	Frankston	\N	syan
66	2002-04-07	\N	\N	pneumonia	bilateral,\
ICU\
PE	7	1990-01-01	Frankston	\N	syan
68	2002-04-13	\N	\N	femur #	uti, atelectasis\
rehab 2/12\
	7	1966-01-01	Sydney	\N	syan
76	2002-04-13	\N	\N	pneumonia	bilateral, ICU \
ventilated/sedated 10 days\
ARDS\
cx dysarthria and\
hemiplegia \
	7	1990-01-01	Frankston	\N	syan
78	2002-04-13	\N	\N	pneumonia	bilateral, ICU \
ventilated/sedated 10 days\
ARDS\
	7	1990-01-01	Frankston	\N	syan
80	2002-04-13	\N	\N	asthma	mild	15	1995-03-01	lmo	\N	syan
81	2002-04-13	\N	\N	asthma	mild , infrequent no hosp admiss	15	1995-03-01	lmo	\N	syan
\.
--
-- Data for TOC Entry ID 324 (OID 38319)
--
-- Name: procedure Type: TABLE DATA Owner: syan
--


COPY "procedure"  FROM stdin;
\.
--
-- Data for TOC Entry ID 325 (OID 38358)
--
-- Name: sequelae Type: TABLE DATA Owner: syan
--


COPY "sequelae"  FROM stdin;
\.
--
-- Data for TOC Entry ID 326 (OID 38405)
--
-- Name: meds Type: TABLE DATA Owner: syan
--


COPY "meds"  FROM stdin;
\.
--
-- Data for TOC Entry ID 327 (OID 38445)
--
-- Name: med_dose Type: TABLE DATA Owner: syan
--


COPY "med_dose"  FROM stdin;
\.
--
-- Data for TOC Entry ID 328 (OID 38490)
--
-- Name: med_timing Type: TABLE DATA Owner: syan
--


COPY "med_timing"  FROM stdin;
\.
--
-- Data for TOC Entry ID 329 (OID 38524)
--
-- Name: med_qty Type: TABLE DATA Owner: syan
--


COPY "med_qty"  FROM stdin;
\.
--
-- Data for TOC Entry ID 330 (OID 38568)
--
-- Name: allergy Type: TABLE DATA Owner: syan
--


COPY "allergy"  FROM stdin;
37	2002-03-31	\N	\N		\N	7	2001-01-01	\N	\N	penicillin	\N	syan
38	2002-03-31	\N	\N	rash	\N	7	2001-01-01	\N	\N	penic	\N	syan
39	2002-03-31	\N	\N	allergy	\N	7	2001-01-01	\N	\N	penic	\N	syan
40	2002-03-31	\N	\N	a	\N	7	2001-01-01	\N	\N	penic	\N	syan
44	2002-03-31	\N	\N	rash , erythematous	\N	7	2001-01-01	\N	\N	penicillin	\N	syan
71	2002-04-13	\N	\N	rash	\N	7	2002-03-01	\N	\N	penicillin	\N	syan
73	2002-04-13	\N	\N	penicillin allergy	rash	7	2002-02-01	\N	\N	penicillin	\N	syan
74	2002-04-13	\N	\N	sulfur allergy	rash	7	2002-02-01	\N	\N	sulfur	\N	syan
83	2002-04-13	\N	\N	bactrim allergy	Stevens Johnsons	15	2000-11-01	\N	\N	bactrim	\N	syan
\.
--
-- Data for TOC Entry ID 331 (OID 38609)
--
-- Name: sochx Type: TABLE DATA Owner: syan
--


COPY "sochx"  FROM stdin;
\.
--
-- Data for TOC Entry ID 332 (OID 38647)
--
-- Name: fhx Type: TABLE DATA Owner: syan
--


COPY "fhx"  FROM stdin;
\.
--
-- Data for TOC Entry ID 333 (OID 38689)
--
-- Name: habit_type Type: TABLE DATA Owner: syan
--


COPY "habit_type"  FROM stdin;
\.
--
-- Data for TOC Entry ID 334 (OID 38728)
--
-- Name: habit Type: TABLE DATA Owner: syan
--


COPY "habit"  FROM stdin;
\.
--
-- Data for TOC Entry ID 335 (OID 38777)
--
-- Name: ix_type Type: TABLE DATA Owner: syan
--


COPY "ix_type"  FROM stdin;
\.
--
-- Data for TOC Entry ID 336 (OID 38811)
--
-- Name: ixphx Type: TABLE DATA Owner: syan
--


COPY "ixphx"  FROM stdin;
\.
--
-- Data for TOC Entry ID 337 (OID 38851)
--
-- Name: problem Type: TABLE DATA Owner: syan
--


COPY "problem"  FROM stdin;
\.
--
-- Data for TOC Entry ID 338 (OID 38893)
--
-- Name: problem_phx_link Type: TABLE DATA Owner: syan
--


COPY "problem_phx_link"  FROM stdin;
\.
--
-- Data for TOC Entry ID 339 (OID 39285)
--
-- Name: revocation Type: TABLE DATA Owner: syan
--


COPY "revocation"  FROM stdin;
17	2002-03-29	\N	\N	\N	\N	syan	2	16
20	2002-03-29	\N	\N	\N	\N	syan	5	20
21	2002-03-29	\N	\N	\N	\N	syan	6	21
22	2002-03-29	\N	\N	\N	\N	syan	16	22
26	2002-03-29	\N	\N	\N	\N	syan	4	26
27	2002-03-29	\N	\N	\N	\N	syan	24	27
28	2002-03-29	\N	\N	\N	\N	syan	25	28
29	2002-03-29	\N	\N	\N	\N	syan	3	29
31	2002-03-29	\N	\N	\N	\N	syan	19	31
34	2002-03-29	\N	\N	\N	\N	syan	18	34
36	2002-03-30	\N	\N	\N	\N	syan	30	36
41	2002-03-31	\N	\N	\N	\N	syan	40	41
42	2002-03-31	\N	\N	\N	\N	syan	38	42
43	2002-03-31	\N	\N	\N	\N	syan	39	43
45	2002-03-31	\N	\N	\N	\N	syan	37	45
47	2002-04-02	\N	\N	\N	\N	syan	32	47
49	2002-04-02	\N	\N	\N	\N	syan	46	49
52	2002-04-02	\N	\N	\N	\N	syan	50	52
55	2002-04-02	\N	\N	\N	\N	syan	53	55
57	2002-04-02	\N	\N	\N	\N	syan	51	57
59	2002-04-02	\N	\N	\N	\N	syan	56	59
61	2002-04-02	\N	\N	\N	\N	syan	58	61
63	2002-04-02	\N	\N	\N	\N	syan	60	63
65	2002-04-07	\N	\N	\N	\N	syan	8	65
67	2002-04-07	\N	\N	\N	\N	syan	64	67
69	2002-04-13	\N	\N	\N	\N	syan	48	69
70	2002-04-13	\N	\N	\N	\N	syan	44	70
72	2002-04-13	\N	\N	\N	\N	syan	71	72
75	2002-04-13	\N	\N	\N	\N	syan	73	75
77	2002-04-13	\N	\N	\N	\N	syan	66	77
79	2002-04-13	\N	\N	\N	\N	syan	76	79
82	2002-04-13	\N	\N	\N	\N	syan	80	82
\.
--
-- TOC Entry ID 247 (OID 35698)
--
-- Name: "clinician_id_key" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "clinician_id_key" on "clinician" using btree ( "id" "int4_ops" );

--
-- TOC Entry ID 248 (OID 35750)
--
-- Name: "session_id_key" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "session_id_key" on "session" using btree ( "id" "int4_ops" );

--
-- TOC Entry ID 249 (OID 36588)
--
-- Name: "payor_id_key" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "payor_id_key" on "payor" using btree ( "id" "int4_ops" );

--
-- TOC Entry ID 250 (OID 36778)
--
-- Name: "disease_id_key" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "disease_id_key" on "disease" using btree ( "id" "int4_ops" );

--
-- TOC Entry ID 251 (OID 36912)
--
-- Name: "side_effect_id_key" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "side_effect_id_key" on "side_effect" using btree ( "id" "int4_ops" );

--
-- TOC Entry ID 252 (OID 37015)
--
-- Name: "nodupes" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "nodupes" on "state" using btree ( "code" "bpchar_ops", "country" "bpchar_ops" );

--
-- TOC Entry ID 253 (OID 37233)
--
-- Name: "link_amount_id_key" Type: INDEX Owner: syan
--

CREATE UNIQUE INDEX "link_amount_id_key" on "link_amount" using btree ( "id" "int4_ops" );

--
-- TOC Entry ID 344 (OID 37844)
--
-- Name: "RI_ConstraintTrigger_37843" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "session"  FROM "clinician" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'session', 'clinician', 'UNSPECIFIED', 'clinician', 'id');

--
-- TOC Entry ID 340 (OID 37846)
--
-- Name: "RI_ConstraintTrigger_37845" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "clinician"  FROM "session" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'session', 'clinician', 'UNSPECIFIED', 'clinician', 'id');

--
-- TOC Entry ID 341 (OID 37848)
--
-- Name: "RI_ConstraintTrigger_37847" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "clinician"  FROM "session" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'session', 'clinician', 'UNSPECIFIED', 'clinician', 'id');

--
-- TOC Entry ID 350 (OID 37850)
--
-- Name: "RI_ConstraintTrigger_37849" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "holiday"  FROM "clinician" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'holiday', 'clinician', 'UNSPECIFIED', 'clinician', 'id');

--
-- TOC Entry ID 342 (OID 37852)
--
-- Name: "RI_ConstraintTrigger_37851" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "clinician"  FROM "holiday" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'holiday', 'clinician', 'UNSPECIFIED', 'clinician', 'id');

--
-- TOC Entry ID 343 (OID 37854)
--
-- Name: "RI_ConstraintTrigger_37853" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "clinician"  FROM "holiday" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'holiday', 'clinician', 'UNSPECIFIED', 'clinician', 'id');

--
-- TOC Entry ID 351 (OID 37856)
--
-- Name: "RI_ConstraintTrigger_37855" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "appointment"  FROM "session" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'appointment', 'session', 'UNSPECIFIED', 'session', 'id');

--
-- TOC Entry ID 345 (OID 37858)
--
-- Name: "RI_ConstraintTrigger_37857" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "session"  FROM "appointment" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'appointment', 'session', 'UNSPECIFIED', 'session', 'id');

--
-- TOC Entry ID 346 (OID 37860)
--
-- Name: "RI_ConstraintTrigger_37859" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "session"  FROM "appointment" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'appointment', 'session', 'UNSPECIFIED', 'session', 'id');

--
-- TOC Entry ID 353 (OID 37862)
--
-- Name: "RI_ConstraintTrigger_37861" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "list"  FROM "session" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'list', 'session', 'UNSPECIFIED', 'session', 'id');

--
-- TOC Entry ID 347 (OID 37864)
--
-- Name: "RI_ConstraintTrigger_37863" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "session"  FROM "list" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'list', 'session', 'UNSPECIFIED', 'session', 'id');

--
-- TOC Entry ID 348 (OID 37866)
--
-- Name: "RI_ConstraintTrigger_37865" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "session"  FROM "list" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'list', 'session', 'UNSPECIFIED', 'session', 'id');

--
-- TOC Entry ID 349 (OID 37867)
--
-- Name: list_create Type: TRIGGER Owner: syan
--

CREATE TRIGGER "list_create" AFTER INSERT OR DELETE OR UPDATE ON "session"  FOR EACH ROW EXECUTE PROCEDURE "list_create" ();

--
-- TOC Entry ID 352 (OID 37868)
--
-- Name: new_appointment Type: TRIGGER Owner: syan
--

CREATE TRIGGER "new_appointment" BEFORE INSERT OR DELETE OR UPDATE ON "appointment"  FOR EACH ROW EXECUTE PROCEDURE "new_appointment" ();

--
-- TOC Entry ID 358 (OID 37870)
--
-- Name: "RI_ConstraintTrigger_37869" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "config"  FROM "distributed_db" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'config', 'distributed_db', 'UNSPECIFIED', 'ddb', 'id');

--
-- TOC Entry ID 356 (OID 37872)
--
-- Name: "RI_ConstraintTrigger_37871" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "distributed_db"  FROM "config" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'config', 'distributed_db', 'UNSPECIFIED', 'ddb', 'id');

--
-- TOC Entry ID 357 (OID 37874)
--
-- Name: "RI_ConstraintTrigger_37873" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "distributed_db"  FROM "config" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'config', 'distributed_db', 'UNSPECIFIED', 'ddb', 'id');

--
-- TOC Entry ID 359 (OID 37876)
--
-- Name: "RI_ConstraintTrigger_37875" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "config"  FROM "db" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'config', 'db', 'UNSPECIFIED', 'db', 'id');

--
-- TOC Entry ID 354 (OID 37878)
--
-- Name: "RI_ConstraintTrigger_37877" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "db"  FROM "config" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'config', 'db', 'UNSPECIFIED', 'db', 'id');

--
-- TOC Entry ID 355 (OID 37880)
--
-- Name: "RI_ConstraintTrigger_37879" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "db"  FROM "config" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'config', 'db', 'UNSPECIFIED', 'db', 'id');

--
-- TOC Entry ID 360 (OID 37882)
--
-- Name: "RI_ConstraintTrigger_37881" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "class"  FROM "class" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'class', 'class', 'UNSPECIFIED', 'superclass', 'id');

--
-- TOC Entry ID 361 (OID 37884)
--
-- Name: "RI_ConstraintTrigger_37883" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "class"  FROM "class" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'class', 'class', 'UNSPECIFIED', 'superclass', 'id');

--
-- TOC Entry ID 362 (OID 37886)
--
-- Name: "RI_ConstraintTrigger_37885" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "class"  FROM "class" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'class', 'class', 'UNSPECIFIED', 'superclass', 'id');

--
-- TOC Entry ID 365 (OID 37888)
--
-- Name: "RI_ConstraintTrigger_37887" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "substance"  FROM "class" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'substance', 'class', 'UNSPECIFIED', 'class', 'id');

--
-- TOC Entry ID 363 (OID 37890)
--
-- Name: "RI_ConstraintTrigger_37889" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "class"  FROM "substance" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'substance', 'class', 'UNSPECIFIED', 'class', 'id');

--
-- TOC Entry ID 364 (OID 37892)
--
-- Name: "RI_ConstraintTrigger_37891" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "class"  FROM "substance" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'substance', 'class', 'UNSPECIFIED', 'class', 'id');

--
-- TOC Entry ID 376 (OID 37894)
--
-- Name: "RI_ConstraintTrigger_37893" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "obstetric_codes"  FROM "substance" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'obstetric_codes', 'substance', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 366 (OID 37896)
--
-- Name: "RI_ConstraintTrigger_37895" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "substance"  FROM "obstetric_codes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'obstetric_codes', 'substance', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 367 (OID 37898)
--
-- Name: "RI_ConstraintTrigger_37897" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "substance"  FROM "obstetric_codes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'obstetric_codes', 'substance', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 377 (OID 37900)
--
-- Name: "RI_ConstraintTrigger_37899" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "obstetric_codes"  FROM "pregnancy_cat" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'obstetric_codes', 'pregnancy_cat', 'UNSPECIFIED', 'preg_code', 'id');

--
-- TOC Entry ID 372 (OID 37902)
--
-- Name: "RI_ConstraintTrigger_37901" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "pregnancy_cat"  FROM "obstetric_codes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'obstetric_codes', 'pregnancy_cat', 'UNSPECIFIED', 'preg_code', 'id');

--
-- TOC Entry ID 373 (OID 37904)
--
-- Name: "RI_ConstraintTrigger_37903" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "pregnancy_cat"  FROM "obstetric_codes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'obstetric_codes', 'pregnancy_cat', 'UNSPECIFIED', 'preg_code', 'id');

--
-- TOC Entry ID 378 (OID 37906)
--
-- Name: "RI_ConstraintTrigger_37905" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "obstetric_codes"  FROM "breastfeeding_cat" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'obstetric_codes', 'breastfeeding_cat', 'UNSPECIFIED', 'brst_code', 'id');

--
-- TOC Entry ID 374 (OID 37908)
--
-- Name: "RI_ConstraintTrigger_37907" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "breastfeeding_cat"  FROM "obstetric_codes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'obstetric_codes', 'breastfeeding_cat', 'UNSPECIFIED', 'brst_code', 'id');

--
-- TOC Entry ID 375 (OID 37910)
--
-- Name: "RI_ConstraintTrigger_37909" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "breastfeeding_cat"  FROM "obstetric_codes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'obstetric_codes', 'breastfeeding_cat', 'UNSPECIFIED', 'brst_code', 'id');

--
-- TOC Entry ID 385 (OID 37912)
--
-- Name: "RI_ConstraintTrigger_37911" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "drug_presentation"  FROM "drug_route" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'drug_presentation', 'drug_route', 'UNSPECIFIED', 'route', 'id');

--
-- TOC Entry ID 383 (OID 37914)
--
-- Name: "RI_ConstraintTrigger_37913" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_route"  FROM "drug_presentation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'drug_presentation', 'drug_route', 'UNSPECIFIED', 'route', 'id');

--
-- TOC Entry ID 384 (OID 37916)
--
-- Name: "RI_ConstraintTrigger_37915" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_route"  FROM "drug_presentation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'drug_presentation', 'drug_route', 'UNSPECIFIED', 'route', 'id');

--
-- TOC Entry ID 386 (OID 37918)
--
-- Name: "RI_ConstraintTrigger_37917" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "drug_presentation"  FROM "amount_unit" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'drug_presentation', 'amount_unit', 'UNSPECIFIED', 'amount_unit', 'id');

--
-- TOC Entry ID 379 (OID 37920)
--
-- Name: "RI_ConstraintTrigger_37919" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "amount_unit"  FROM "drug_presentation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'drug_presentation', 'amount_unit', 'UNSPECIFIED', 'amount_unit', 'id');

--
-- TOC Entry ID 380 (OID 37922)
--
-- Name: "RI_ConstraintTrigger_37921" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "amount_unit"  FROM "drug_presentation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'drug_presentation', 'amount_unit', 'UNSPECIFIED', 'amount_unit', 'id');

--
-- TOC Entry ID 389 (OID 37924)
--
-- Name: "RI_ConstraintTrigger_37923" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "drug_package"  FROM "drug_presentation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'drug_package', 'drug_presentation', 'UNSPECIFIED', 'presentation', 'id');

--
-- TOC Entry ID 387 (OID 37926)
--
-- Name: "RI_ConstraintTrigger_37925" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_presentation"  FROM "drug_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'drug_package', 'drug_presentation', 'UNSPECIFIED', 'presentation', 'id');

--
-- TOC Entry ID 388 (OID 37928)
--
-- Name: "RI_ConstraintTrigger_37927" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_presentation"  FROM "drug_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'drug_package', 'drug_presentation', 'UNSPECIFIED', 'presentation', 'id');

--
-- TOC Entry ID 398 (OID 37930)
--
-- Name: "RI_ConstraintTrigger_37929" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_subst_package"  FROM "drug_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_subst_package', 'drug_package', 'UNSPECIFIED', 'package', 'id');

--
-- TOC Entry ID 390 (OID 37932)
--
-- Name: "RI_ConstraintTrigger_37931" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_package"  FROM "link_subst_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_subst_package', 'drug_package', 'UNSPECIFIED', 'package', 'id');

--
-- TOC Entry ID 391 (OID 37934)
--
-- Name: "RI_ConstraintTrigger_37933" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_package"  FROM "link_subst_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_subst_package', 'drug_package', 'UNSPECIFIED', 'package', 'id');

--
-- TOC Entry ID 399 (OID 37936)
--
-- Name: "RI_ConstraintTrigger_37935" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_subst_package"  FROM "substance" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_subst_package', 'substance', 'UNSPECIFIED', 'substance', 'id');

--
-- TOC Entry ID 368 (OID 37938)
--
-- Name: "RI_ConstraintTrigger_37937" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "substance"  FROM "link_subst_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_subst_package', 'substance', 'UNSPECIFIED', 'substance', 'id');

--
-- TOC Entry ID 369 (OID 37940)
--
-- Name: "RI_ConstraintTrigger_37939" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "substance"  FROM "link_subst_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_subst_package', 'substance', 'UNSPECIFIED', 'substance', 'id');

--
-- TOC Entry ID 400 (OID 37942)
--
-- Name: "RI_ConstraintTrigger_37941" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_subst_package"  FROM "drug_unit" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_subst_package', 'drug_unit', 'UNSPECIFIED', 'unit', 'id');

--
-- TOC Entry ID 381 (OID 37944)
--
-- Name: "RI_ConstraintTrigger_37943" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_unit"  FROM "link_subst_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_subst_package', 'drug_unit', 'UNSPECIFIED', 'unit', 'id');

--
-- TOC Entry ID 382 (OID 37946)
--
-- Name: "RI_ConstraintTrigger_37945" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_unit"  FROM "link_subst_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_subst_package', 'drug_unit', 'UNSPECIFIED', 'unit', 'id');

--
-- TOC Entry ID 403 (OID 37948)
--
-- Name: "RI_ConstraintTrigger_37947" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "brand"  FROM "drug_manufacturer" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'brand', 'drug_manufacturer', 'UNSPECIFIED', 'drug_manufacturer_id', 'id');

--
-- TOC Entry ID 401 (OID 37950)
--
-- Name: "RI_ConstraintTrigger_37949" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_manufacturer"  FROM "brand" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'brand', 'drug_manufacturer', 'UNSPECIFIED', 'drug_manufacturer_id', 'id');

--
-- TOC Entry ID 402 (OID 37952)
--
-- Name: "RI_ConstraintTrigger_37951" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_manufacturer"  FROM "brand" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'brand', 'drug_manufacturer', 'UNSPECIFIED', 'drug_manufacturer_id', 'id');

--
-- TOC Entry ID 406 (OID 37954)
--
-- Name: "RI_ConstraintTrigger_37953" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_brand_drug"  FROM "brand" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_brand_drug', 'brand', 'UNSPECIFIED', 'brand_id', 'id');

--
-- TOC Entry ID 404 (OID 37956)
--
-- Name: "RI_ConstraintTrigger_37955" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "brand"  FROM "link_brand_drug" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_brand_drug', 'brand', 'UNSPECIFIED', 'brand_id', 'id');

--
-- TOC Entry ID 405 (OID 37958)
--
-- Name: "RI_ConstraintTrigger_37957" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "brand"  FROM "link_brand_drug" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_brand_drug', 'brand', 'UNSPECIFIED', 'brand_id', 'id');

--
-- TOC Entry ID 407 (OID 37960)
--
-- Name: "RI_ConstraintTrigger_37959" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_brand_drug"  FROM "drug_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_brand_drug', 'drug_package', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 392 (OID 37962)
--
-- Name: "RI_ConstraintTrigger_37961" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_package"  FROM "link_brand_drug" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_brand_drug', 'drug_package', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 393 (OID 37964)
--
-- Name: "RI_ConstraintTrigger_37963" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_package"  FROM "link_brand_drug" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_brand_drug', 'drug_package', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 410 (OID 37966)
--
-- Name: "RI_ConstraintTrigger_37965" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_flag_package"  FROM "drug_flags" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_flag_package', 'drug_flags', 'UNSPECIFIED', 'flag_id', 'id');

--
-- TOC Entry ID 408 (OID 37968)
--
-- Name: "RI_ConstraintTrigger_37967" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_flags"  FROM "link_flag_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_flag_package', 'drug_flags', 'UNSPECIFIED', 'flag_id', 'id');

--
-- TOC Entry ID 409 (OID 37970)
--
-- Name: "RI_ConstraintTrigger_37969" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_flags"  FROM "link_flag_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_flag_package', 'drug_flags', 'UNSPECIFIED', 'flag_id', 'id');

--
-- TOC Entry ID 411 (OID 37972)
--
-- Name: "RI_ConstraintTrigger_37971" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_flag_package"  FROM "drug_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_flag_package', 'drug_package', 'UNSPECIFIED', 'pack_id', 'id');

--
-- TOC Entry ID 394 (OID 37974)
--
-- Name: "RI_ConstraintTrigger_37973" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_package"  FROM "link_flag_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_flag_package', 'drug_package', 'UNSPECIFIED', 'pack_id', 'id');

--
-- TOC Entry ID 395 (OID 37976)
--
-- Name: "RI_ConstraintTrigger_37975" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_package"  FROM "link_flag_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_flag_package', 'drug_package', 'UNSPECIFIED', 'pack_id', 'id');

--
-- TOC Entry ID 414 (OID 37978)
--
-- Name: "RI_ConstraintTrigger_37977" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "restriction"  FROM "substance" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'restriction', 'substance', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 370 (OID 37980)
--
-- Name: "RI_ConstraintTrigger_37979" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "substance"  FROM "restriction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'restriction', 'substance', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 371 (OID 37982)
--
-- Name: "RI_ConstraintTrigger_37981" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "substance"  FROM "restriction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'restriction', 'substance', 'UNSPECIFIED', 'drug_id', 'id');

--
-- TOC Entry ID 415 (OID 37984)
--
-- Name: "RI_ConstraintTrigger_37983" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "restriction"  FROM "payor" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'restriction', 'payor', 'UNSPECIFIED', 'payor_id', 'id');

--
-- TOC Entry ID 412 (OID 37986)
--
-- Name: "RI_ConstraintTrigger_37985" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "payor"  FROM "restriction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'restriction', 'payor', 'UNSPECIFIED', 'payor_id', 'id');

--
-- TOC Entry ID 413 (OID 37988)
--
-- Name: "RI_ConstraintTrigger_37987" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "payor"  FROM "restriction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'restriction', 'payor', 'UNSPECIFIED', 'payor_id', 'id');

--
-- TOC Entry ID 420 (OID 37990)
--
-- Name: "RI_ConstraintTrigger_37989" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "interaction"  FROM "severity_code" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'interaction', 'severity_code', 'UNSPECIFIED', 'severity', 'id');

--
-- TOC Entry ID 416 (OID 37992)
--
-- Name: "RI_ConstraintTrigger_37991" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "severity_code"  FROM "interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'interaction', 'severity_code', 'UNSPECIFIED', 'severity', 'id');

--
-- TOC Entry ID 417 (OID 37994)
--
-- Name: "RI_ConstraintTrigger_37993" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "severity_code"  FROM "interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'interaction', 'severity_code', 'UNSPECIFIED', 'severity', 'id');

--
-- TOC Entry ID 425 (OID 37996)
--
-- Name: "RI_ConstraintTrigger_37995" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_drug_interaction"  FROM "interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_drug_interaction', 'interaction', 'UNSPECIFIED', 'interaction_id', 'id');

--
-- TOC Entry ID 421 (OID 37998)
--
-- Name: "RI_ConstraintTrigger_37997" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "interaction"  FROM "link_drug_interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_drug_interaction', 'interaction', 'UNSPECIFIED', 'interaction_id', 'id');

--
-- TOC Entry ID 422 (OID 38000)
--
-- Name: "RI_ConstraintTrigger_37999" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "interaction"  FROM "link_drug_interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_drug_interaction', 'interaction', 'UNSPECIFIED', 'interaction_id', 'id');

--
-- TOC Entry ID 430 (OID 38002)
--
-- Name: "RI_ConstraintTrigger_38001" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "indication"  FROM "drug_package" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'indication', 'drug_package', 'UNSPECIFIED', 'drug', 'id');

--
-- TOC Entry ID 396 (OID 38004)
--
-- Name: "RI_ConstraintTrigger_38003" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "drug_package"  FROM "indication" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'indication', 'drug_package', 'UNSPECIFIED', 'drug', 'id');

--
-- TOC Entry ID 397 (OID 38006)
--
-- Name: "RI_ConstraintTrigger_38005" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "drug_package"  FROM "indication" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'indication', 'drug_package', 'UNSPECIFIED', 'drug', 'id');

--
-- TOC Entry ID 431 (OID 38008)
--
-- Name: "RI_ConstraintTrigger_38007" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_disease_interaction"  FROM "disease" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_disease_interaction', 'disease', 'UNSPECIFIED', 'disease_id', 'id');

--
-- TOC Entry ID 426 (OID 38010)
--
-- Name: "RI_ConstraintTrigger_38009" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "disease"  FROM "link_disease_interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_disease_interaction', 'disease', 'UNSPECIFIED', 'disease_id', 'id');

--
-- TOC Entry ID 427 (OID 38012)
--
-- Name: "RI_ConstraintTrigger_38011" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "disease"  FROM "link_disease_interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_disease_interaction', 'disease', 'UNSPECIFIED', 'disease_id', 'id');

--
-- TOC Entry ID 432 (OID 38014)
--
-- Name: "RI_ConstraintTrigger_38013" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "link_disease_interaction"  FROM "interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'link_disease_interaction', 'interaction', 'UNSPECIFIED', 'interaction_id', 'id');

--
-- TOC Entry ID 423 (OID 38016)
--
-- Name: "RI_ConstraintTrigger_38015" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "interaction"  FROM "link_disease_interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'link_disease_interaction', 'interaction', 'UNSPECIFIED', 'interaction_id', 'id');

--
-- TOC Entry ID 424 (OID 38018)
--
-- Name: "RI_ConstraintTrigger_38017" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "interaction"  FROM "link_disease_interaction" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'link_disease_interaction', 'interaction', 'UNSPECIFIED', 'interaction_id', 'id');

--
-- TOC Entry ID 433 (OID 38020)
--
-- Name: "RI_ConstraintTrigger_38019" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "side_effect"  FROM "disease" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'side_effect', 'disease', 'UNSPECIFIED', 'disease', 'id');

--
-- TOC Entry ID 428 (OID 38022)
--
-- Name: "RI_ConstraintTrigger_38021" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "disease"  FROM "side_effect" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'side_effect', 'disease', 'UNSPECIFIED', 'disease', 'id');

--
-- TOC Entry ID 429 (OID 38024)
--
-- Name: "RI_ConstraintTrigger_38023" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "disease"  FROM "side_effect" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'side_effect', 'disease', 'UNSPECIFIED', 'disease', 'id');

--
-- TOC Entry ID 434 (OID 38026)
--
-- Name: "RI_ConstraintTrigger_38025" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "side_effect"  FROM "severity_code" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'side_effect', 'severity_code', 'UNSPECIFIED', 'severity', 'id');

--
-- TOC Entry ID 418 (OID 38028)
--
-- Name: "RI_ConstraintTrigger_38027" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "severity_code"  FROM "side_effect" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'side_effect', 'severity_code', 'UNSPECIFIED', 'severity', 'id');

--
-- TOC Entry ID 419 (OID 38030)
--
-- Name: "RI_ConstraintTrigger_38029" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "severity_code"  FROM "side_effect" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'side_effect', 'severity_code', 'UNSPECIFIED', 'severity', 'id');

--
-- TOC Entry ID 437 (OID 38032)
--
-- Name: "RI_ConstraintTrigger_38031" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "state"  FROM "country" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'state', 'country', 'UNSPECIFIED', 'country', 'code');

--
-- TOC Entry ID 435 (OID 38034)
--
-- Name: "RI_ConstraintTrigger_38033" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "country"  FROM "state" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'state', 'country', 'UNSPECIFIED', 'country', 'code');

--
-- TOC Entry ID 436 (OID 38036)
--
-- Name: "RI_ConstraintTrigger_38035" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "country"  FROM "state" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'state', 'country', 'UNSPECIFIED', 'country', 'code');

--
-- TOC Entry ID 440 (OID 38038)
--
-- Name: "RI_ConstraintTrigger_38037" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "urb"  FROM "state" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'urb', 'state', 'UNSPECIFIED', 'statecode', 'id');

--
-- TOC Entry ID 438 (OID 38040)
--
-- Name: "RI_ConstraintTrigger_38039" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "state"  FROM "urb" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'urb', 'state', 'UNSPECIFIED', 'statecode', 'id');

--
-- TOC Entry ID 439 (OID 38042)
--
-- Name: "RI_ConstraintTrigger_38041" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "state"  FROM "urb" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'urb', 'state', 'UNSPECIFIED', 'statecode', 'id');

--
-- TOC Entry ID 443 (OID 38044)
--
-- Name: "RI_ConstraintTrigger_38043" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "street"  FROM "urb" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'street', 'urb', 'UNSPECIFIED', 'id_urb', 'id');

--
-- TOC Entry ID 441 (OID 38046)
--
-- Name: "RI_ConstraintTrigger_38045" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "urb"  FROM "street" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'street', 'urb', 'UNSPECIFIED', 'id_urb', 'id');

--
-- TOC Entry ID 442 (OID 38048)
--
-- Name: "RI_ConstraintTrigger_38047" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "urb"  FROM "street" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'street', 'urb', 'UNSPECIFIED', 'id_urb', 'id');

--
-- TOC Entry ID 450 (OID 38050)
--
-- Name: "RI_ConstraintTrigger_38049" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "relation"  FROM "relation_types" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'relation', 'relation_types', 'UNSPECIFIED', 'id_relation_type', 'id');

--
-- TOC Entry ID 448 (OID 38052)
--
-- Name: "RI_ConstraintTrigger_38051" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "relation_types"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'relation_types', 'UNSPECIFIED', 'id_relation_type', 'id');

--
-- TOC Entry ID 449 (OID 38054)
--
-- Name: "RI_ConstraintTrigger_38053" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "relation_types"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'relation_types', 'UNSPECIFIED', 'id_relation_type', 'id');

--
-- TOC Entry ID 451 (OID 38056)
--
-- Name: "RI_ConstraintTrigger_38055" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "address"  FROM "address_type" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'address', 'address_type', 'UNSPECIFIED', 'addrtype', 'id');

--
-- TOC Entry ID 446 (OID 38058)
--
-- Name: "RI_ConstraintTrigger_38057" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "address_type"  FROM "address" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'address', 'address_type', 'UNSPECIFIED', 'addrtype', 'id');

--
-- TOC Entry ID 447 (OID 38060)
--
-- Name: "RI_ConstraintTrigger_38059" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "address_type"  FROM "address" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'address', 'address_type', 'UNSPECIFIED', 'addrtype', 'id');

--
-- TOC Entry ID 452 (OID 38062)
--
-- Name: "RI_ConstraintTrigger_38061" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "address"  FROM "street" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'address', 'street', 'UNSPECIFIED', 'number', 'id');

--
-- TOC Entry ID 444 (OID 38064)
--
-- Name: "RI_ConstraintTrigger_38063" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "street"  FROM "address" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'address', 'street', 'UNSPECIFIED', 'number', 'id');

--
-- TOC Entry ID 445 (OID 38066)
--
-- Name: "RI_ConstraintTrigger_38065" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "street"  FROM "address" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'address', 'street', 'UNSPECIFIED', 'number', 'id');

--
-- TOC Entry ID 453 (OID 38068)
--
-- Name: "RI_ConstraintTrigger_38067" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "names" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'names', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 454 (OID 38070)
--
-- Name: "RI_ConstraintTrigger_38069" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "names" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'names', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 455 (OID 38072)
--
-- Name: "RI_ConstraintTrigger_38071" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 456 (OID 38074)
--
-- Name: "RI_ConstraintTrigger_38073" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 457 (OID 38076)
--
-- Name: "RI_ConstraintTrigger_38075" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_relative', 'id');

--
-- TOC Entry ID 458 (OID 38078)
--
-- Name: "RI_ConstraintTrigger_38077" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_relative', 'id');

--
-- TOC Entry ID 459 (OID 38080)
--
-- Name: "RI_ConstraintTrigger_38079" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "identities_addresses" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'identities_addresses', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 460 (OID 38082)
--
-- Name: "RI_ConstraintTrigger_38081" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "identities_addresses" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'identities_addresses', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 461 (OID 38084)
--
-- Name: "RI_ConstraintTrigger_38083" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "names" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'names', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 462 (OID 38086)
--
-- Name: "RI_ConstraintTrigger_38085" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "names" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'names', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 463 (OID 38088)
--
-- Name: "RI_ConstraintTrigger_38087" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 464 (OID 38090)
--
-- Name: "RI_ConstraintTrigger_38089" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 465 (OID 38092)
--
-- Name: "RI_ConstraintTrigger_38091" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_relative', 'id');

--
-- TOC Entry ID 466 (OID 38094)
--
-- Name: "RI_ConstraintTrigger_38093" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "relation" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'relation', 'identity', 'UNSPECIFIED', 'id_relative', 'id');

--
-- TOC Entry ID 467 (OID 38096)
--
-- Name: "RI_ConstraintTrigger_38095" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "identity"  FROM "identities_addresses" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'identities_addresses', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 468 (OID 38098)
--
-- Name: "RI_ConstraintTrigger_38097" Type: TRIGGER Owner: syan
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "identity"  FROM "identities_addresses" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'identities_addresses', 'identity', 'UNSPECIFIED', 'id_identity', 'id');

--
-- TOC Entry ID 3 (OID 35679)
--
-- Name: clinician_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"clinician_id_seq"', 1, 'f');

--
-- TOC Entry ID 5 (OID 35731)
--
-- Name: session_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"session_id_seq"', 1, 'f');

--
-- TOC Entry ID 7 (OID 35845)
--
-- Name: doc_type_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"doc_type_id_seq"', 1, 'f');

--
-- TOC Entry ID 9 (OID 35879)
--
-- Name: db_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"db_id_seq"', 1, 'f');

--
-- TOC Entry ID 11 (OID 35925)
--
-- Name: distributed_db_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"distributed_db_id_seq"', 13, 't');

--
-- TOC Entry ID 13 (OID 35960)
--
-- Name: config_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"config_id_seq"', 1, 'f');

--
-- TOC Entry ID 15 (OID 36014)
--
-- Name: class_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"class_id_seq"', 3, 't');

--
-- TOC Entry ID 17 (OID 36065)
--
-- Name: substance_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"substance_id_seq"', 2, 't');

--
-- TOC Entry ID 19 (OID 36116)
--
-- Name: pregnancy_cat_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"pregnancy_cat_id_seq"', 1, 'f');

--
-- TOC Entry ID 21 (OID 36167)
--
-- Name: breastfeeding_cat_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"breastfeeding_cat_id_seq"', 1, 'f');

--
-- TOC Entry ID 23 (OID 36230)
--
-- Name: amount_unit_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"amount_unit_id_seq"', 8, 't');

--
-- TOC Entry ID 25 (OID 36265)
--
-- Name: drug_unit_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"drug_unit_id_seq"', 1, 'f');

--
-- TOC Entry ID 27 (OID 36303)
--
-- Name: drug_route_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"drug_route_id_seq"', 1, 'f');

--
-- TOC Entry ID 29 (OID 36338)
--
-- Name: drug_presentation_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"drug_presentation_id_seq"', 1, 'f');

--
-- TOC Entry ID 31 (OID 36374)
--
-- Name: drug_package_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"drug_package_id_seq"', 2, 't');

--
-- TOC Entry ID 33 (OID 36425)
--
-- Name: drug_manufacturer_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"drug_manufacturer_id_seq"', 1, 'f');

--
-- TOC Entry ID 35 (OID 36460)
--
-- Name: brand_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"brand_id_seq"', 1, 'f');

--
-- TOC Entry ID 37 (OID 36507)
--
-- Name: drug_flags_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"drug_flags_id_seq"', 1, 'f');

--
-- TOC Entry ID 39 (OID 36569)
--
-- Name: payor_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"payor_id_seq"', 1, 'f');

--
-- TOC Entry ID 41 (OID 36630)
--
-- Name: severity_code_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"severity_code_id_seq"', 1, 'f');

--
-- TOC Entry ID 43 (OID 36681)
--
-- Name: interaction_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"interaction_id_seq"', 1, 'f');

--
-- TOC Entry ID 45 (OID 36759)
--
-- Name: disease_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"disease_id_seq"', 1, 'f');

--
-- TOC Entry ID 47 (OID 36807)
--
-- Name: indication_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"indication_id_seq"', 1, 'f');

--
-- TOC Entry ID 49 (OID 36893)
--
-- Name: side_effect_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"side_effect_id_seq"', 1, 'f');

--
-- TOC Entry ID 51 (OID 36944)
--
-- Name: audit_gis_audit_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"audit_gis_audit_id_seq"', 217, 't');

--
-- TOC Entry ID 53 (OID 36996)
--
-- Name: state_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"state_id_seq"', 1, 'f');

--
-- TOC Entry ID 55 (OID 37040)
--
-- Name: urb_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"urb_id_seq"', 186, 't');

--
-- TOC Entry ID 57 (OID 37084)
--
-- Name: street_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"street_id_seq"', 1, 'f');

--
-- TOC Entry ID 59 (OID 37126)
--
-- Name: address_type_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"address_type_id_seq"', 1, 'f');

--
-- TOC Entry ID 61 (OID 37214)
--
-- Name: link_amount_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"link_amount_id_seq"', 1, 'f');

--
-- TOC Entry ID 63 (OID 37296)
--
-- Name: audit_identity_audit_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"audit_identity_audit_id_seq"', 72, 't');

--
-- TOC Entry ID 65 (OID 37330)
--
-- Name: identity_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"identity_id_seq"', 15, 't');

--
-- TOC Entry ID 67 (OID 37381)
--
-- Name: relation_types_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"relation_types_id_seq"', 9, 't');

--
-- TOC Entry ID 69 (OID 37426)
--
-- Name: relation_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"relation_id_seq"', 1, 'f');

--
-- TOC Entry ID 71 (OID 37473)
--
-- Name: identities_addresses_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"identities_addresses_id_seq"', 10, 't');

--
-- TOC Entry ID 73 (OID 37517)
--
-- Name: address_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"address_id_seq"', 10, 't');

--
-- TOC Entry ID 75 (OID 37574)
--
-- Name: names_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"names_id_seq"', 16, 't');

--
-- TOC Entry ID 77 (OID 37593)
--
-- Name: phone_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"phone_id_seq"', 25, 't');

--
-- TOC Entry ID 79 (OID 38099)
--
-- Name: clin_id_seq Type: SEQUENCE SET Owner: 
--

SELECT setval ('"clin_id_seq"', 83, 't');

