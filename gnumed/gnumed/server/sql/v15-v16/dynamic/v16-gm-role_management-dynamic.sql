-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.create_pg_account(name, text)
	returns boolean
	language 'plpgsql'
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

	perform 1 from pg_group where groname = _username;
	if FOUND then
		return true;
	end if;

	_query := ''create user '' || quote_ident(_username)
		|| '' with password '' || quote_literal(_password)
		|| '';'';
	execute _query;

	perform 1 from pg_user where usename = _username;
	if not FOUND then
		raise exception ''cannot create PostgreSQL account [%]'', _username;
		return false;
	end if;

	return true;
END;';


revoke all on function gm.create_pg_account(name, text) from public;
grant execute on function gm.create_pg_account(name, text) to "gm-dbo";


comment on function gm.create_pg_account(name, text) is
'To create users one needs to have CREATEROLE rights.
 Only gm-dbo is GRANTed EXECUTE. This way users need
 to know the gm-dbo (GNUmed admin) password to execute
 the function.';

-- --------------------------------------------------------------
select gm.create_pg_account('gm-staff', '\/\/\/\/');
alter role "gm-staff" with password null;
alter role "gm-staff" nologin;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-gm-role_management-dynamic.sql', '16.3');

-- ==============================================================
