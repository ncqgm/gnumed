-- project: GNUMed
-- database: PERSON
-- purpose:  unique identifier for a person and a person's relationships
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)
-- version: 0.1
-- changelog:
-- 20.10.2001:  (hherb) identity related tables separated from gnumed main database
--              in order to facilitate use of distributed servers.
--
--              All data integrity checking and versioning taken out of this code, now handled
--              by backend driven log mechanism resp. generated automatically by another script.
--
--              In order to simplfy and heed performance, normalization of "names" undone
--
--              All address related items have been moved into a separate database
--              in order to use GIS servers where available


-- ==========================================================

-- any table that needs auditing MUST inherit audit_identity.
-- A python script (gmhistorian.py) generates automatically all triggers
-- and tables neccessary to allow versioning and audit trail keeping of
-- these tables

create table audit_identity (
	audit_id serial primary key
);

COMMENT ON TABLE audit_identity IS
'not for direct use - must be inherited by all auditable tables';


-- ==========================================================

create table identity (
	id serial primary key,
	pupic char(24),
	gender character(2) DEFAULT '?' check (gender in ('m', 'f', 'h', 'tm', 'tf', '?')),
	karyotype character(10),
	dob char(8),
	cob char(2),
	deceased date default NULL
) inherits (audit_identity);


COMMENT ON TABLE identity IS
'represents the unique identity of a person';

COMMENT ON COLUMN identity.pupic IS
'Portable Unique Person Identification Code as per gnumed white papers';

COMMENT ON COLUMN identity.gender is
'(m)ale, (f)emale, (h)ermaphrodite, (tm)transsexual phaenotype male, (tf)transsexual phaenotype female, (?)unknown';

COMMENT ON COLUMN identity.dob IS
'date of birth';

COMMENT ON COLUMN identity.cob IS
'country of birth as per date of birth, coded as 2 character ISO code';

COMMENT ON COLUMN identity.deceased IS
'date when a person has died (if)';


-- ==========================================================

-- as opposed to the versioning of all other tables, changed names
-- should not be moved into the audit trail tables. Search functionality
-- must be available at any time for all names a person ever had.
-- we still need a smart and efficient trigger function that ensures that
-- there is only ONE "active" names record for any given identity at any
-- given time

create table names (
	id serial primary key,
	id_identity integer references identity,
	active boolean default 't',
	lastnames varchar (80),
	firstnames varchar(255),
	aka varchar (80),
	preferred varchar(80)
) inherits (audit_identity);

COMMENT ON TABLE names IS
'all the names an identity is known under';

COMMENT ON COLUMN names.active IS
'true if the name is still in use';

COMMENT ON COLUMN names.firstnames IS
'all first names of an identity in legal order';

COMMENT ON COLUMN names.lastnames IS
'all last names of an identity in legal order';

COMMENT ON COLUMN names.aka IS
'also known as ...';

COMMENT ON COLUMN names.preferred IS
'the preferred first name, the name a person is usually called';

-- ==========================================================

-- theoretically, the only information needed to establish any kind of
-- biological family tree would be information about parenthood.
-- However, sometimes social family trees are equally important and at
-- other times information about parenthood is not known or uncertain
-- and it is still useful to record whatever information we can gather.
-- Thus, we need a variety of relationship types

create table relation_types (
	id serial primary key,
	biological boolean,
	biol_verified boolean default false,
	description varchar(40)
) inherits (audit_identity);

COMMENT ON TABLE relation_types IS
'types of biological and social relationships between an identities';

COMMENT ON COLUMN relation_types.biological IS
'true id the relationship is biological (proven or reasonable assumption), else false';

COMMENT ON COLUMN relation_types.biol_verified IS
'ONLY set to true if there is genetic proof for this relationship';

COMMENT ON COLUMN relation_types.description IS
'plain text description of relationship';

--!!I18N!!
-- TRANSLATORS: please do NOT alter the sequence or insert anything; just translate!
-- Only that way we will be able to exchange relationship details between multilingual
-- databases. Hopefully, we will soon have an ontology taking care of this problem.

insert into relation_types(biological, description) values('t', 'parent');
insert into relation_types(biological, description) values('t', 'sibling');
insert into relation_types(biological, description) values('t', 'halfsibling');
insert into relation_types(biological, description) values('f', 'stepparent');
insert into relation_types(biological, description) values('f', 'married');
insert into relation_types(biological, description) values('f', 'defacto');
insert into relation_types(biological, description) values('f', 'divorced');
insert into relation_types(biological, description) values('f', 'separated');
insert into relation_types(biological, description) values('f', 'legal_guardian');

-- ==========================================================

create table relation (
	id serial primary key,
	id_identity integer references identity,
	id_relative integer references identity,
	id_relation_type integer references relation_types,
	started date default NULL,
	ended date default NULL
) inherits (audit_identity);

COMMENT ON TABLE relation IS
'biological and social relationships between an identity and other identities';

COMMENT ON COLUMN relation.id_identity IS
'primary identity to whom the relationship applies';

COMMENT ON COLUMN relation.id_relative IS
'referred identity of this relationship (e.g. "child" if id_identity points to the father and id_relation_type points to "parent")';

COMMENT ON COLUMN relation.started IS
'date when this relationship begun';

COMMENT ON COLUMN relation.ended IS
'date when this relationship ended. Biological relationships do not end!';

create table identities_addresses (
	id serial primary key,
	id_identity integer references identity,
	id_address integer, -- should be a foreign key, but might be "outsourced"
	address_source char(80) default NULL
) inherits (audit_identity);

COMMENT ON TABLE identities_addresses IS
'a many-to-many pivot table linking addresses to identities';

COMMENT ON COLUMN identities_addresses.id_identity IS
'identity to whom the address belongs';

COMMENT ON COLUMN identities_addresses.id_address IS
'address belonging to this identity';

COMMENT ON COLUMN identities_addresses.address_source IS
'URL of some sort allowing to reproduce where the address is sourced from';

