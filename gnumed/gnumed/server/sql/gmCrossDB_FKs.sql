-- Project: GnuMed - cross-database foreign key descriptions
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCrossDB_FKs.sql,v $
-- $Revision: 1.2 $
-- license: GPL
-- author: Karsten Hilbert

-- import this into any GnuMed database that has foreign keys
-- pointing to other databases

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
	last_checked timestamp with time zone not null default CURRENT_TIMESTAMP,
	-- should include fk_schema, too, but not now since
	-- schemata aren't used yet so the "default null" on
	-- fk_schema would always satisfy the unique constraint
	-- since null != null	
	unique (fk_table, fk_col),
	-- for src_schema, respectively
	unique (src_service, src_table, src_col)
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
	'the service holding the FK column, remote
	 database access parameters are derived from this';
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
	 -- this relies on the fact that we use
	 -- integers for all our primary keys
	pk_fk_table integer not null,
	-- value casted to text ...
	fk_value text not null,
	fk_schema name default null,
	fk_table name not null, -- references pg_class(relname),
	fk_col name not null, -- references pg_attribute(attname),
	src_service text not null default 'default',
	src_schema name default null,
	src_table name not null,
	src_col name not null,
	-- should include fk_schema, too, but not now since
	-- schemata aren't used yet so the "default null" on
	-- fk_schema would always satisfy the unique constraint
	-- since null != null	
	unique (pk_fk_table, fk_table, fk_col),
	-- for src_schema, respectively
	unique (src_service, src_table, src_col)
);

-- =============================================
-- no grants needed since the only one using
-- these tables is gm-dbowner, the owner of them
--GRANT SELECT ON
--	x_db_fk,
--	x_db_fk_violation
--TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmCrossDB_FKs.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmCrossDB_FKs.sql,v $
-- Revision 1.2  2003-07-26 23:59:03  ncq
-- - can't create trigger on pg_class, hence cannot reference as FK source
--
-- Revision 1.1  2003/07/26 23:52:40  ncq
-- - initial commit
-- - remote foreign keys
--
