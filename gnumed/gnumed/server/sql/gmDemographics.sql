-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics.sql,v $
-- $Revision: 1.65 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create schema dem authorization "gm-dbo";

-- ===================================================================
-- location related tables
-- ===================================================================
-- no auditing neccessary, as this table only uses
-- original ISO data (= reference verifiable any time)
create table dem.country (
	id serial primary key,
	code char(2)
		unique
		not null,
	name text
		unique
		not null,
	deprecated date
		default null
);

-- ===================================================================
-- state codes: any need for more than 3 characters?
-- yes, in Germany we have up to 6
create table dem.state (
	id serial primary key,
	code text not null,
	country char(2) not null references dem.country(code),
	name text not null,
	unique (code, country)
) inherits (audit.audit_fields);

-- ===================================================================
-- FIXME: remodel according to XMeld
create table dem.urb (
	id serial primary key,
	id_state integer
		not null
		references dem.state(id)
		on update cascade
		on delete restrict,
	postcode text not null,
	lat_lon point,
	name text
		not null,
	unique (id_state, postcode, name)
) inherits (audit.audit_fields);

-- this does not work in the UK! Seperate postcodes for each street,
-- Same in Germany ! Postcodes can be valid for:
-- - several smaller urbs
-- - one urb
-- - several streets in one urb
-- - one street in one urb
-- - part of one street in one urb
-- Take that !  :-)

-- ===================================================================
create table dem.street (
	id serial primary key,
	id_urb integer
		not null
		references dem.urb(id)
		on update cascade
		on delete restrict,
	name text not null,
	postcode text,
	suburb text default null,
	lat_lon point,
	unique(id_urb, name, postcode)
) inherits (audit.audit_fields);

-- ===================================================================
create table dem.address (
	id serial primary key,
	id_street integer
		not null
		references dem.street(id)
		on update cascade
		on delete restrict,
	aux_street text default null,
	number text not null,
	subunit text default null,
	addendum text default null,
	lat_lon point default null,
	unique(id_street, aux_street, number, subunit, addendum)
) inherits (audit.audit_fields);

-- FIXME: should be unique(coalesce(field, '')) for aux_street, subunit, addendum !

-- ===================================================================
create table dem.address_type (
	id serial primary key,
	"name" text unique not null
);

-- ===================================================================
create table dem.marital_status (
	pk serial primary key,
	name text
		unique
		not null
);

-- ===================================================================
create table dem.enum_comm_types (
	id serial primary key,
	description text unique not null
);

-- ===================================================================
-- person related tables
-- ===================================================================
create table dem.gender_label (
	pk serial primary key,
	tag text
		not null
		unique
		check (tag in ('m', 'f', 'h', 'tm', 'tf')),
	label text
		unique
		not null,
	sort_weight integer
		not null,
	comment text
		not null
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'gender_label');

comment on table dem.gender_label is
	'This table stores the genders known to GNUmed.
	 FIXME: cross-check with CDA:administrative-gender-code';

-- ==========================================================
create table dem.identity (
	pk serial primary key,
	pupic char(24),
	gender text
		references dem.gender_label(tag)
		on update cascade
		on delete restrict,
	karyotype text
		default null,
	dob timestamp with time zone
		not null,
	fk_marital_status integer
		default null
		references dem.marital_status(pk),
	cob char(2),
	deceased timestamp with time zone
		default null
		check ((deceased is null) or (deceased >= dob)),
	title text
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'identity');

comment on table dem.identity IS
	'represents the unique identity of a person';
comment on column dem.identity.pupic IS
	'Portable Unique Person Identification Code as per gnumed white papers';
comment on column dem.identity.gender is
	'the gender code';
comment on column dem.identity.dob IS
	'date/time of birth';
comment on column dem.identity.cob IS
	'country of birth as per date of birth, coded as 2 character ISO code';
comment on column dem.identity.deceased IS
	'date when a person has died';
comment on column dem.identity.title IS
	'Yes, a title is an attribute of an identity, not of a name !
	 Also, there are some incredible rants of titles.';

-- ===================================================================
create table dem.enum_ext_id_types (
	pk serial primary key,
	name text,
	issuer text,
	context char default 'p' check (context in ('p', 'o', 'c', 's')),
	unique (name, issuer)
);

comment on table dem.enum_ext_id_types is
	'a list of all bureaucratic IDs/serial numbers/3rd party primary keys, etc.';
comment on column dem.enum_ext_id_types.issuer is
	'the authority/system issuing the number';
comment on column dem.enum_ext_id_types.context is
	'the context in which this number is used
		- p for ordinary persons
		- o for organisations
		- c for clinicians
		- s for staff in this clinic
	 FIXME: is context really a property of *type* ?';

-- ==========================================================
create table dem.lnk_identity2ext_id (
	id serial primary key,
	id_identity integer
		not null
		references dem.identity(pk)
		on update cascade
		on delete cascade,
	external_id text not null,
	fk_origin integer
		not null references dem.enum_ext_id_types(pk),
	comment text,
	unique (id_identity, external_id, fk_origin)
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'lnk_identity2ext_id');

comment on table dem.lnk_identity2ext_id is
	'link external IDs to GnuMed identities';
comment on column dem.lnk_identity2ext_id.external_id is
	'textual representation of external ID which
	 may be Social Security Number, patient ID of
	 another EMR system, you-name-it';
comment on column dem.lnk_identity2ext_id.fk_origin is
	'originating system';

-- ==========================================================
-- FIXME: rebuild according to OpenEHR and XMeld
create table dem.names (
	id serial primary key,
	id_identity integer
		not null
		references dem.identity(pk)
		on update cascade
		on delete cascade,
	active boolean default true,
	lastnames text not null,
	firstnames text not null,
	preferred text,
	comment text,
	unique(id_identity, lastnames, firstnames)
);

comment on table dem.names is
	'all the names an identity is known under;
	 As opposed to the versioning of all other tables, changed names
	 should not be moved into the audit trail tables. Search functionality
	 must be available at any time for all names a person ever had.';
comment on column dem.names.active IS
	'true if the name is still in use';
comment on column dem.names.firstnames IS
	'all first names of an identity in legal order,\n
	 IOW "minor" name, identifier of this identity within\n
	 the group defined by <lastnames>';
comment on column dem.names.lastnames IS
	'all last names of an identity in legal order,\n
	 IOW "major" name, "group identifier", eg. family, village, tribe, ...';
comment on column dem.names.preferred IS
	'preferred first name, the name a person is usually\n
	 called (nickname, warrior name)';
comment on column dem.names.comment is
	'a comment regarding this name, useful in things like "this was
	 the name before marriage" etc';

-- ==========================================================
create table dem.name_gender_map (
	id serial primary key,
	name text unique not null,
	gender character(1) check (gender in ('m', 'f'))
);

COMMENT on table dem.name_gender_map is
	'maps (first) names to their most frequently locally assigned gender,
	 this table is updated nightly by a cron script,
	 names whose gender distribution is between 70/30 and 30/70 are
	 ignored for ambiguity reasons,
	 names with "ambigous" gender are also ignored';


-- ==========================================================
create table dem.lnk_identity2comm (
	id serial primary key,
	id_identity integer
		not null
		references dem.identity(pk)
		on update cascade
		on delete cascade,
	id_address integer
		default null
		references dem.address(id)
		on update set null
		on delete set null,
	url text,
	id_type integer references dem.enum_comm_types,
	is_confidential bool not null default false,
	unique (id_identity, url)
);

-- rlee0001 <robeddielee@hotmail.com> writes:
-->> > example. For example:
-->> >       In: 123 456-7890
-->> >       Out: (123) 456-7890
-->> >       Stored As:
-->> >            PHONE = (Virtual Function, with Regexp input parser)
-->> >                AREA_CODE = 123
-->> >                PREFIX = 456
-->> >                SUFFIX = 7890
-->> > It would be interesting. Combine with item 9 above and you can make
-->> > "name" output in a structured format like "Last, First". Vb.Net's IDE
-->> > does this in the properties list for nested properties.
-->>
-->> So, create a type that does that. PostgreSQL is extensible. It's got
-->> data types for ISBNs, Internet addresses and even an XML document type.
-->> Compared to that a simple phone number field would be trivial.
-->
--> Actually I might try to have a go at it just for fun at home. Here at
--> work I just don't have the ability to create types (AFAIK).
--
--The trouble with the phone number idea is that the above doesn't match
--with any relevant standards.
--
--The one thing that *would* match a standard would be ITU-T
--Recommendation E.164: "The International Public Telecommunication
--Numbering Plan", May 1997.
--
--2.5.  Telephone Numbers
--
--   Contact telephone number structure is derived from structures defined
--   in [E164a].  Telephone numbers described in this mapping are
--   character strings that MUST begin with a plus sign ("+", ASCII value
--   0x002B), followed by a country code defined in [E164b], followed by a
--   dot (".", ASCII value 0x002E), followed by a sequence of digits
--   representing the telephone number.  An optional "x" attribute is
--   provided to note telephone extension information.
--
--Thus, the structure would break the phone number into three pieces:
--
-- 1. Country code
-- 2. Telephone number
-- 3. Extension information (optional)
--
--My phone number, in EB164 form, looks like:
-- +01.4166734124
--
--What you seem to be after, here, would confine your telno formatting
--to telephone numbers for Canada and the United States, and would break
--any time people have a need to express telephone numbers outside those
--two countries.
--
--It would be quite interesting to add an EB164 type, as it could
--represent phone numbers considerably more compactly than is the case
--for plain strings.  The 20 digits permissible across 1. and 2. could
--be encoded in... 68 bits.
-- 
--output = ("cbbrowne" "@" "cbbrowne.com")
--http://www3.sympatico.ca/cbbrowne/nonrdbms.html
-- Yves Deville

-- ==========================================================
-- theoretically, the only information needed to establish any kind of
-- biological family tree would be information about parenthood.
-- However, sometimes social family trees are equally important and at
-- other times information about parenthood is not known or uncertain
-- and it is still useful to record whatever information we can gather.
-- Thus, we need a variety of relationship types

create table dem.relation_types (
	id serial primary key,
	inverse integer references dem.relation_types (id),
	biological boolean not null,
	biol_verified boolean default false,
	description text
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'relation_types');

comment on table dem.relation_types IS
	'types of biological/social relationships between identities';
comment on column dem.relation_types.biological IS
	'true if relationship is biological (proven or
	 reasonable assumption), else false';
comment on column dem.relation_types.biol_verified IS
	'ONLY true if there is genetic proof for this relationship';
comment on column dem.relation_types.description IS
	'plain text description of relationship';

-- ==========================================================
-- this is consistent with what Aldfaer uses for genealogical
-- data and is said to be plenty fast
-- FIXME: it might be useful to CLUSTER ON id_identity ?

create table dem.lnk_person2relative (
	id serial primary key,
	id_identity integer not null references dem.identity(pk),
	id_relative integer not null references dem.identity(pk),
	id_relation_type integer not null references dem.relation_types,
	started date default NULL,
	ended date default NULL
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'lnk_person2relative');

comment on table dem.lnk_person2relative IS
	'biological and social relationships between an identity and other identities';
comment on column dem.lnk_person2relative.id_identity IS
	'primary identity to whom the relationship applies';
comment on column dem.lnk_person2relative.id_relative IS
	'referred-to identity of this relationship (e.g. "child"
	 if id_identity points to the father and id_relation_type
	 points to "parent")';
comment on column dem.lnk_person2relative.started IS
	'date when this relationship began';
comment on column dem.lnk_person2relative.ended IS
	'date when this relationship ended, biological
	 relationships do not end !';

-- ==========================================================
create table dem.occupation (
	id serial
		primary key,
	name text
		not null
		check (trim(name) != '')
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'occupation');

comment on table dem.occupation is
	'collects occupation names';

-- ==========================================================
create table dem.lnk_job2person (
	id serial primary key,
	id_identity integer not null references dem.identity(pk),
	id_occupation integer not null references dem.occupation(id),
	comment text,
	unique (id_identity, id_occupation)
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'lnk_job2person');

comment on table dem.lnk_job2person is
	'linking (possibly several) jobs to a person';
comment on column dem.lnk_job2person.comment is
	'if you think you need non-unique id_identity/id_occupation
	 combinations, think again, you may be missing the point
	 of the comment field';
-- ==========================================================
create table dem.staff_role (
	pk serial primary key,
	name text unique not null,
	comment text
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'staff_role');

comment on table dem.staff_role is
	'work roles a staff member can have';

-- ==========================================================
create table dem.staff (
	pk serial primary key,
	-- should actually point to identity(PUPIC)
	fk_identity integer
		not null
		references dem.identity(pk)
		on update cascade
		on delete cascade,
	fk_role integer
		not null
		references dem.staff_role(pk)
		on update cascade
		on delete cascade,
	db_user name
		unique
		not null
		default CURRENT_USER,
	short_alias text unique not null,
	comment text,
	unique(fk_role, db_user)
	-- link to practice
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'staff');
--select add_x_db_fk_def('staff', 'db_user', 'personalia', 'pg_user', 'usename');

comment on table dem.staff is
	'one-to-one mapping of database user accounts
	 (db_user) to staff identities (fk_identity)';
comment on column dem.staff.short_alias is
	'a short signature unique to this staff member
	 to be used in the GUI, actually this is somewhat
	 redundant with ext_person_id...';

-- ==========================================================
create table dem.lnk_identity2primary_doc (
	pk serial primary key,
	fk_identity integer
		not null
		references dem.identity(pk)
		on update cascade
		on delete cascade,
	fk_primary_doc integer
		not null
		references dem.staff(pk)
		on update cascade
		on delete cascade,
	unique (fk_identity, fk_primary_doc)
);

select audit.add_table_for_audit('dem', 'lnk_identity2primary_doc');

-- ===================================================================
-- organisation related tables
-- ===================================================================

-- ===================================================================
create table dem.org_category (
	id serial primary key,
	description text unique not null
);

-- ===================================================================
-- measurements will link to this, for example
create table dem.org (
	id serial primary key,
	id_category integer not null references dem.org_category(id),
	description text not null,
	unique(id_category, description)
);

-- ====================================================================
create table dem.lnk_org2comm (
	id serial primary key,
	id_org integer not null
		references dem.org(id)
		on update cascade
		on delete cascade,
	url text,
	id_type integer references dem.enum_comm_types(id), 
	is_confidential bool not null default false,
	unique (id_org, url)
);

-- =====================================================================

create table dem.lnk_org2ext_id (
	id serial primary key,
	id_org integer not null references dem.org(id),
	external_id text not null,
	fk_origin integer not null references dem.enum_ext_id_types(pk),
	comment text,
	unique (id_org, external_id, fk_origin)
) inherits (audit.audit_fields);

-- ==========================================================
-- the table formerly known as lnk_person2address
-- homologous to data_links in Richard's schema
create table dem.lnk_person_org_address (
	id serial primary key,
	id_identity integer
		references dem.identity(pk),
	id_address integer
		references dem.address(id),
	id_type integer
		default 1
		references dem.address_type(id),
	address_source text,
	id_org integer
		references dem.org(id),
	unique(id_identity, id_address),
	unique(id_org, id_address)
--	, unique(id_identity, id_org, id_occupation)
);

COMMENT on table dem.lnk_person_org_address IS
	'a many-to-many pivot table describing the relationship
	 between an organisation, a person, their work address and
	 their occupation at that location.
	 For patients id_org is NULL';
COMMENT on column dem.lnk_person_org_address.id_identity IS
	'identity to which the address belongs';
COMMENT on column dem.lnk_person_org_address.id_address IS
	'address belonging to this identity (the branch of the organisation)';
COMMENT on column dem.lnk_person_org_address.id_type IS
	'type of this address (like home, work, parents, holidays ...)';

-- consider not plainly auditing this table but also
-- giving a reason for changes (incorrectly recorded
-- vs. moved etc.) or even explicitely model that
-- behaviour (as per Tim Churches)

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.sql,v $', '$Revision: 1.65 $');

-- ===================================================================
-- $Log: gmDemographics.sql,v $
-- Revision 1.65  2006-02-19 13:46:47  ncq
-- - factor out dynamic DDL
-- - disallow CR/LF/FF/VT in many single-line demographics fields
--
-- Revision 1.64  2006/01/23 22:10:57  ncq
-- - staff.sign -> .short_alias
--
-- Revision 1.63  2006/01/16 22:12:33  ncq
-- - add some info re proper phone number handling
--
-- Revision 1.62  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.61  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.60  2005/12/27 19:13:17  ncq
-- - add link table to audit system
--
-- Revision 1.59  2005/12/05 19:05:59  ncq
-- - clin_episode -> episode
--
-- Revision 1.58  2005/12/05 16:13:48  ncq
-- - comment out calls to add_x_db_*
--
-- Revision 1.57  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.56  2005/09/08 17:03:29  ncq
-- - add comment
--
-- Revision 1.55  2005/08/14 15:37:56  ncq
-- - comments
--
-- Revision 1.54  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.53  2005/06/09 21:09:45  ncq
-- - there is no sensible reason to make state.code varchar(10)
--   instead of text so put it back
--
-- Revision 1.52  2005/06/09 00:24:25  cfmoro
-- State code text -> varchar to avoid extra spaces when fetching
--
-- Revision 1.51  2005/05/27 16:16:41  ncq
-- - Carlos rightly points out that id_address must be nullable in lnk_identity2comm
--
-- Revision 1.50  2005/05/24 19:53:53  ncq
-- - prepare for allowing communications channels to be tied to addresses
--
-- Revision 1.49  2005/04/17 16:37:40  ncq
-- - some cleanup/tightened constraints
--
-- Revision 1.48  2005/04/14 17:45:21  ncq
-- - gender_label.sort_rank -> sort_weight
--
-- Revision 1.47  2005/04/14 16:56:33  ncq
-- - fixed faulty field name
--
-- Revision 1.46  2005/04/14 16:46:51  ncq
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
