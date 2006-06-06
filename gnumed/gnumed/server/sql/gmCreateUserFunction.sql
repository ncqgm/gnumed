-- GNUmed functions to manage database accounts

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCreateUserFunction.sql,v $
-- $Id: gmCreateUserFunction.sql,v 1.4 2006-06-06 20:57:29 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net
-- ===================================================================
\set ON_ERROR_STOP 1

-- ===================================================
create or replace function gm_create_user(name, text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_username alias for $1;
	_password alias for $2;
	_database text;
	_query text;
BEGIN
	perform 1 from pg_user where usename = _username;
	if FOUND then
		return true;
	end if;
	-- satisfy "database = samegroup" in pg_hba.conf
	select into _database current_database();
	_query := ''create user '' || quote_ident(_username)
				|| '' with password '' || quote_literal(_password)
				|| '' in group "gm-doctors", "gm-public", "gm-logins", '' || quote_ident(_database)
				|| '';'';
	execute _query;
	perform 1 from pg_user where usename = _username;
	if FOUND then
		return true;
	end if;
	return false;
END;';

revoke all on function gm_create_user(name, text) from public;
grant execute on function gm_create_user(name, text) to "gm-dbo";

comment on function gm_create_user(name, text) is
	'To create users one needs to have superuser rights. We do
	 not want to grant superuser rights to any GNUmed account,
	 however. Therefore this function is owned by postgres and
	 is set SECURITY DEFINER. Only gm-dbo is GRANTed EXECUTE.
	 This way users need to know the gm-dbo (GNUmed admin) password
	 to execute the function. Later on roles should be used to
	 limit execution of this function.';

-- ===================================================
create or replace function gm_drop_user(name)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_username alias for $1;
	_query text;
BEGIN
	perform 1 from pg_user where usename = _username;
	if not FOUND then
		return true;
	end if;
	_query := ''drop user '' || quote_ident(_username) || '';'';
	execute _query;
	perform 1 from pg_user where usename = _username;
	if FOUND then
		return false;
	end if;
	return true;
END;';

revoke all on function gm_drop_user(name) from public;
grant execute on function gm_drop_user(name) to "gm-dbo";

comment on function gm_drop_user(name) is
	'To drop users one needs to have superuser rights. We do
	 not want to grant superuser rights to any GNUmed account,
	 however. Therefore this function is owned by postgres and
	 is set SECURITY DEFINER. Only gm-dbo is GRANTed EXECUTE.
	 This way users need to know the gm-dbo (GNUmed admin) password
	 to execute the function. Later on roles should be used to
	 limit execution of this function.';

-- ===================================================
create or replace function gm_disable_user(name)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_username alias for $1;
	_query text;
BEGIN
	perform 1 from pg_user where usename = _username;
	if not FOUND then
		return true;
	end if;
	_query := ''alter group "gm-logins" drop user '' || quote_ident(_username) || '';'';
	execute _query;
	return true;
END;';

revoke all on function gm_disable_user(name) from public;
grant execute on function gm_disable_user(name) to "gm-dbo";

comment on function gm_disable_user(name) is
	'To disable users one needs to have superuser rights. We do
	 not want to grant superuser rights to any GNUmed account,
	 however. Therefore this function is owned by postgres and
	 is set SECURITY DEFINER. Only gm-dbo is GRANTed EXECUTE.
	 This way users need to know the gm-dbo (GNUmed admin) password
	 to execute the function. Later on roles should be used to
	 limit execution of this function.';

-- ===================================================
--select log_script_insertion('$RCSfile: gmCreateUserFunction.sql,v $', '$Revision: 1.4 $');

-- ===================================================
-- $Log: gmCreateUserFunction.sql,v $
-- Revision 1.4  2006-06-06 20:57:29  ncq
-- - add gm_disable_user()
--
-- Revision 1.3  2006/04/23 15:15:20  ncq
-- - add comments, all this should actually be renamed to *_role and gmManageRoleFunctions.sql
-- - add gm_drop_user()
--
-- Revision 1.2  2006/02/02 16:20:08  ncq
-- - streamline gm_create_user() and enable proper insertion
--   into database authentication groups
--
-- Revision 1.1  2006/01/28 10:37:11  ncq
-- - allow frontend to create users
--
