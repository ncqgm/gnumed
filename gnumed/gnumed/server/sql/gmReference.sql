-- Project: GnuMed - service "Reference"
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference.sql,v $
-- $Revision: 1.2 $
-- license: GPL
-- author: Karsten Hilbert

-- these tables hold data that are "reference material" and naturally
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
) inherits (audit_fields, audit_mark);

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
create table link_table2src (
	id_ref_source integer not null references ref_source(id),
	data_table name unique not null references pg_class(relname)
);

comment on table link_table2src is
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
GRANT SELECT ON
	basic_unit,
	unit,
	ref_source
TO GROUP "gm-public";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmReference.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmReference.sql,v $
-- Revision 1.2  2003-08-10 01:01:59  ncq
-- - add constraints on basic_unit
--
-- Revision 1.1  2003/07/27 16:50:52  ncq
-- - first check-in
--
