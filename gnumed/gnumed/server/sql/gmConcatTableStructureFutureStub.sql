-- =============================================
-- project: GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConcatTableStructureFutureStub.sql,v $
-- $Id: gmConcatTableStructureFutureStub.sql,v 1.1 2007-05-07 16:21:51 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- this is needed to allow a post 0.2.6 bootstrapper
-- to bootstrap databases starting from v2, it needs to
-- be imported by all versions up to and including v5

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop schema gm cascade;
\set ON_ERROR_STOP 1

create schema gm authorization "gm-dbo";

-- ---------------------------------------------
create or replace function gm.concat_table_structure(integer)
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_db_ver alias for $1;
	_struct text;
begin
	select into _struct public.gm_concat_table_structure();
	return _struct;
end;
';

-- ---------------------------------------------
create or replace function gm.concat_table_structure()
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_struct text;
begin
	select into _struct public.gm_concat_table_structure();
	return _struct;
end;
';

-- =============================================
select public.log_script_insertion('$RCSfile: gmConcatTableStructureFutureStub.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmConcatTableStructureFutureStub.sql,v $
-- Revision 1.1  2007-05-07 16:21:51  ncq
-- - needed during upgrade from v2/3/4/5
--
--