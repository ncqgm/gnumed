-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics.sql,v $
-- $Revision: 1.46 $
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
	id_state integer
		not null
		references state(id)
		on update cascade
		on delete restrict,
	postcode text not null,
	lat_lon point,
	name text
		not null,
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
	'cities, towns, dwellings ..., eg. "official" places of residence';
COMMENT ON COLUMN urb.id_state IS
	'reference to information about country and state';
COMMENT ON COLUMN urb.postcode IS
	'default postcode for urb.name,
	 useful for all the smaller urbs that only have one postcode,
	 also useful as a default when adding new streets to an urb';
COMMENT ON COLUMN urb.name IS
	'the name of the city/town/dwelling';
COMMENT ON COLUMN urb.lat_lon is
	'the location of the urb, as lat/long co-ordinates. Ideally this would be NOT NULL';
-- ===================================================================
create table street (
	id serial primary key,
	id_urb integer
		not null
		references urb(id)
		on update cascade
		on delete restrict,
	name text not null,
	postcode text,
	suburb text default null,
	lat_lon point,
	unique(id_urb, name, postcode)
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
comment on column street.suburb is
	'the suburb this street is in (if any)';
comment on column street.lat_lon is
'the approximate location of the street, as lat/long co-ordinates';
-- ===================================================================
create table address (
	id serial primary key,
	id_street integer
		not null
		references street(id)
		on update cascade
		on delete restrict,
	aux_street text default null,
	number text not null,
	subunit text default null,
	addendum text default null,
	lat_lon point default null,
	unique(id_street, aux_street, number, subunit, addendum)
) inherits (audit_fields);

-- FIXME: should be unique(coalesce(field, '')) for aux_street, subunit, addendum !

select add_table_for_audit('address');

comment on table address is
	'an address aka a location, void of attached meaning such as type of address';
comment on column address.id_street is
	'the street this address is at from
	 whence the urb is to be found, it
	 thus indirectly references urb(id)';
comment on column address.aux_street is
	'additional street-level information which
	 formatters would usually put on lines directly
	 below the street line of an address, such as
	 postal box directions in CA';
comment on column address.number is
	'number of the house';
comment on column address.subunit is
	'directions *below* the unit (eg.number) level,
	 such as appartment number, room number, level,
	 entrance or even verbal directions';
comment on column address.addendum is
	'any additional information that
	 did not fit anywhere else';
comment on column address.lat_lon is
	'the exact location of this address in latitude-longtitude';

-- ===================================================================
create table address_type (
	id serial primary key,
	"name" text unique not null
);


-- ===================================================================
create table marital_status (
	pk serial primary key,
	name text
		unique
		not null
);
-- ===================================================================
create table enum_comm_types (
	id serial primary key,
	description text unique not null
);

-- ===================================================================
-- person related tables
-- ===================================================================
create table gender_label (
	pk serial primary key,
	tag text
		not null
		unique
		check (gender in ('m', 'f', 'h', 'tm', 'tf')),
	label text
		unique
		not null,
	sort_rank integer
		not null,
	comment text
		not null
) inherits (audit_fields);

select add_table_for_audit('gender_label');

comment on table gender_label is
	'This table stores the genders known to GNUmed.
	 FIXME: cross-check with CDA:administrative-gender-code';

-- ==========================================================
create table identity (
	pk serial primary key,
	pupic char(24),
	gender text
		references gender_label(tag)
		on update cascade
		on delete restrict,
	karyotype text
		default null,
	dob timestamp with time zone
		not null,
	fk_marital_status integer
		default null
		references marital_status(pk),
	cob char(2),
	deceased timestamp with time zone
		default null
		check ((deceased is null) or (deceased >= dob)),
	title text
) inherits (audit_fields);

select add_table_for_audit('identity');

comment on table identity IS
	'represents the unique identity of a person';
comment on column identity.pupic IS
	'Portable Unique Person Identification Code as per gnumed white papers';
comment on column identity.gender is
	'the gender code';
comment on column identity.dob IS
	'date/time of birth';
comment on column identity.cob IS
	'country of birth as per date of birth, coded as 2 character ISO code';
comment on column identity.deceased IS
	'date when a person has died';
comment on column identity.title IS
	'Yes, a title is an attribute of an identity, not of a name !
	 Also, there are some incredible rants of titles.';

-- ===================================================================
create table enum_ext_id_types (
	pk serial primary key,
	name text,
	issuer text,
	context char default 'p' check (context in ('p', 'o', 'c', 's')),
	unique (name, issuer)
);

comment on table enum_ext_id_types is
	'a list of all bureaucratic IDs/serial numbers/3rd party primary keys, etc.';
comment on column enum_ext_id_types.issuer is
	'the authority/system issuing the number';
comment on column enum_ext_id_types.context is
	'the context in which this number is used
		- p for ordinary persons
		- o for organisations
		- c for clinicians
		- s for staff in this clinic
	 FIXME: is context really a property of *type* ?';

-- ==========================================================
create table lnk_identity2ext_id (
	id serial primary key,
	id_identity integer
		not null
		references identity(pk)
		on update cascade
		on delete cascade,
	external_id text not null,
	fk_origin integer
		not null references
		enum_ext_id_types(pk),
	comment text,
	unique (id_identity, external_id, fk_origin)
) inherits (audit_fields);

select add_table_for_audit('lnk_identity2ext_id');

comment on table lnk_identity2ext_id is
	'link external IDs to GnuMed identities';
comment on column lnk_identity2ext_id.external_id is
	'textual representation of external ID which
	 may be Social Security Number, patient ID of
	 another EMR system, you-name-it';
comment on column lnk_identity2ext_id.fk_origin is
	'originating system';

-- ==========================================================
create table names (
	id serial primary key,
	id_identity integer
		references identity(pk)
		on update cascade
		on delete cascade,
	active boolean default true,
	lastnames text not null,
	firstnames text not null,
	preferred text,
	comment text,
	unique(id_identity, lastnames, firstnames)
);

comment on table names is
	'all the names an identity is known under;
	 As opposed to the versioning of all other tables, changed names
	 should not be moved into the audit trail tables. Search functionality
	 must be available at any time for all names a person ever had.';
comment on column names.active IS
	'true if the name is still in use';
comment on column names.firstnames IS
	'all first names of an identity in legal order,\n
	 IOW "minor" name, identifier of this identity within\n
	 the group defined by <lastnames>';
comment on column names.lastnames IS
	'all last names of an identity in legal order,\n
	 IOW "major" name, "group identifier", eg. family, village, tribe, ...';
comment on column names.preferred IS
	'preferred first name, the name a person is usually\n
	 called (nickname, warrior name)';
comment on column names.comment is
	'a comment regarding this name, useful in things like "this was
	 the name before marriage" etc';

-- ==========================================================
create table name_gender_map (
	id serial primary key,
	name text unique not null,
	gender character(1) check (gender in ('m', 'f'))
);

COMMENT on table name_gender_map is
	'maps (first) names to their most frequently locally assigned gender,
	 this table is updated nightly by a cron script,
	 names whose gender distribution is between 70/30 and 30/70 are
	 ignored for ambiguity reasons,
	 names with "ambigous" gender are also ignored';


-- ==========================================================
create table lnk_identity2comm (
	id serial primary key,
	id_identity integer not null
		references identity(pk)
		on update cascade
		on delete cascade,
	url text,
	id_type integer references enum_comm_types,
	is_confidential bool not null default false,
	unique (id_identity, url)
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
	inverse integer references relation_types (id),
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
-- this is consistent with what Aldfaer uses for genealogical
-- data and is said to be plenty fast
-- FIXME: it might be useful to CLUSTER ON id_identity ?

create table lnk_person2relative (
	id serial primary key,
	id_identity integer not null references identity(pk),
	id_relative integer not null references identity(pk),
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
	'referred-to identity of this relationship (e.g. "child"
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
	id_identity integer not null references identity(pk),
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
-- ==========================================================
create table staff_role (
	pk serial primary key,
	name text unique not null,
	comment text
) inherits (audit_fields);

select add_table_for_audit('staff_role');

comment on table staff_role is
	'work roles a staff member can have';

-- ==========================================================
create table staff (
	pk serial primary key,
	-- should actually point to identity(PUPIC)
	fk_identity integer
		not null
		references identity(pk)
		on update cascade
		on delete cascade,
	fk_role integer
		not null
		references staff_role(pk)
		on update cascade
		on delete cascade,
	db_user name
		unique
		not null
		default CURRENT_USER,
	sign text unique not null,
	comment text,
	unique(fk_role, db_user)
	-- link to practice
) inherits (audit_fields);

select add_table_for_audit('staff');
select add_x_db_fk_def('staff', 'db_user', 'personalia', 'pg_user', 'usename');

comment on table staff is
	'one-to-one mapping of database user accounts
	 (db_user) to staff identities (fk_identity)';
comment on column staff.sign is
	'a short signature unique to this staff member
	 to be used in the GUI, actually this is somewhat
	 redundant with ext_person_id...';

-- ===================================================================
-- organisation related tables
-- ===================================================================

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

-- ====================================================================
create table lnk_org2comm (
	id serial primary key,
	id_org integer not null
		references org(id)
		on update cascade
		on delete cascade,
	url text,
	id_type integer references enum_comm_types(id), 
	is_confidential bool not null default false,
	unique (id_org, url)
);

-- =====================================================================

create table lnk_org2ext_id (
	id serial primary key,
	id_org integer not null references org(id),
	external_id text not null,
	fk_origin integer not null references enum_ext_id_types(pk),
	comment text,
	unique (id_org, external_id, fk_origin)
) inherits (audit_fields);

-- ==========================================================
-- the table formerly known as lnk_person2address
-- homologous to data_links in Richard's schema
create table lnk_person_org_address (
	id serial primary key,
	id_identity integer
		references identity(pk),
	id_address integer
		references address(id),
	id_type integer
		default 1
		references address_type(id),
	address_source text,
	id_org integer
		references org(id),
	unique(id_identity, id_address),
	unique(id_org, id_address)
--	, unique(id_identity, id_org, id_occupation)
);

COMMENT ON TABLE lnk_person_org_address IS
	'a many-to-many pivot table describing the relationship
	 between an organisation, a person, their work address and
	 their occupation at that location.
	 For patients id_org is NULL';
COMMENT ON COLUMN lnk_person_org_address.id_identity IS
	'identity to which the address belongs';
COMMENT ON COLUMN lnk_person_org_address.id_address IS
	'address belonging to this identity (the branch of the organisation)';
COMMENT ON COLUMN lnk_person_org_address.id_type IS
	'type of this address (like home, work, parents, holidays ...)';

-- consider not plainly auditing this table but also
-- giving a reason for changes (incorrectly recorded
-- vs. moved etc.) or even explicitely model that
-- behaviour (as per Tim Churches)

-- ===================================================================
-- do simple schema revision tracking
--INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.sql,v $', '$Revision: 1.46 $');

-- ===================================================================
-- $Log: gmDemographics.sql,v $
-- Revision 1.46  2005-04-14 16:46:51  ncq
-- - name_gender_map moved here from DE specific section
--
-- Revision 1.45  2005/03/31 17:48:41  ncq
-- - missing on update/delete clauses on FKs
--
-- Revision 1.44  2005/03/14 14:40:35  ncq
-- - improved comments on name fields
--
-- Revision 1.43  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.42  2005/02/13 14:42:47  ncq
-- - add names.comment
--
-- Revision 1.41  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.40  2005/01/24 17:57:43  ncq
-- - cleanup
-- - Ian's enhancements to address and forms tables
--
-- Revision 1.39  2004/12/21 09:59:40  ncq
-- - comm_channel -> comm else too long on server < 7.3
--
-- Revision 1.38  2004/12/20 19:04:37  ncq
-- - fixes by Ian while overhauling the demographics API
--
-- Revision 1.37  2004/12/15 09:33:16  ncq
-- - improve marital_status handling
--
-- Revision 1.36  2004/11/28 14:30:55  ncq
-- - make delete/update on identity cascade to names table
--
-- Revision 1.35  2004/09/17 20:16:35  ncq
-- - cleanup, improve comments
-- - tighten identity constraints
--
-- Revision 1.34  2004/09/10 10:57:02  ncq
-- - re discussion with Jim et al on urb/suburb/address problem
--   in CA/AU/DE added aux_street/subunit to address, see inline
--   docs for explanations
--
-- Revision 1.33  2004/09/02 00:44:43  ncq
-- - move suburb field from address to street
-- - improve comments
-- - add on update/cascade clauses
--
-- Revision 1.32  2004/08/18 08:28:14  ncq
-- - improve comments on Knot system
--
-- Revision 1.31  2004/07/22 02:23:58  ihaywood
-- Jim's new comments for comm_channel
--
-- Revision 1.30  2004/05/30 21:01:11  ncq
-- - cleanup
--
-- Revision 1.29  2004/04/07 18:42:10  ncq
-- - *comm_channel -> *comm_chan
--
-- Revision 1.28  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.27  2004/03/27 18:36:28  ncq
-- - cleanup, added FSME vaccine
--
-- Revision 1.26  2004/03/27 04:37:01  ihaywood
-- lnk_person2address now lnk_person_org_address
-- sundry bugfixes
--
-- Revision 1.25  2004/03/09 09:10:50  ncq
-- - removed N/A gender
--
-- Revision 1.24  2004/03/04 10:40:29  ncq
-- - cleanup, comments, renamed id->pk, origin -> fk_origin
--
-- Revision 1.23  2004/03/03 23:51:41  ihaywood
-- external ID tables harmonised
--
-- Revision 1.22  2004/03/02 10:22:30  ihaywood
-- support for martial status and occupations
-- .conf files now use host autoprobing
--
-- Revision 1.21  2004/02/27 07:05:30  ihaywood
-- org_address is dead. Doesn't make
-- sense for orgs to have multiple addresses IMHO
-- as we allow branch organisations
--
-- Revision 1.20  2004/02/18 14:18:51  ncq
-- - since we dare let org_address inherit from address
--   there's no org_address_id_seq to be granted rights on
--
-- Revision 1.19  2004/02/18 06:37:47  ihaywood
-- extra organisation table to represent comm channels
--
-- Revision 1.18  2003/12/29 15:36:50  uid66147
-- - add staff tables
--
-- Revision 1.17  2003/12/01 22:12:41  ncq
-- - lnk_person2id -> lnk_person_ext_id
--
-- Revision 1.16  2003/11/23 23:34:49  ncq
-- - names.title -> identity.title
--
-- Revision 1.15  2003/11/22 14:55:15  ncq
-- - default names.active to false, thereby fixing various side effects
--
-- Revision 1.14  2003/11/20 02:08:20  ncq
-- - we decided to drop N/A from identity.gender, hence make it varchar(2) again
--
-- Revision 1.13  2003/11/20 00:38:43  ncq
-- - if we want to allow "N/A" in identity.gender we better make it
--   varchar(3) not (2) :-)       found by Syan
--
-- Revision 1.12  2003/11/02 10:17:02  ihaywood
-- fixups that crash psql.py
--
-- Revision 1.11  2003/10/31 23:29:38  ncq
-- - cleanup, id_ -> fk_
--
-- Revision 1.10  2003/10/26 18:00:03  ncq
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
