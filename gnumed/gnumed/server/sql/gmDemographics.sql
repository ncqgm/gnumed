-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- location related tables
-- ===================================================================
-- no auditing neccessary, as this table only uses
-- original ISO data (= reference verifiable any time)
create table country (
	id serial primary key,
	code char(2) unique not null,
	name text not null,
	deprecated date default null
);

COMMENT ON TABLE country IS
	'countries coded per ISO 3166-1';
COMMENT ON COLUMN country.code IS
	'international two character country code as per ISO 3166-1';
COMMENT ON COLUMN country.deprecated IS
	'date when this country ceased officially to exist (if applicable)';

-- ===================================================================
-- state codes: any need for more than 3 characters?
-- yes, in Germany we have up to 6
create table state (
	id serial primary key,
	code char(10) not null,
	country char(2) not null references country(code),
	name text not null,
	unique (code, country)
) inherits (audit_fields, audit_mark);

COMMENT ON TABLE state IS
	'state codes (country specific)';
COMMENT ON COLUMN state.code IS
	'state code';
COMMENT ON COLUMN state.country IS
	'2 character ISO 3166-1 country code';

create table log_state (
        id integer not null,
        code char(10) not null,
        country char(2) not null,
        name text not null
) inherits (audit_trail);

-- ===================================================================
create table urb (
	id serial primary key,
	id_state integer not null references state(id),
	postcode varchar(12) default null,
	name text not null,
	unique (id_state, postcode, name)
) inherits (audit_fields, audit_mark);

-- this does not work in the UK! Seperate postcodes for each street,
-- Same in Germany ! Postcodes can be valid for:
-- - several smaller urbs
-- - one urb
-- - several streets in one urb
-- - one street in one urb
-- - part of one street in one urb
-- Take that !  :-)

COMMENT ON TABLE urb IS
	'cities, towns, dwellings ...';
COMMENT ON COLUMN urb.id_state IS
	'reference to information about country and state';
COMMENT ON COLUMN urb.postcode IS
	'the postcode (if applicable';
COMMENT ON COLUMN urb.name IS
	'the name of the city/town/dwelling';

create table log_urb (
	id integer not null,
	id_state integer not null,
	postcode varchar(12),
	name text not null
) inherits (audit_trail);

-- ===================================================================
create table street (
	id serial primary key,
	id_urb integer not null references urb(id),
	name text not null,
	postcode varchar(12),
	unique(id_urb, name)
) inherits (audit_fields, audit_mark);

COMMENT ON TABLE street IS
	'street names, specific for distinct "urbs"';
COMMENT ON COLUMN street.id_urb IS
	'reference to information postcode, city, country and state';
COMMENT ON COLUMN street.name IS
	'name of this street';
COMMENT ON COLUMN street.postcode IS
	'postcode for systems (such as UK Royal Mail) which specify the street';


create table log_street (
	id integer not null,
	id_urb integer not null,
	name text not null,
	postcode varchar(12)
) inherits (audit_trail);

-- ===================================================================
create table address (
	id serial primary key,
	-- indirectly references urb(id)
	id_street integer not null references street(id),
	suburb text default null,
	number char(10) not null,
	addendum text
) inherits (audit_fields, audit_mark);

comment on table address is
	'an address aka a location';
comment on column address.id_street is
	'the street this address is at, from
	 whence the urb is to be found';
comment on column address.suburb is
	'the suburb this address is in (if any)';
comment on column address.number is
	'number of the house';
comment on column address.addendum is
	'eg. appartment number, room number, level, entrance';

create table log_address (
	id integer not null,
	id_street integer not null,
	suburb text,
	number char(10) not null,
	addendum text
) inherits (audit_trail);

-- ===================================================================
-- Other databases may reference to an address stored in this table.
-- As Postgres does not allow (yet) cross database queries, we use
-- external reference tables containing "external reference" counters
-- in order to preserve referential integrity
-- (no address shall be deleted as long as there is an external object
-- referencing this address)
create table address_external_ref (
	id serial primary key,
	id_address integer references address(id),
	refcounter int default 0
);

-- ===================================================================
create table address_type (
	id serial primary key,
	"name" text unique not null
);

-- ===================================================================
create table enum_comm_types (
	id serial primary key,
	description text unique not null
);

create table comm_channel (
	id serial primary key,
	id_type integer not null references enum_comm_types(id),
	url text not null,
	unique(id_type, url)
);

comment on table comm_channel is
	'stores reachability information';
comment on column comm_channel.id_type is
	'the type of communication channel';
comment on column comm_channel.url is
	'the actual connection information such as a
	 a phone number, email address, pager number, etc.';

-- ===================================================================

-- the following table still needs a lot of work.
-- especially the GPS and map related information needs to be
-- normalized

-- added IH 8/3/02
-- table for street civilian type maps, i.e Melways
create table mapbook (
       id serial primary key,
       name char (30)
);

-- ===================================================================
-- table for co-ordinate systems, such at latitude-longitude
-- there are others, military, aviation and country-specific.
-- GPS handsets can display several.
create table coordinate (
      id serial primary key,
      name varchar (30),
      scale float
);
      -- NOTE: this converts distances from the co-ordinate units to
      -- kilometres.
      -- theoretically this may be problematic with some systems due to the
      -- ellipsoid nature of the Earth, but in reality it is unlikely to matter

-- ===================================================================
create table address_info (
        id serial primary key,
        id_address integer references address(id),
        location point,
        id_coord integer references coordinate (id),
        mapref char(30),
        id_map integer references mapbook (id),
        howto_get_there text,
        comments text
) inherits (audit_fields, audit_mark);

-- this refers to a SQL point type. This would allow us to do
-- interesting queries, like, how many patients live within
-- 10kms of the clinic.

create table log_address_info (
        id integer,
        id_address integer not null,
        location point,
        id_coord integer not null,
        mapref char(30),
        id_map integer not null,
        howto_get_there text,
        comments text
) inherits (audit_trail);

-- ===================================================================
-- person related tables
-- ===================================================================
create table identity (
	id serial primary key,
	pupic char(24),
	gender varchar(2) DEFAULT '?' check (gender in ('m', 'f', 'h', 'tm', 'tf', '?')),
	karyotype character(10) default null,
	dob timestamp with time zone not null,
	cob char(2),
	deceased timestamp with time zone null
) inherits (audit_mark, audit_fields);

comment on table identity IS
	'represents the unique identity of a person';
comment on column identity.pupic IS
	'Portable Unique Person Identification Code as per gnumed white papers';
comment on column identity.gender is
	'(m)ale,
	 (f)emale,
	 (h)ermaphrodite,
	 tm - (t)ranssexual phenotype (m)ale,
	 tf - (t)ranssexual phenotype (f)emale,
	 ? - unknown';
comment on column identity.dob IS
	'date/time of birth';
comment on column identity.cob IS
	'country of birth as per date of birth, coded as 2 character ISO code';
comment on column identity.deceased IS
	'date when a person has died (if so), format yyyymmdd';

create table log_identity (
	id integer not null,
	pupic char(24),
	gender varchar(2) not null,
	karyotype character(10),
	dob timestamp with time zone not null,
	cob char(2),
	deceased timestamp with time zone
) inherits (audit_trail);

-- ==========================================================
-- as opposed to the versioning of all other tables, changed names
-- should not be moved into the audit trail tables. Search functionality
-- must be available at any time for all names a person ever had.

create table names (
	id serial primary key,
	id_identity integer references identity,
	active boolean default 't',
	lastnames text not null,
	firstnames text not null,
	preferred text,
	-- yes, there are some incredible rants of titles ...
	title text
);

comment on table names IS
	'all the names an identity is known under';
comment on column names.active IS
	'true if the name is still in use';
comment on column names.firstnames IS
	'all first names of an identity in legal order';
comment on column names.lastnames IS
	'all last names of an identity in legal order';
comment on column names.preferred IS
	'preferred first name, the name a person is usually called (nickname)';

-- ==========================================================
create table person_addresses (
	id serial primary key,
	id_identity integer references identity,
	id_address integer references address,
	id_type int references address_type default 1,
	address_source varchar(30)
);

COMMENT ON TABLE person_addresses IS
	'a many-to-many pivot table linking addresses to identities';
COMMENT ON COLUMN person_addresses.id_identity IS
	'identity to whom the address belongs';
COMMENT ON COLUMN person_addresses.id_address IS
	'address belonging to this identity';
COMMENT ON COLUMN person_addresses.id_type IS
	'type of this address (like home, work, parents, holidays ...)';

-- ==========================================================
create table person_comm_channels (
	id serial primary key,
	id_identity integer not null references identity(id),
	id_comm integer not null references comm_channel(id),
	is_confidential bool not null default false,
	unique (id_identity, id_comm)
);

-- ==========================================================
-- theoretically, the only information needed to establish any kind of
-- biological family tree would be information about parenthood.
-- However, sometimes social family trees are equally important and at
-- other times information about parenthood is not known or uncertain
-- and it is still useful to record whatever information we can gather.
-- Thus, we need a variety of relationship types

create table relation_types (
	id serial primary key,
	biological boolean not null,
	biol_verified boolean default false,
	description text
) inherits (audit_mark, audit_fields);

comment on table relation_types IS
	'types of biological/social relationships between identities';
comment on column relation_types.biological IS
	'true if relationship is biological (proven or
	 reasonable assumption), else false';
comment on column relation_types.biol_verified IS
	'ONLY true if there is genetic proof for this relationship';
comment on column relation_types.description IS
	'plain text description of relationship';

create table log_relation_types (
	id integer not null,
	biological boolean not null,
	biol_verified boolean,
	description text
) inherits (audit_trail);

-- ==========================================================
create table relation (
	id serial primary key,
	id_identity integer not null references identity,
	id_relative integer not null references identity,
	id_relation_type integer not null references relation_types,
	started date default NULL,
	ended date default NULL
) inherits (audit_mark, audit_fields);

comment on table relation IS
	'biological and social relationships between an identity and other identities';
comment on column relation.id_identity IS
	'primary identity to whom the relationship applies';
comment on column relation.id_relative IS
	'referred identity of this relationship (e.g. "child"
	if id_identity points to the father and id_relation_type
	points to "parent")';
comment on column relation.started IS
	'date when this relationship began';
comment on column relation.ended IS
	'date when this relationship ended, biological
	 relationships do not end !';

create table log_relation (
	id integer not null,
	id_identity integer not null,
	id_relative integer not null,
	id_relation_type integer not null,
	started date,
	ended date
) inherits (audit_trail);

-- ===================================================================
-- organisation related tables
-- ===================================================================
create table org_address (
	id serial primary key,
	id_address integer not null references address(id),
	is_head_office bool not null default true,
	is_postal_address bool not null default true,
	unique (id_address, is_head_office, is_postal_address)
) ;

comment on table org_address is
	'tailors the standard address table for use by organisations';
comment on column org_address.id_address is
	'points to the address row belonging to this org';
comment on column org_address.is_head_office is
	'whether the head office is at this address';
comment on column org_address.is_postal_address is
	'whether this is the address to send snail mail to';

-- ===================================================================
create table org_category (
	id serial primary key,
	description text unique not null
);

-- ===================================================================
-- the main organisation table,
-- equivalent to identity but for non-people,
-- measurements will link to this, for example
create table org (
	id serial primary key,
	id_address integer not null references org_address(id),
	id_category integer not null references org_category(id),
	description text not null,
	unique(id_address, id_category, description)
);

-- ===================================================================
-- permissions
-- ===================================================================
-- FIXME: until proper permissions system is developed,
-- otherwise new users  can spend hours wrestling with
-- postgres permissions
GRANT SELECT ON
	names,
	identity,
	identity_id_seq
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	names,
	names_id_seq,
	identity_id_seq
TO GROUP "_gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.sql,v $', '$Revision: 1.3 $');

-- ===================================================================
-- $Log: gmDemographics.sql,v $
-- Revision 1.3  2003-08-05 09:16:46  ncq
-- - cleanup
--
-- Revision 1.2  2003/08/02 13:17:05  ncq
-- - add audit tables
-- - cleanup
--
-- Revision 1.1  2003/08/01 22:31:31  ncq
-- - schema for service "demographics" (personalia)
--
