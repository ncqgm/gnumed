v-- structure of drug database for gnumed
-- Copyright 2000, 2001 by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.sql"
--
-- changelog:
-- 7.6.02: extensions for complex packages (i.e Losec HP7) 
-- 25.3.02: simplified to some tables for new
-- attempt at PBS import
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

--CREATE FUNCTION plpgsql_call_handler () RETURNS OPAQUE AS
--    '/usr/lib/pgsql/plpgsql.so' LANGUAGE 'C';

--CREATE TRUSTED PROCEDURAL LANGUAGE 'plpgsql'
--    HANDLER plpgsql_call_handler
--    LANCOMPILER 'PL/pgSQL';


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
'Unit to measure the preparation';

insert into amount_unit values (1, 'each'); -- for discrete objects:
-- tablets, capsules, etc.
insert into amount_unit values (2, 'gram'); -- for solid but
-- indiscrete: powders, pastes
insert into amount_unit values (3, 'millilitre'); -- for liquid
-- preparations: syrups, solutions
 


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

insert into drug_unit values (1, 'y', 'mg');
insert into drug_unit values (2, 'y', 'g');
insert into drug_unit values (3, 'y', 'ml');
insert into drug_unit values (4, 'n', 'unit');
insert into drug_unit values (5, 'n', 'international unit');



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
	name varchar (30)
);


-- ================================================
-- This table corresponds to each line in the PBS Yellow Book.
-- The manufacturer is linked to the strengths and pack sizes that they offer.

CREATE TABLE drug_package (
	id SERIAL PRIMARY KEY,
	max_rpts INTEGER, -- maximum repeats
	name VARCHAR (100), -- generic name(s) 
	description VARCHAR (100), -- extra presentation description
	course INTEGER -- in days, if prescription has a fixed course
	-- (e.g. 28 for Pill, 14 for Losec HP7)
);


-- most packages are homogenous: all tablets are of the same type, so
-- this table has one-to-one link with the previous.
-- some drug 'packs', notably Losec HP7, and triphasic contraceptives,
-- have several tablet types within the one packet, so several entries
-- in this table for one in drug_package.
CREATE TABLE drug_series
(
	id SERIAL,
	package INTEGER REFERENCES drug_package (id),	
	presentation INTEGER REFERENCES drug_presentation (id),
	route INTEGER REFERENCES drug_route (id),
	amount_unit INTEGER REFERENCES amount_unit (id),
	amount FLOAT, -- actual 'amount' of drug, so 100 for 100mL
	-- bottle, 28 for 28 tabs
);

-- Here's the money. Links substances to drugs. Obviously a drug can
-- have several substances (hence compounds)
CREATE TABLE link_subst_drug (
       series INTEGER REFERENCES drug_series (id),
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

CREATE TABLE link_brand_package (
       brand_id INTEGER REFERENCES brand (id),
       drug_id INTEGER REFERENCES drug_package (id),
       price MONEY	       
);

-- Note here that several brands may link to a single drug_package
-- entry.
-- This may be taken to imply that the drugs are clinically
-- interchangable.
-- If they are not, because of adjuvant, solute or other reason, a
-- seperate entry should exist in drug_package, and the difference
-- noted by drug_flags below.

-- =============================================
CREATE TABLE drug_flags (
	id SERIAL PRIMARY KEY,
	package INTEGER REFERENCES drug_package (id),
        description varchar(60),
        comment text
);

COMMENT ON TABLE drug_flags IS
'important searchable information relating to a drug such as sugar
free, gluten free, orange-flavoured, ...';

-- ==============================================
-- This is for formulary restriction imposed on the prescriber by a payor.

--- The payor, i.e PBS, NHS, private insurance collective, etc.
CREATE TABLE payor (
       id SERIAL,
       country CHAR (2), -- Internet two-letter code
       name VARCHAR (50),
);

-- restriction on a substance imposed by a payor
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
        description text,
	block BOOL default 'f'
);

COMMENT ON TABLE severity_code IS
'e.g. (contraindicated) (potentially life threatening) (not advisable) (caution) ...';

COMMENT ON COLUMN severity_code.block IS
'true indicates client should interrupt user if attempts to prescribe.';

-- =============================================

-- interaction between any substance or class of substances, or disease
-- ideally, this refers to the physicological site of interaction,
-- such as a cytochrome P450 enzyme, etc. Obviously for many
-- interactions, the comment has to be 'interaction between X and Y'.
CREATE TABLE interaction (
       id SERIAL PRIMARY KEY,
       comment text,
       severity INTEGER REFERENCES severity_code (id)
);


-- =====================================================
-- interactions involving drugs or classes of drugs
-- if the interaction is only known for a compound, link both substances in

CREATE TABLE link_subst_interaction (
	subst_id INTEGER NOT NULL REFERENCES substance (id),
	interaction_id INTEGER NOT NULL REFERENCES interaction (id),
	action CHAR DEFAULT NULL check (action in (NULL, 'S', 'I',
	'D')),
	-- this is for interactions mediated by enzymes or the like
	-- S = Substrate of the enzyme 
	-- I = Inhibits the enzyme
	-- D = inDuces the enzyme
	-- how useful is this? 
        comment text
);

COMMENT ON COLUMN link_subst_interaction.subst_id IS 'Index of substance table';


CREATE TABLE link_class_interaction (
	class_id INTEGER NOT NULL REFERENCES class (id),
	interaction_id INTEGER NOT NULL REFERENCES interaction (id),
	action CHAR DEFAULT NULL check (action in (NULL, 'S', 'I',
	'D')),
        comment text
);

COMMENT ON COLUMN link_class_interaction.class_id IS 'Index of class table';
-- this allows a class of drugs to 'inherit' the property of
-- the interaction


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
-- Proposed mechanism for therapeutic guidelines.



-- therapeutic option: such as 'SSRI antidepressant', for which
-- several entries may exist in prescription.
CREATE TABLE therapy (
       id SERIAL,
       indication INTEGER REFERENCES disease (id),
       line INTEGER, -- 1=first line, 2=second line, etc.
       comment TEXT, -- short text to decide which therapy amongst several
       handout TEXT, -- longer explanation for non-pharmacological
       -- therapies, such as the Hallpike manoeuvre.
       referral_specialty VARCHAR (10), -- the specialty, mainly if a
       -- procedural therapy
);
       

CREATE TABLE prescription (
       id SERIAL,
       therapy_id INTEGER REFERENCES therapy (id),
       adjunct INTEGER REFERENCES prescription (id),
       -- adjunct to another drug (compound drugs, e.g. co-amoxyclav) 
       -- NULL for the 'main' drug 
       drug INTEGER REFERENCES substance (id), -- use multiple entries
       course INTEGER, -- in days, 1 for stat dose, 0 if continuing
       frequency VARCHAR(5) DEFAULT 'mane' check (frequency in ('mane', 'nocte', 'bd', 'tds', 'qid')),
	-- Latin expressions for prescribing
	-- mane='morning', nocte='night', bd=twice daily, tds=three times daily
	-- qid=four times day. Are other times needed?
       dose FLOAT,
       unit INTEGER REFERENCES drug_unit (id),
       route INTEGER REFERENCES drug_route (id),
       dose_denominator CHAR DEFAULT 'A' check (dose_denominator in
       ('A', 'W', 'S')),
       -- A=absolute 
       -- W=by weight (kg)
       -- S=by computed surface area (m^2)
       max_dose FLOAT, -- absolute maximum. For many drugs the
       -- 'paediatric' dose may be encoded above as 'by weight', 
       -- and the adult dose can be placed here. Smaller adults may
       -- get the calculated paediatric dose: probably a good thing.    
       elderly_dose FLOAT, -- some drugs (like tricyclics) reduced
       -- dose recommended in elderly 
);

-- with this table, a list of indicated drugs would appear in a sidebox
-- when a diagnosis was entered, with interacting/contraindicated/allergic
-- drugs removed first. The prescriber could click on one to these to
-- bring up the prescription dialogue, pre-loaded with the drug.
-- paediatric dosing can be automatically calculated.

-- For drugs such as gentamicin and warfarin, client-side modules can 
-- adjust dosing dsing further


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
-- side-effects
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






