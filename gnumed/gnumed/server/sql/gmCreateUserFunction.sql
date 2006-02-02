-- GNUmed public function to create new db users

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCreateUserFunction.sql,v $
-- $Id: gmCreateUserFunction.sql,v 1.2 2006-02-02 16:20:08 ncq Exp $
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

-- ===================================================
--select log_script_insertion('$RCSfile: gmCreateUserFunction.sql,v $', '$Revision: 1.2 $');

-- ===================================================
-- $Log: gmCreateUserFunction.sql,v $
-- Revision 1.2  2006-02-02 16:20:08  ncq
-- - streamline gm_create_user() and enable proper insertion
--   into database authentication groups
--
-- Revision 1.1  2006/01/28 10:37:11  ncq
-- - allow frontend to create users
--
