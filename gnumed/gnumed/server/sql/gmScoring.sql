-- GnuMed phrasewheel scoring functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmScoring.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Karsten Hilbert

-- the one important limitation is, that we can only have one scoring
-- table per data table, this is due to our linking them by means of
-- the data table primary key

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table scored_tables (
	id serial primary key,
	schema name default null,
	table_name name unique not null
);

comment on table scored_tables is
	'All tables that are to be scored must be
	 recorded in this table. Scoring tables will
	 be generated automatically for all tables
	 recorded here.';

-- ===================================================================
\unset ON_ERROR_STOP
drop function add_table_for_scoring(name);
\set ON_ERROR_STOP 1

create function add_table_for_scoring(name) returns unknown as '
DECLARE
	tbl_name ALIAS FOR $1;
	dummy RECORD;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where relname = tbl_name;
	if not found then
		raise exception ''add_table_for_scoring: Table [%] does not exist.'', tbl_name;
		return false;
	end if;
	-- add definition
	insert into scored_tables (
		table_name
	) values (
		tbl_name
	);
	return true;
END;' language 'plpgsql';

comment on function add_table_for_scoring(name) is
	'sanity-checking convenience function for marking tables for scoring';

-- ===================================================================
create table scoring_fields (
	pk serial primary key,
	cookie text default null,
	"user" name not null default CURRENT_USER,
	score bigint not null default 0
);

comment on table scoring_fields is
	'this table holds all the fields needed for scoring';
comment on column scoring_fields.cookie is
	'an opaque value denoting the context of this score,
	 applications better know what to do with this value';
comment on COLUMN scoring_fields."user" is
	'which user this score applies to';
comment on COLUMN scoring_fields.score is
	'the score itself';

-- ===================================================================
-- FIXME: actually this should be done by giving "creator"
-- rights to the audit trigger functions
grant SELECT, UPDATE, INSERT, DELETE on
	"scoring_fields",
	"scoring_fields_pk_seq"
to group "gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmScoring.sql,v $', '$Revision: 1.3 $', False);

-- ===================================================================
-- $Log: gmScoring.sql,v $
-- Revision 1.3  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.2  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.1  2003/10/19 13:04:57  ncq
-- - scoring implementation
--
