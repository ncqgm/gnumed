-- Project: GnuMed - service "Reference"
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference.sql,v $
-- $Revision: 1.8 $
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
	source text unique not null
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
	fk_ref_source integer not null references ref_source(pk),
	data_table name unique not null
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
create table form_defs (
	pk serial primary key,
	name_short text not null,
	name_long text not null,
	revision text not null,
	template text,
	engine char default 'T' not null check (engine in ('T', 'L')),
	in_use boolean not null default true,
	electronic boolean not null default false,
	flags varchar (100) [],
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
	 - L: LaTeX';
comment on column form_defs.in_use is
	'whether this template is currently actively
	 used in a given practice';
comment on column form_defs.electronic is
	'True if the form is designed for electronic transmission, such as e-mail. 
Currently always false as we need appropriate middleware engines to do this (viz. HL7)';
comment on column form_defs.flags is
	'an array of flags (boolean options) for this form, which the GUI should display to the user
Currently not implemented';

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
	, form_defs
	, form_print_defs
TO GROUP "gm-public";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmReference.sql,v $', '$Revision: 1.8 $');

-- =============================================
-- $Log: gmReference.sql,v $
-- Revision 1.8  2004-04-06 04:19:04  ihaywood
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
