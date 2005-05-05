-- structure of drug database for gnumed
-- Copyrigth 2000, 2001 by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.sql"
--
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


CREATE TABLE substance_class (
	id SERIAL PRIMARY KEY,
	name  varchar(60)
);

COMMENT ON TABLE substance_class IS
'substance class. Example: tricyclics, macrolides, etc.';

-- =============================================


CREATE TABLE therapeutic_superclass (
	id SERIAL PRIMARY KEY,
	name  varchar(60)
);

COMMENT ON TABLE therapeutic_superclass IS
'therapeutic superclass. Example: antiinfectives (superclass for antibiotics, antivirals, antifungals ...)';


-- =============================================


CREATE TABLE therapeutic_class (
	id SERIAL PRIMARY KEY,
	superclass_id INTEGER REFERENCES therapeutic_superclass(id),
	name  varchar(60)
);

COMMENT ON TABLE therapeutic_class IS
'therapeutic class. Example: antibiotics, antihypertensives, etc.';

-- =============================================

CREATE TABLE substance (
	id SERIAL PRIMARY KEY,
	name  varchar(60)
);

COMMENT ON TABLE substance_class IS
'single ("atomic") pharmacological substances. Example: Trimethoprim, Sulfamethoxazole etc.';

-- =============================================


CREATE TABLE link_substance_therclass (
	substance_id INTEGER REFERENCES substance(id),
	therclass_id INTEGER REFERENCES therapeutic_class(id)
);

COMMENT ON TABLE link_substance_therclass IS
'Facilitates many-to-many relationships between substances and therapeutic classes';

CREATE INDEX idx_link_substance_therclass1 ON link_substance_therclass(substance_id);
CREATE INDEX idx_link_substance_therclass2 ON link_substance_therclass(therclass_id);

-- =============================================

CREATE TABLE link_substance_substclass (
	substance_id INTEGER REFERENCES substance(id),
	substclass_id INTEGER REFERENCES substance_class(id)
);

CREATE INDEX idx_link_substance_substclass1 ON link_substance_substclass(substance_id);
CREATE INDEX idx_link_substance_substclass2 ON link_substance_substclass(substclass_id);

-- =============================================


CREATE TABLE pregnancy_cat (
	id SERIAL PRIMARY KEY,
	code char(3),
	description text,
	comment text
);

-- =============================================


CREATE TABLE breastfeeding_cat (
	id SERIAL PRIMARY KEY,
	code char(3),
	description text,
	comment text
);

-- =============================================

CREATE TABLE generic_drug (
	id SERIAL PRIMARY KEY,
	pregnancy_cat_id INTEGER NOT NULL REFERENCES pregnancy_cat(id) ,
	breastfeeding_cat_id INTEGER NOT NULL REFERENCES breastfeeding_cat(id) ,
        name varchar(60)
);

-- =============================================

CREATE TABLE link_gendrug_components (
	generic_drug_id INTEGER REFERENCES generic_drug(id),
	substance_id INTEGER REFERENCES substance(id)
);

COMMENT ON TABLE link_gendrug_components IS
'Facilitates many-to-many relationships between drug entities and drug components (substances)';

CREATE INDEX idx_link_gendrug_components1 ON link_gendrug_components(generic_drug_id);
CREATE INDEX idx_link_gendrug_components2 ON link_gendrug_components(substance_id);

-- =============================================

-- the therapeutic class of a compound drug can be different from the
-- therapeutic classes of it's components! Hence, an additional m2m relationship

CREATE TABLE link_gendrug_therclass (
	generic_drug_id INTEGER NOT NULL REFERENCES generic_drug(id) ,
	therclass_id INTEGER NOT NULL REFERENCES therapeutic_class(id)
);

COMMENT ON TABLE link_gendrug_therclass IS
'allows many-to-many relationship between drugs and therapeutic classes';


CREATE INDEX idx_link_gendrug_therclass1 ON link_gendrug_therclass(generic_drug_id);
CREATE INDEX idx_link_gendrug_therclass2 ON link_gendrug_therclass(therclass_id);

-- =============================================

-- the substance class of a compound drug can be different from the
-- substance classes of it's components! Hence, an additional m2m relationship

CREATE TABLE link_gendrug_substclass (
	generic_drug_id INTEGER NOT NULL REFERENCES generic_drug(id) ,
	substclass_id INTEGER NOT NULL REFERENCES substance_class(id)
);

COMMENT ON TABLE link_gendrug_substclass IS
'allows many-to-many relationship between drugs and substance classes';


CREATE INDEX idx_link_gendrug_substclass1 ON link_gendrug_substclass(generic_drug_id);
CREATE INDEX idx_link_gendrug_substclass2 ON link_gendrug_substclass(substclass_id);

-- =============================================

CREATE TABLE drug_manufacturer (
	id SERIAL PRIMARY KEY,
	name varchar(60)
);

COMMENT ON TABLE drug_manufacturer IS
'Name of a drug company. Details like address etc. in separate table';

-- =============================================

CREATE TABLE branded_drug (
	id SERIAL PRIMARY KEY,
	generic_drug_id INTEGER NOT NULL references generic_drug(id),
	drug_manufacturer_id INTEGER NOT NULL references drug_manufacturer(id),
        brand_name varchar(60)
);

-- =============================================

CREATE TABLE drug_units (
	id SERIAL PRIMARY KEY,
	is_SI boolean default 'y',
	description char[20]
);

COMMENT ON COLUMN drug_units.is_SI IS
'Example: mg, mcg, ml, U, IU, ...';

COMMENT ON TABLE drug_units IS
'true if it is a System International (SI) compliant unit';

-- =============================================

CREATE TABLE amount_units (
	id SERIAL PRIMARY KEY,
	description char[20]
);

COMMENT ON TABLE amount_units IS
'Example: ml, each, ..';


-- =============================================


CREATE TABLE drug_presentation (
	id SERIAL PRIMARY KEY,
	scored boolean DEFAULT 'f',
        description varchar(60)
);


COMMENT ON table drug_presentation IS
'e.g. tablet, capsule, syrup-sugarfree ...';

-- =============================================


CREATE TABLE drug_route (
	id SERIAL PRIMARY KEY,
	description varchar(60)
);

COMMENT ON table drug_route IS
'Examples: oral, i.m., i.v., s.c.';

-- =============================================

CREATE TABLE drug (
	id SERIAL PRIMARY KEY,
	route INTEGER REFERENCES drug_route(id),
	unit INTEGER REFERENCES drug_units(id),
	strength FLOAT
);

-- =============================================

CREATE TABLE drug_package (
	id SERIAL PRIMARY KEY,
	drug_id INTEGER REFERENCES drug(id),
	branded_drug_id INTEGER REFERENCES branded_drug(id) default NULL,
	amount INTEGER,
	amount_unit INTEGER REFERENCES amount_units(id)
);

-- =============================================

CREATE TABLE drug_flags (
	id SERIAL PRIMARY KEY,
        description varchar(60),
        comment text
);

COMMENT ON TABLE drug_flags IS
'important searchable information relating to a drug such as sugar free, gluten free, ...';


-- =============================================

CREATE TABLE drug_warning_categories (
	id SERIAL PRIMARY KEY,
        description text
);

COMMENT ON TABLE drug_warning_categories IS
'e.g. (potentially life threatening complication) (drug-disease interaction check neccessary) ...';

-- =============================================

CREATE TABLE substance_warning (
	substance_id INTEGER NOT NULL REFERENCES substance(id) ,
	drug_warning_categories_id INTEGER NOT NULL REFERENCES drug_warning_categories(id) ,
	warning text
);

COMMENT ON TABLE substance_warning IS
'allows to link searchable categories of warning messages to any drug component';

-- =============================================

CREATE TABLE drug_warning (
	drug_id INTEGER NOT NULL REFERENCES generic_drug(id) ,
	drug_warning_categories_id INTEGER NOT NULL REFERENCES drug_warning_categories(id) ,
	warning text
);

COMMENT ON TABLE drug_warning IS
'allows to link searchable categories of warning messages to any drug';

-- =============================================

CREATE TABLE drug_interaction_categories (
	id SERIAL PRIMARY KEY,
	code CHAR(3),
        description text
);

COMMENT ON TABLE drug_interaction_categories IS
'e.g. (contraindicated) (potentially life threatening) (not advisable) (caution) ...';


-- =============================================


CREATE TABLE drug_interaction (
	id SERIAL PRIMARY KEY,
	drug_interaction_categories_id INTEGER NOT NULL REFERENCES drug_interaction_categories(id) ,
        description text
);


-- =============================================


CREATE TABLE substance_class_interaction (
        id SERIAL PRIMARY KEY,
	substclass1_id INTEGER NOT NULL REFERENCES substance_class(id) ,
	substclass2_id INTEGER NOT NULL REFERENCES substance_class(id) ,
	drug_interaction_id INTEGER NOT NULL REFERENCES drug_interaction(id) ,
        comment text
);


COMMENT ON TABLE substance_class_interaction IS
'allows any number of substance class interactions for any given drug';


CREATE TABLE substance_interaction (
        id SERIAL PRIMARY KEY,
	subst1_id INTEGER NOT NULL REFERENCES substance(id) ,
	subst2_id INTEGER NOT NULL REFERENCES substance(id) ,
	drug_interaction_id INTEGER NOT NULL REFERENCES drug_interaction(id) ,
        comment text
);


COMMENT ON TABLE substance_interaction IS
'allows any number of substance interactions for any given drug';

-- =============================================



CREATE TABLE drug_drug_interaction (
        id SERIAL PRIMARY KEY,
	drug1_id INTEGER NOT NULL REFERENCES generic_drug(id) ,
	drug2_id INTEGER NOT NULL REFERENCES generic_drug(id) ,
	drug_interaction_id INTEGER NOT NULL REFERENCES drug_interaction(id) ,
        comment text
);


COMMENT ON TABLE drug_drug_interaction IS
'allows any number of drug-drug interactions for any given drug';


-- =============================================

CREATE TABLE drug_disease_interaction (
        id SERIAL PRIMARY KEY,
	drug_id INTEGER NOT NULL REFERENCES generic_drug(id) ,
	diseasecode char[8],
	drug_interaction_id INTEGER NOT NULL REFERENCES drug_interaction(id) ,
        comment text
);


COMMENT ON TABLE drug_disease_interaction IS
'allows any number of drug-disease interactions for any given drug';

COMMENT ON COLUMN drug_disease_interaction.diseasecode IS
'preferrably ICD10 codes here.';