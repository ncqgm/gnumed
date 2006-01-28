-- GNUmed public function to create new db users

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCreateUserFunction.sql,v $
-- $Id: gmCreateUserFunction.sql,v 1.1 2006-01-28 10:37:11 ncq Exp $
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
	_query text;
BEGIN
	perform 1 from pg_user where usename = _username;
	if FOUND then
		return true;
	end if;
	_query := ''create user '' || quote_ident(_username)
				|| '' with password '' || quote_literal(_password)
				|| '' in group "gm-doctors", "gm-public";'';
	execute _query;
	perform 1 from pg_user where usename = _username;
	if FOUND then
		return true;
	end if;
	return false;
END;';

-- ===================================================
-- do simple schema revision tracking
--select log_script_insertion('$RCSfile: gmCreateUserFunction.sql,v $', '$Revision: 1.1 $');

-- ===================================================
-- $Log: gmCreateUserFunction.sql,v $
-- Revision 1.1  2006-01-28 10:37:11  ncq
-- - allow frontend to create users
--
--
