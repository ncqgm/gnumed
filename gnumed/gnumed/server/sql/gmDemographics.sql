-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics.sql,v $
-- $Revision: 1.10 $
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
) inherits (audit_fields);

select add_table_for_audit('state');

COMMENT ON TABLE state IS
	'state codes (country specific)';
COMMENT ON COLUMN state.code IS
	'state code';
COMMENT ON COLUMN state.country IS
	'2 character ISO 3166-1 country code';

-- ===================================================================
create table urb (
	id serial primary key,
	id_state integer not null references state(id),
	postcode varchar(12) not null,
	name text not null,
	unique (id_state, postcode, name)
) inherits (audit_fields);

-- this does not work in the UK! Seperate postcodes for each street,
-- Same in Germany ! Postcodes can be valid for:
-- - several smaller urbs
-- - one urb
-- - several streets in one urb
-- - one street in one urb
-- - part of one street in one urb
-- Take that !  :-)

select add_table_for_audit('urb');

COMMENT ON TABLE urb IS
	'cities, towns, dwellings ...';
COMMENT ON COLUMN urb.id_state IS
	'reference to information about country and state';
COMMENT ON COLUMN urb.postcode IS
	'the postcode (if applicable';
COMMENT ON COLUMN urb.name IS
	'the name of the city/town/dwelling';

-- ===================================================================
create table street (
	id serial primary key,
	id_urb integer not null references urb(id),
	name text not null,
	postcode varchar(12),
	unique(id_urb, name)
) inherits (audit_fields);

select add_table_for_audit('street');

COMMENT ON TABLE street IS
	'street names, specific for distinct "urbs"';
COMMENT ON COLUMN street.id_urb IS
	'reference to information postcode, city, country and state';
COMMENT ON COLUMN street.name IS
	'name of this street';
COMMENT ON COLUMN street.postcode IS
	'postcode for systems (such as UK Royal Mail) which specify the street';

-- ===================================================================
create table address (
	id serial primary key,
	-- indirectly references urb(id)
	id_street integer not null references street(id),
	suburb text default null,
	number char(10) not null,
	addendum text
) inherits (audit_fields);

select add_table_for_audit('address');

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
) inherits (audit_fields);

select add_table_for_audit('address_info');

-- this refers to a SQL point type. This would allow us to do
-- interesting queries, like, how many patients live within
-- 10kms of the clinic.

-- ===================================================================
-- person related tables
-- ===================================================================
create table identity (
	id serial primary key,
	pupic char(24),
	gender varchar(2) DEFAULT '?' check (gender in ('m', 'f', 'h', 'tm', 'tf', '?', 'N/A')),
	karyotype character(10) default null,
	dob timestamp with time zone not null,
	cob char(2),
	-- FIXME: constraint: deceased > dob
	deceased timestamp with time zone default null
) inherits (audit_fields);

select add_table_for_audit('identity');

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
	 ? - unknown,
	 N/A - not applicable';
comment on column identity.dob IS
	'date/time of birth';
comment on column identity.cob IS
	'country of birth as per date of birth, coded as 2 character ISO code';
comment on column identity.deceased IS
	'date when a person has died (if so), format yyyymmdd';

-- ==========================================================
create table lnk_person2id (
	pk serial primary key,
	fk_identity_pk integer not null references identity(id),
	external_id text not null,
	description text,
	unique (fk_identity_pk, external_id, description)
) inherits (audit_fields);

select add_table_for_audit('lnk_person2id');

comment on table lnk_person2id is
	'link external IDs to GnuMed identities';
comment on column lnk_person2id.external_id is
	'textual representation of external ID which
	 may be Social Security Number, patient ID of
	 another EMR system, you-name-it';
comment on column lnk_person2id.description is
	'description of ID, e.g. name, originating system,
	 scope, expiration, etc.';

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
create table lnk_person2address (
	id serial primary key,
	id_identity integer references identity,
	id_address integer references address,
	id_type int references address_type default 1,
	address_source varchar(30),
	unique(id_identity, id_address),
	unique(id_identity, id_type)
);

COMMENT ON TABLE lnk_person2address IS
	'a many-to-many pivot table linking addresses to identities';
COMMENT ON COLUMN lnk_person2address.id_identity IS
	'identity to whom the address belongs';
COMMENT ON COLUMN lnk_person2address.id_address IS
	'address belonging to this identity';
COMMENT ON COLUMN lnk_person2address.id_type IS
	'type of this address (like home, work, parents, holidays ...)';

-- consider not plainly auditing this table but also
-- giving a reason for changes (incorrectly recorded
-- vs. moved etc.) or even explicitely model that
-- behaviour (as per Tim Churches)

-- ==========================================================
create table lnk_person2comm_channel (
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
) inherits (audit_fields);

select add_table_for_audit('relation_types');

comment on table relation_types IS
	'types of biological/social relationships between identities';
comment on column relation_types.biological IS
	'true if relationship is biological (proven or
	 reasonable assumption), else false';
comment on column relation_types.biol_verified IS
	'ONLY true if there is genetic proof for this relationship';
comment on column relation_types.description IS
	'plain text description of relationship';

-- ==========================================================
create table lnk_person2relative (
	id serial primary key,
	id_identity integer not null references identity,
	id_relative integer not null references identity,
	id_relation_type integer not null references relation_types,
	started date default NULL,
	ended date default NULL
) inherits (audit_fields);

select add_table_for_audit('lnk_person2relative');

comment on table lnk_person2relative IS
	'biological and social relationships between an identity and other identities';
comment on column lnk_person2relative.id_identity IS
	'primary identity to whom the relationship applies';
comment on column lnk_person2relative.id_relative IS
	'referred identity of this relationship (e.g. "child"
	if id_identity points to the father and id_relation_type
	points to "parent")';
comment on column lnk_person2relative.started IS
	'date when this relationship began';
comment on column lnk_person2relative.ended IS
	'date when this relationship ended, biological
	 relationships do not end !';

-- ==========================================================
create table occupation (
	id serial primary key,
	name text
) inherits (audit_fields);

select add_table_for_audit('occupation');

comment on table occupation is
	'collects occupation names';

-- ==========================================================
create table lnk_job2person (
	id serial primary key,
	id_identity integer not null references identity(id),
	id_occupation integer not null references occupation(id),
	comment text,
	unique (id_identity, id_occupation)
) inherits (audit_fields);

select add_table_for_audit('lnk_job2person');

comment on table lnk_job2person is
	'linking (possibly several) jobs to a person';
comment on column lnk_job2person.comment is
	'if you think you need non-unique id_identity/id_occupation
	 combinations, think again, you may be missing the point
	 of the comment field';

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
-- measurements will link to this, for example
create table org (
	id serial primary key,
	id_category integer not null references org_category(id),
	description text not null,
	unique(id_category, description)
);

-- ===================================================================
create table lnk_org2address (
	id serial primary key,
	id_org integer not null references org(id),
	id_address integer not null references org_address(id),
	unique (id_org, id_address)
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
	identity_id_seq,
	urb,
	country,
	street,
	address,
	address_type,
	state,
	enum_comm_types,
	comm_channel,
	mapbook,
	coordinate,
	address_info,
	lnk_person2address,
	lnk_person2comm_channel,
	relation_types,
	lnk_person2relative,
	occupation,
	lnk_job2person,
	org_address,
	org_category,
	org,
	lnk_org2address
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	names,
	names_id_seq,
	identity_id_seq,
	urb,
	urb_id_seq,
	country,
	street,
	street_id_seq,
	address,
	address_id_seq,
	comm_channel,
	comm_channel_id_seq,
	coordinate,
	coordinate_id_seq,
	address_info,
	address_info_id_seq,
	lnk_person2address,
	lnk_person2address_id_seq,
	lnk_person2comm_channel,
	lnk_person2comm_channel_id_seq,
	lnk_person2relative,
	lnk_person2relative_id_seq,	
	lnk_job2person,
	lnk_job2person_id_seq,
	org_address,
	org_address_id_seq,
	org,
	org_id_seq,
	lnk_org2address,
	lnk_org2address_id_seq
TO GROUP "_gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.sql,v $', '$Revision: 1.10 $');

-- ===================================================================
-- $Log: gmDemographics.sql,v $
-- Revision 1.10  2003-10-26 18:00:03  ncq
-- - add link table identity -> external IDs
--
-- Revision 1.9  2003/10/01 15:45:20  ncq
-- - use add_table_for_audit() instead of inheriting from audit_mark
--
-- Revision 1.8  2003/09/21 06:54:13  ihaywood
-- sane permissions
--
-- Revision 1.7  2003/09/21 06:10:06  ihaywood
-- sane permissions for gmDemographics
--
-- Revision 1.6  2003/08/17 00:23:22  ncq
-- - add occupation tables
-- - remove log_ tables, they are now auto-created
--
-- Revision 1.5  2003/08/13 21:08:51  ncq
-- - remove default "unknown" from urb.postcode
--
-- Revision 1.4  2003/08/10 01:03:39  ncq
-- - better name link tables (lnk_a2b pattern)
-- - urb.postcode constraint not null
--
-- Revision 1.3  2003/08/05 09:16:46  ncq
-- - cleanup
--
-- Revision 1.2  2003/08/02 13:17:05  ncq
-- - add audit tables
-- - cleanup
--
-- Revision 1.1  2003/08/01 22:31:31  ncq
-- - schema for service "demographics" (personalia)
--
