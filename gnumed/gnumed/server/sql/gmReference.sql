-- Project: GnuMed - service "Reference"
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference.sql,v $
-- $Revision: 1.26 $
-- license: GPL
-- author: Karsten Hilbert

-- these tables hold data that are "reference material" and are naturally
-- used in several other services, eg: ICD10 will be referenced from
-- service "pharmaca" and from service "clinical" and maybe from service
-- "administrivia" (for, say, billing)

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- note: avoid One True Lookup Tables(tm): http://www.dbazine.com/ofinterest/oi-articles/celko22

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
) inherits (audit.audit_fields);

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

-- ===================================================================
-- measurement units
-- -------------------------------------------------------------------
CREATE TABLE basic_unit (
	pk serial primary key,
	name_short text unique not null,
	name_long text unique
);

-- ====================================
create table unit (
	pk serial primary key,
	fk_basic_unit integer references basic_unit(pk),
	name_short text not null,
	name_long text,
	factor float not null default 1.0,
	shift float not null default 0.0
);

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
) inherits (audit.audit_fields);

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
) inherits (audit.audit_fields);

-- =============================================
create table test_norm (
	pk serial primary key,
	fk_ref_src integer not null references ref_source(pk),
	data text not null,
	comment text,
	unique (fk_ref_src, data)
);

-- =============================================
create table papersizes (
	pk serial primary key,
	name text unique not null,
	size point not null
);

-- =============================================
-- form templates

create table form_types (
	name text unique,
	pk serial primary key
);

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
	is_user boolean
		not null
		default true,
	unique (name_short, name_long),
	unique (name_long, revision)
) inherits (audit.audit_fields);

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

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmReference.sql,v $', '$Revision: 1.26 $');

-- =============================================
-- $Log: gmReference.sql,v $
-- Revision 1.26  2006-06-28 14:13:05  ncq
-- - add comment on the One True Lookup Table trap
--
-- Revision 1.25  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.24  2005/11/13 17:38:40  ncq
-- - factor out dynamic DDL
--
-- Revision 1.23  2005/11/11 23:05:08  ncq
-- - add is_user to form_defs
--
-- Revision 1.22  2005/09/19 16:38:51  ncq
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
