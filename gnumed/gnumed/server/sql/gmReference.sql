-- Project: GnuMed - service "Reference"
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference.sql,v $
-- $Revision: 1.22 $
-- license: GPL
-- author: Karsten Hilbert

-- these tables hold data that are "reference material" and are naturally
-- used in several other services, eg: ICD10 will be referenced from
-- service "pharmaca" and from service "clinical" and maybe from service
-- "administrivia" (for, say, billing)

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- reference sources and pivot table linking sources to data tables
-- -------------------------------------------------------------------
-- we need to audit this table so we can trace back removed references
create table ref_source (
	pk serial primary key,
	name_short text unique not null,
	name_long text unique default null,
	version text not null,
	description text,
	source text unique not null,
	unique(name_short, version)
) inherits (audit_fields);

select add_table_for_audit('ref_source');

comment on table ref_source is
	'lists the available coding systems, classifications, ontologies and term lists';
comment on column ref_source.name_short is
	'shorthand for referrring to this reference entry';
comment on column ref_source.name_long is
	'long, complete (, ?official) name for this reference entry';
comment on column ref_source.version is
	'the exact and non-ambigous version for this entry';
comment on column ref_source.description is
	'optional arbitrary description';
comment on column ref_source.source is
	'non-ambigous description of source; with this info in hand
	 it must be possible to locate a copy of the external reference';

-- ====================================
create table lnk_tbl2src (
	fk_ref_source integer
		not null
		references ref_source(pk)
		on update cascade
		on delete cascade,
	data_table name
		unique
		not null
);

-- workaround since we cannot add trigger on
-- pg_class directly (and hence not point to
-- it with a foreign key constraint)
select add_x_db_fk_def ('lnk_tbl2src', 'data_table', 'reference', 'pg_class', 'relname');

comment on table lnk_tbl2src is
	'This table links data tables to sources. Source entries may
	 appear more than once (because they describe several tables)
	 but table names must be unique in here. Note, however, that
	 this table only links those data tables to their sources in
	 which all rows have the very same source (such as ICD10).
	 Tables where each row has its own source (say, literature
	 references on diseases etc) will have a column constrained
	 by a foreign key into ref_source directly.';

-- ===================================================================
-- measurement units
-- -------------------------------------------------------------------
CREATE TABLE basic_unit (
	pk serial primary key,
	name_short text unique not null,
	name_long text unique
);

COMMENT ON TABLE basic_unit IS
	'basic units are SI units, units derived from them and the Unity';

-- ====================================
create table unit (
	pk serial primary key,
	fk_basic_unit integer references basic_unit(pk),
	name_short text not null,
	name_long text,
	factor float not null default 1.0,
	shift float not null default 0.0
);

COMMENT ON TABLE unit IS 
	'units as used in real life';
COMMENT ON column unit.fk_basic_unit IS
	'what is the SI-Standard unit for this, e.g. for the unit mg it is kg';
COMMENT ON column unit.factor IS
	'what factor the value with this unit has to be multiplied with to get values in the basic_unit';
COMMENT ON column unit.shift IS
	'what has to be added (after multiplying by factor) to a value with this unit to get values in the basic_unit';

-- ===================================================================
-- ATC classification
-- -------------------------------------------------------------------
create table atc_group (
	pk serial primary key,
	code text
		unique
		not null,
	description text
		unique
		not null
) inherits (audit_fields);

select add_table_for_audit('atc_group');


create table atc_substance (
	pk serial primary key,
	code text
		unique
		not null,
	name text
		unique
		not null,
	ddd_amount numeric,
	fk_ddd_unit integer
		references unit(pk)
		on update cascade
		on delete restrict,
	route text,
	comment text
) inherits (audit_fields);

select add_table_for_audit('atc_substance');

-- =============================================
create table test_norm (
	pk serial primary key,
	fk_ref_src integer not null references ref_source(pk),
	data text not null,
	comment text,
	unique (fk_ref_src, data)
);

comment on table test_norm is
	'each row defines one set of measurement reference data';
comment on column test_norm.fk_ref_src is
	'source this reference data set was taken from';
comment on column test_norm.data is
	'the actual reference data in some format,
	 say, XML or like in a *.conf file';

-- =============================================
create table papersizes (
	pk serial primary key,
	name text unique not null,
	size point not null
);

comment on column papersizes.size is '(cm, cm)';

-- =============================================
-- form templates

create table form_types (
	name text unique,
	pk serial primary key
);

comment on table form_types is
	'types of forms which are available,
	 generally by purpose (radiology, pathology, sick leave, etc.)';

-- =============================================
create table form_defs (
	pk serial primary key,
	fk_type integer references form_types(pk),
	country text,
	locale text,
	soap_cat text
		not null
		default 'p'
		check(lower(soap_cat) in ('s', 'o', 'a', 'p')),
	name_short text not null,
	name_long text not null,
	revision text not null,
	template text,
	engine char default 'T' not null check (engine in ('T', 'L', 'H')),
	in_use boolean not null default true,
	url text,
	unique (name_short, name_long),
	unique (name_long, revision)
) inherits (audit_fields);

select add_table_for_audit('form_defs');

comment on table form_defs is
	'form definitions';
comment on column form_defs.name_short is
	'a short name for use in a GUI or some such';
comment on column form_defs.name_long is
	'a long name unambigously describing the form';
comment on column form_defs.revision is
	'GnuMed internal form def version, may
	 occur if we rolled out a faulty form def';
comment on column form_defs.template is
	'the template complete with placeholders in
	 the format accepted by the engine defined in
	 form_defs.engine';
comment on column form_defs.engine is
	'the business layer forms engine used
	 to process this form, currently:
	 - T: plain text
	 - L: LaTeX
	 - H: Health Layer 7';
comment on column form_defs.in_use is
	'whether this template is currently actively
	 used in a given practice';
comment on column form_defs.url is
	'For electronic forms which are always sent to the same 
	url (such as reports to a statutory public-health surveilliance 
	authority)';

-- =============================================
create table form_field_types (
	name text unique,
	pk serial primary key
);

-- ===================================================
create table form_fields (
	pk serial primary key,
	fk_form integer
		not null
		references form_defs(pk),
	long_name text not null,
	template_placeholder text not null,
	help text,
	fk_type integer not null references form_field_types(pk),
	param text,
	display_order integer,
	unique (fk_form, long_name),
	unique (fk_form, template_placeholder)
);

comment on table form_fields is
	'List of fields for a particular form';
comment on column form_fields.long_name is
	'The full name of the form field as presented to the user';
comment on column form_fields.template_placeholder is
	'The name of the field as exposed to the form template.
	 In other words, the placeholder in form_defs.template where
	 the value entered into this field ist to be substituted.
	 Must be a valid identifier in the form template''s
	 script language (viz. Python)';
comment on column form_fields.help is
	'longer help text';
comment on column form_fields.fk_type is
	'the field type';
comment on column form_fields.param is
	'a parameter for the field''s behaviour, meaning is type-dependent';
comment on column form_fields.display_order is
	'used to *suggest* display order, but client may ignore';

-- ===================================================
create table form_print_defs (
	pk serial primary key,
	fk_form integer
		unique
		not null
		references form_defs(pk),
	fk_papersize integer
		not null
		references papersizes(pk),
	offset_top integer not null default 0,
	offset_left integer not null default 0,
	pages integer not null default 1,
	printer text not null,
	tray text not null,
	manual_feed bool not null default false,
	papertype text not null,
	eject_direction character(1) not null,
	orientation character(1) not null
);

comment on column form_print_defs.offset_top is
	'in mm - and yes, they do change even within one
	 type of form, but we do not want to change the
	 offset for all the fields in that case';
comment on column form_print_defs.papertype is
	'type of paper such as "watermarked rose",
	 mainly for user interaction on manual_feed==true';

-- =============================================
GRANT SELECT ON
	ref_source
	, lnk_tbl2src
	, unit
	, basic_unit
	, test_norm
	, papersizes
	, form_types
	, form_defs
	, form_print_defs
TO GROUP "gm-public";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmReference.sql,v $', '$Revision: 1.22 $');

-- =============================================
-- $Log: gmReference.sql,v $
-- Revision 1.22  2005-09-19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.21  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.20  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.19  2005/02/21 18:48:23  ncq
-- - added default to form_defs.soap_cat
--
-- Revision 1.18  2005/02/21 18:34:42  ncq
-- - add soap_cat to form_defs
--
-- Revision 1.17  2005/01/29 18:38:08  ncq
-- - silly cleanup
--
-- Revision 1.16  2005/01/27 17:24:50  ncq
-- - form_fields.internal_name -> template_placeholder
--
-- Revision 1.15  2005/01/24 17:57:43  ncq
-- - cleanup
-- - Ian's enhancements to address and forms tables
--
-- Revision 1.14  2004/12/18 09:55:24  ncq
-- - cleanup
--
-- Revision 1.13  2004/12/15 12:14:08  ihaywood
-- couple of extra fields and comments
--
-- Revision 1.12  2004/06/26 23:43:51  ncq
-- - added unique() in ref_source
-- - atc_* tables
--
-- Revision 1.11  2004/06/23 21:11:27  ncq
-- - whitespace fix
--
-- Revision 1.10  2004/06/17 11:32:08  ihaywood
-- bugfixes
--
-- Revision 1.9  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.8  2004/04/06 04:19:04  ihaywood
-- form templates for australia
--
-- Revision 1.7  2004/03/09 09:31:41  ncq
-- - merged most form def tables into reference service schema
--
-- Revision 1.6  2003/12/29 15:41:59  uid66147
-- - fk/pk naming cleanup
--
-- Revision 1.5  2003/10/01 15:45:20  ncq
-- - use add_table_for_audit() instead of inheriting from audit_mark
--
-- Revision 1.4  2003/08/17 00:25:38  ncq
-- - remove log_ tables, they are now auto-created
--
-- Revision 1.3  2003/08/13 21:12:24  ncq
-- - auditing tables
-- - add test_norm table
--
-- Revision 1.2  2003/08/10 01:01:59  ncq
-- - add constraints on basic_unit
--
-- Revision 1.1  2003/07/27 16:50:52  ncq
-- - first check-in
--
