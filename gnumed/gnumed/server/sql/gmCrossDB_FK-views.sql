-- Project: GnuMed - cross-database foreign key descriptions
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCrossDB_FK-views.sql,v $
-- $Revision: 1.4 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- remote foreign keys definition
-- -------------------------------------------------------------------
create or replace function add_x_db_fk_def (name, name, text, name, name) returns unknown as '
DECLARE
	src_table ALIAS FOR $1;
	src_col ALIAS FOR $2;
	ext_srvc ALIAS FOR $3;
	ext_tbl ALIAS FOR $4;
	ext_column ALIAS FOR $5;
	dummy RECORD;
	msg text;
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
		msg = ''add_x_db_fk_def: Source column ['' || src_col || ''] not found in source table ['' || src_table || ''].''
		raise exception msg;
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
\unset ON_ERROR_STOP
drop view v_x_db_fk_violation;
\set ON_ERROR_STOP 1

create view v_x_db_fk_violation as
	select
		viol.id,
		viol.id_fk_def,
		def.fk_src_schema as src_schema,
		def.fk_src_table as src_table,
		def.fk_src_col as src_col,
		def.ext_service,
		def.ext_schema,
		def.ext_table,
		def.ext_col,
		def.last_checked,
		viol.fk_table_pk as offending_pk,
		viol.fk_value as offending_val,
		viol.description
	from
		x_db_fk_violation viol,
		x_db_fk def
	where
		viol.id_fk_def = def.id
	order by
		def.ext_service,
		def.ext_schema,
		def.ext_table
	;

-- -------------------------------------------------------------------
create or replace function log_x_db_fk_violation (integer, text, text, text) returns unknown as '
DECLARE
	fk_def_id alias for $1;
	viol_pk alias for $2;
	viol_val alias for $3;
	viol_comment alias for $4;
	dummy RECORD;
BEGIN
	-- violation already reported ?
	select 1 into dummy
	from
		x_db_fk_violation viol
	where
		viol.id_fk_def = fk_def_id
			and
		viol.fk_table_pk = viol_pk
			and
		viol.fk_value = viol_val
	;
	-- no
	if not found then
		insert into x_db_fk_violation(id_fk_def, fk_table_pk, fk_value, description)
			values (fk_def_id, viol_pk, viol_val, viol_comment);
	end if;
	return true;
END;' language 'plpgsql';

-- =============================================
-- do simple schema revision tracking
--INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmCrossDB_FK-views.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: gmCrossDB_FK-views.sql,v $
-- Revision 1.4  2005-10-24 19:17:04  ncq
-- - use ... or replace ... on functions
--
-- Revision 1.3  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.2  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.1  2003/08/17 17:57:23  ncq
-- - break out x_db_fk views/functions
-- - add helper log_violation()
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
