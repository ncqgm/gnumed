-- Project: GnuMed - cross-database foreign key descriptions
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCrossDB_FKs.sql,v $
-- $Revision: 1.9 $
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
-- remote foreign keys definition
-- -------------------------------------------------------------------
create table x_db_fk (
	id serial primary key,
	fk_src_schema name default null,
	fk_src_table name not null, -- references pg_class(relname),
	fk_src_col name not null, -- references pg_attribute(attname),
	ext_service text not null default 'default',
	ext_schema name default null,
	ext_table name not null,
	ext_col name not null,
	last_checked timestamp with time zone,
	-- should include fk_src_schema, too, but not now since
	-- schemata aren't used yet so the "default null" on
	-- fk_src_schema would always satisfy the unique constraint
	-- since null != null	
	unique (fk_src_table, fk_src_col)
);

comment on table x_db_fk is
	'describes cross-database (remote) foreign keys';
comment on column x_db_fk.fk_src_schema is
	'the schema holding the FK column, unused so far';
comment on column x_db_fk.fk_src_table is
	'the table holding the FK column';
comment on column x_db_fk.fk_src_col is
	'the actual FK column name';
comment on column x_db_fk.ext_service is
	'the service holding the column referenced by the FK,
	 remote database access parameters are derived from this';
comment on column x_db_fk.ext_schema is
	'the schema holding the column referenced by the FK, unused so far';
comment on column x_db_fk.ext_table is
	'the table holding the column referenced by the FK';
comment on column x_db_fk.ext_col is
	'the name of the column referenced by the FK';
comment on column x_db_fk.last_checked is
	'when was this constraint checked last ?
	 (used for efficiency)';

-- ===================================================================
\unset ON_ERROR_STOP
drop function add_x_db_fk_def (name, name, text, name, name);
\set ON_ERROR_STOP 1

create function add_x_db_fk_def (name, name, text, name, name) returns unknown as '
DECLARE
	src_table ALIAS FOR $1;
	src_col ALIAS FOR $2;
	ext_srvc ALIAS FOR $3;
	ext_tbl ALIAS FOR $4;
	ext_column ALIAS FOR $5;
	dummy RECORD;
BEGIN
	-- src table exists ?
	select relname into dummy from pg_class where relname = src_table;
	if not found then
		raise exception ''add_x_db_fk_def: Source table [%] does not exist.'', src_table;
		return false;
	end if;
	-- src column exists ?
	select pgc.relname into dummy from pg_class pgc, pg_attribute pga where
		pgc.relname = src_table
			and
		pga.attrelid = pgc.oid
			and
		pga.attname = src_col;
	if not found then
		-- FIXME: find out how to pass in table AND column
		raise exception ''add_x_db_fk_def: Source column [%] not found.'', src_col;
		return false;
	end if;
	-- add definition
	insert into x_db_fk (
		fk_src_table, fk_src_col, ext_service, ext_table, ext_col
	) values (
		src_table, src_col, ext_srvc, ext_tbl, ext_column
	);
	return true;
END;' language 'plpgsql';

comment on function add_x_db_fk_def (name, name, text, name, name) is
	'sanity-checking convenience function for defining cross-database foreign keys';

-- ===================================================================
-- detected violations
-- -------------------------------------------------------------------
create table x_db_fk_violation (
	id serial primary key,
	id_fk_def integer references x_db_fk(id),
	fk_table_pk text not null,
	fk_value text not null,
	description text,
	-- do not report the same violation (value) in
	-- the same row (fk_table_pk) of the same table
	-- (id_fk_def->fk_src_table) more than once
	unique (id_fk_def, fk_table_pk, fk_value)
);

comment on table x_db_fk_violation is
	'lists cross-database (remote) foreign key referential integrity violations';
comment on column x_db_fk_violation.id_fk_def is
	'the foreign key definition this violation report refers to';
comment on column x_db_fk_violation.fk_table_pk is
	'the primary key of the row in which the value of the
	 remote foreign key violates referential integrity,
	 casted to "text"';
comment on column x_db_fk_violation.fk_value is
	'the value of the remote foreign key violating
	 referential integrity, casted to "text"';
comment on column x_db_fk_violation.description is
	'per remote FK constraint def:
	 - referenced service not accessible
	 - referenced schema does not exist
	 - referenced table does not exist
	 - referenced column does not exist
	 per remote FK value:
	 - referenced value does not exist
	 - referenced value not unique';

-- =============================================
-- no grants needed since the only one using
-- these tables is gm-dbo, the owner of them
--GRANT SELECT ON
--TO GROUP "";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmCrossDB_FKs.sql,v $', '$Revision: 1.9 $', False);

-- =============================================
-- $Log: gmCrossDB_FKs.sql,v $
-- Revision 1.9  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.8  2005/01/12 14:47:48  ncq
-- - in DB speak the database owner is customarily called dbo, hence use that
--
-- Revision 1.7  2003/08/17 18:09:11  ncq
-- - factor out views
--
-- Revision 1.6  2003/08/10 00:58:47  ncq
-- - add stored procedure helper add_x_db_fk_def()
--
-- Revision 1.5  2003/08/03 14:41:01  ncq
-- - clear up column naming confusion in x_db_fk, adapt users
--
-- Revision 1.4  2003/07/27 21:56:17  ncq
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
