-- Project: GnuMed - service "Reference"
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference.sql,v $
-- $Revision: 1.5 $
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
	id serial primary key,
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
	id_ref_source integer not null references ref_source(id),
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
	id serial primary key,
	name_short text unique not null,
	name_long text unique
);

COMMENT ON TABLE basic_unit IS
	'basic units are SI units, units derived from them and the Unity';

-- ====================================
create table unit (
	id serial primary key,
	id_basic_unit integer references basic_unit,
	name_short text not null,
	name_long text,
	factor float not null default 1.0,
	shift float not null default 0.0
);

COMMENT ON TABLE unit IS 
	'units as used in real life';
COMMENT ON column unit.id_basic_unit IS
	'what is the SI-Standard unit for this, e.g. for the unit mg it is kg';
COMMENT ON column unit.factor IS
	'what factor the value with this unit has to be multiplied with to get values in the basic_unit';
COMMENT ON column unit.shift IS
	'what has to be added (after multiplying by factor) to a value with this unit to get values in the basic_unit';

-- =============================================
create table test_norm (
	id serial primary key,
	id_ref_src integer not null references ref_source(id),
	data text not null,
	comment text,
	unique (id_ref_src, data)
);

comment on table test_norm is
	'each row defines one set of measurement reference data';
comment on column test_norm.id_ref_src is
	'source this reference data set was taken from';
comment on column test_norm.data is
	'the actual reference data in some format,
	 say, XML or like in a *.conf file';

-- =============================================
GRANT SELECT ON
	basic_unit,
	unit,
	ref_source
TO GROUP "gm-public";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmReference.sql,v $', '$Revision: 1.5 $');

-- =============================================
-- $Log: gmReference.sql,v $
-- Revision 1.5  2003-10-01 15:45:20  ncq
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
