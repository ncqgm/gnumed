v-- structure of drug database for gnumed
-- Copyright 2000, 2001 by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.sql"
--
-- changelog: 20.10.01 (suggestions by Ian Haywood)
--		+ hierarchy of substance categories
--		+ drug-drug interactions removed 
-- (already have substance interactions)
--		+ therapeutic categories replaced by clinical guidelines
-- changelog: 13.10.2001
--		+ stripped down from original database
--		+ all references to gnumed_object removed
--		+ prepared for distributed servers & read-only database
--		+ prescription module separated from drug module
--		+ all permissions, triggers and rules removed
--		+ stripped all use of inheritance in favour of portability
--
-- TODO:
--	* testing
--	* debugging
-- 	* further normalization
--	* trigger maintained denormalized table(s) for fast read access of most common attributes


--=====================================================================

CREATE FUNCTION plpgsql_call_handler () RETURNS OPAQUE AS
    '/usr/lib/pgsql/plpgsql.so' LANGUAGE 'C';

CREATE TRUSTED PROCEDURAL LANGUAGE 'plpgsql'
    HANDLER plpgsql_call_handler
    LANCOMPILER 'PL/pgSQL';


CREATE TABLE class (
       id SERIAL PRIMARY KEY,
       name varchar (60),
	pharmacology TEXT,
       superclass INTEGER REFERENCES class (id)
);

CREATE TABLE substance (
	id SERIAL PRIMARY KEY,
	name  varchar(60),
	pharmacology TEXT,
	class INTEGER REFERENCES class (id)
);

--========================================

CREATE TABLE pregnancy_cat (
	id SERIAL PRIMARY KEY,
	code char(3),
	description text,
	comment text
);


CREATE TABLE breastfeeding_cat (
	id SERIAL PRIMARY KEY,
	code char(3),
	description text,
	comment text
);

CREATE TABLE obstetric_codes (
       drug_id INTEGER REFERENCES substance (id),
       preg_code INTEGER REFERENCES pregnancy_cat (id),
       brst_code INTEGER REFERENCES breastfeeding_cat (id)
);

-- =============================================

CREATE TABLE amount_unit (
        id SERIAL PRIMARY KEY,
        description varchar(20)
);

COMMENT ON TABLE amount_unit IS
'Example: ml, each, ..';


-- =============================================

CREATE TABLE drug_unit (
	id SERIAL PRIMARY KEY,
	is_SI boolean default 'y',
	description varchar(20)
);

COMMENT ON COLUMN drug_unit.is_SI IS
'Example: mg, mcg, ml, U, IU, ...';

COMMENT ON TABLE drug_unit IS
'true if it is a System International (SI) compliant unit';


-- =============================================

CREATE TABLE drug_route (
	id SERIAL PRIMARY KEY,
	description varchar(60)
); 

COMMENT ON table drug_route IS
'Examples: oral, i.m., i.v., s.c.';


-- =============================================
-- each 'type' of drug, like 'tablet', or 'capsule'


CREATE TABLE drug_presentation (
	id SERIAL PRIMARY KEY,
	name varchar (30),
	route INTEGER REFERENCES drug_route (id),
	amount_unit INTEGER REFERENCES amount_unit (id)
);


-- ================================================
-- This table corresponds to each line in the PBS Yellow Book.
-- The manufacturer is linked to the strengths and pack sizes that they offer.

CREATE TABLE drug_package (
	id SERIAL PRIMARY KEY,
	presentation INTEGER REFERENCES drug_presentation (id),
	packsize INTEGER, -- no. of tabs, capsules, etc. in pack
	amount FLOAT, -- actual 'amount' of drug, so 100 for 100mL bottle
	max_rpts INTEGER, -- maximum repeats
	description VARCHAR (100) -- extra description in source data
);


-- Here's the money. Links substances to packages. Obvious package can
-- have several drugs (hence compounds)
CREATE TABLE link_subst_package (
       package INTEGER REFERENCES drug_package (id),
       substance INTEGER REFERENCES substance (id),
       unit INTEGER REFERENCES drug_unit (id),
       amount FLOAT -- amount of drug
);

-- =============================================
-- Commercial data. Ugh!

CREATE TABLE drug_manufacturer (
	id SERIAL PRIMARY KEY,
	name varchar(60)
);

COMMENT ON TABLE drug_manufacturer IS
'Name of a drug company. Details like address etc. in separate table';

CREATE TABLE brand (
	id SERIAL PRIMARY KEY,
	drug_manufacturer_id INTEGER NOT NULL references drug_manufacturer(id),
        brand_name varchar(60)
);

CREATE TABLE link_brand_drug (
       brand_id INTEGER REFERENCES brand (id),
       drug_id INTEGER REFERENCES drug_package (id),
       price MONEY	       
);

-- =============================================
-- where does this link in?
CREATE TABLE drug_flags (
	id SERIAL PRIMARY KEY,
        description varchar(60),
        comment text
);

COMMENT ON TABLE drug_flags IS
'important searchable information relating to a drug such as sugar free, gluten free, ...';

-- sugqestion:
CREATE TABLE link_flag_package (
       flag_id INTEGER REFERENCES drug_flags(id),
       pack_id INTEGER REFERENCES drug_package (id)
);

-- ==============================================
-- This is for formulary restriction imposed on the prescriber by a payor.

--- The payor, i.e PBS, NHS, private insurance collective, etc.
CREATE TABLE payor (
       id SERIAL,
       country CHAR (2), -- Internet two-letter code
       name VARCHAR (50),
       state BOOL -- true if State-owned
);

-- restirction on a substance imposed by a payor
CREATE TABLE restriction (
       drug_id INTEGER REFERENCES substance (id),
       payor_id INTEGER REFERENCES payor (id),
       indication text,
       authority BOOL -- must contact for permission to prescribe
);

-- =============================================

CREATE TABLE severity_code (
	id SERIAL PRIMARY KEY,
	code CHAR(3),
        description text
);

COMMENT ON TABLE severity_code IS
'e.g. (contraindicated) (potentially life threatening) (not advisable) (caution) ...';


-- =============================================

-- interaction between any substance or class of substances, or disease

CREATE TABLE interaction (
       id SERIAL PRIMARY KEY,
       comment text,
       severity INTEGER REFERENCES severity_code (id)
);


-- =====================================================
-- interactions involving drugs or classes of drugs
-- if the interaction is only known for a compound, link both substances in

CREATE TABLE link_drug_interaction (
	drug_id INTEGER NOT NULL,
	class BOOL, -- 'true' for class, false for drug
	interaction_id INTEGER NOT NULL REFERENCES interaction (id) ,
        comment text
);


--=================================================
-- Diseases.
-- A number of false "diseases" can be linked in here, such 
-- as "childhood", "old age", "pregnancy", to add the appropriate
-- caution data
CREATE TABLE disease (
       id SERIAL,
       name varchar (100),
       ICD10 char[8]
);

COMMENT ON COLUMN disease.ICD10 IS 'ICD-10 code, if applicable';


-- =============================================
-- alternative to therapeutic classes, just a thought


CREATE TABLE indication (
       id SERIAL PRIMARY KEY,
       drug INTEGER REFERENCES drug_package (id),
       course INTEGER, -- in days, 1 for stat dose, 0 if continuing
	frequency character(5) DEFAULT 'mane' check (frequency in ('mane', 'nocte', 'bd', 'tds', 'qid')),
	-- For non-med people: these are Latin expressions for prescribing
	-- mane='morning', nocte='night', bd=twice daily, tds=three times daily
	-- qid=four times day.
       paed_dose FLOAT, -- paediatric dose, units/kg
       min_dose FLOAT, -- adult minimum dose
       max_dose FLOAT, -- adult maximum dose
       comment TEXT,
       line INTEGER -- 1=first-line, 2=second-line, etc.
);

-- with this table, a list of indicated drugs would appear in a sidebox
-- when a diagnosis was entered, with interacting/contraindicated/allergic
-- drugs removed a priori. The prescriber could click on one to these to
-- bring up the prescription dialogue, pre-loaded with the drug.
-- paediatric dosing can be automatically calculated.		          

--=============================================
-- link diseases to interactions -- i.e contraindications
-- if the complication is only known for a compounds, link both substances 
CREATE TABLE link_disease_interaction (
	disease_id INTEGER NOT NULL REFERENCES disease (id),
	interaction_id INTEGER NOT NULL REFERENCES interaction (id),
        comment text
);


COMMENT ON TABLE link_disease_interaction IS
'allows any number of drug-disease interactions for any given drug';


--===============================================
-- side-effects: diseases *caused* by a substances
-- obviously, the word 'disease' is used flexibly: 'nausea', 'diarrhoea'
-- are symptoms, but will be listed in the table above. 

CREATE TABLE side_effect (
       id SERIAL,
       drug_id INTEGER NOT NULL,
       class BOOL,
       disease INTEGER REFERENCES disease (id),
       comment TEXT,
       frequency INTEGER, -- rough % of patients
       severity INTEGER REFERENCES severity_code (id)
);
