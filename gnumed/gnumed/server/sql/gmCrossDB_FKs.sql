-- Project: GnuMed - cross-database foreign key descriptions
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCrossDB_FKs.sql,v $
-- $Revision: 1.4 $
-- license: GPL
-- author: Karsten Hilbert

-- import this into any GnuMed database that has foreign keys
-- pointing to other databases, IOW, nearly all of them :-)

-- a cron script checks those FKs and reports errors,
-- the service configuration is taken from the "default"
-- service as given in the config file

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- -------------------------------------------------------------------
create table x_db_fk (
	id serial primary key,
	fk_schema name default null,
	fk_table name not null, -- references pg_class(relname),
	fk_col name not null, -- references pg_attribute(attname),
	src_service text not null default 'default',
	src_schema name default null,
	src_table name not null,
	src_col name not null,
	last_checked timestamp with time zone,
	-- should include fk_schema, too, but not now since
	-- schemata aren't used yet so the "default null" on
	-- fk_schema would always satisfy the unique constraint
	-- since null != null	
	unique (fk_table, fk_col)
);

comment on table x_db_fk is
	'describes cross-database (remote) foreign keys';
comment on column x_db_fk.fk_schema is
	'the schema holding the FK column, unused so far';
comment on column x_db_fk.fk_table is
	'the table holding the FK column';
comment on column x_db_fk.fk_col is
	'the actual FK column name';
comment on column x_db_fk.src_service is
	'the service holding the column referenced by the FK,
	 remote database access parameters are derived from this';
comment on column x_db_fk.src_schema is
	'the schema holding the column referenced by the FK, unused so far';
comment on column x_db_fk.src_table is
	'the table holding the column referenced by the FK';
comment on column x_db_fk.src_col is
	'the name of the column referenced by the FK';
comment on column x_db_fk.last_checked is
	'when was this constraint checked last ?
	 (used for efficiency)';

-- ===================================================================
-- detected violations
-- -------------------------------------------------------------------
create table x_db_fk_violation (
	id serial primary key,
	id_fk integer references x_db_fk(id),
	 -- this relies on the fact that we use
	 -- integers for all our primary keys
	fk_table_pk integer not null,
	-- value casted to text ...
	fk_value text not null,
	-- do not report the same violation (value)
	-- in the same row (fk_table_pk) of the
	-- same table (id_fk) more than once
	unique (id_fk, fk_table_pk, fk_value)
);

comment on table x_db_fk_violation is
	'describes cross-database (remote) foreign keys';
comment on column x_db_fk_violation.id_fk is
	'the foreign key this violation report refers to';
comment on column x_db_fk_violation.fk_table_pk is
	'the primary key of the row in which the value
	 of the remote foreign key violates referential integrity';
comment on column x_db_fk_violation.fk_value is
	'the value of the remote foreign key violating
	 referential integrity, casted to "text"';

-- =============================================
-- no grants needed since the only one using
-- these tables is gm-dbowner, the owner of them
--GRANT SELECT ON
--TO GROUP "";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmCrossDB_FKs.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: gmCrossDB_FKs.sql,v $
-- Revision 1.4  2003-07-27 21:56:17  ncq
-- - adjust unique constraints
-- - don't default to CURRENT_TIMESTAMP in last_checked ! (it needs to be set explicitely)
-- - *reference* relevant remote-FKs from *_violations instead of cloning x_db_fk
--
-- Revision 1.3  2003/07/27 16:41:29  ncq
-- - add table for reporting violations
--
-- Revision 1.2  2003/07/26 23:59:03  ncq
-- - can't create trigger on pg_class, hence cannot reference as FK source
--
-- Revision 1.1  2003/07/26 23:52:40  ncq
-- - initial commit
-- - remote foreign keys
--
