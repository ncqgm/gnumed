-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-gm-role_management-dynamic.sql,v 1.1 2008-12-01 12:09:41 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.transfer_users(text, text)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_source_group alias for $1;
	_target_group alias for $2;
	member_ids int[];
	member_id int;
	member_name text;
	tmp text;
BEGIN
	-- source group exists ?
	perform 1 from pg_group where groname = _source_group;
	if not FOUND then
		raise exception ''gm_transfer_users(): source group [%] does not exist'', _source_group;
		return false;
	end if;

	-- target group exists ?
	perform 1 from pg_group where groname = _target_group;
	if not FOUND then
		raise exception ''gm_transfer_users(): target group [%] does not exist'', _target_group;
		return false;
	end if;

	-- loop over group member IDs
	select into member_ids grolist from pg_group where groname = _source_group;
	FOR idx IN coalesce(array_lower(member_ids, 1), 0) .. coalesce(array_upper(member_ids, 1), -1) LOOP
		member_id := member_ids[idx];
		select into member_name usename from pg_user where usesysid = member_id;
		tmp := ''gm_transfer_users(text): transferring "''
				|| member_name || ''" (''
				|| member_id || '') from group "''
				|| _source_group || ''" to group "''
				|| _target_group || ''"'';
		raise notice ''%'', tmp;
		-- satisfy "database = samegroup" in pg_hba.conf
		tmp := ''alter group '' || quote_ident(_target_group) || '' add user '' || quote_ident(member_name) || '';'';
		execute tmp;

	end LOOP;

	return true;
END;';


revoke all on function gm.transfer_users(text, text) from public;
grant execute on function gm.transfer_users(text, text) to "gm-dbo";


comment on function gm.transfer_users(text, text) is
'This function transfers adds users from the group role given in the
 argument to the group role corresponding to the current database
 name. This enables group membership based authentication as used
 in GNUmed. This operation is typically only run on database upgrade
 and is only available to gm-dbo.';


create or replace function gm.transfer_users(text)
	returns boolean
	language sql
	as 'select gm.transfer_users($1, current_database());';


revoke all on function gm.transfer_users(text) from public;
grant execute on function gm.transfer_users(text) to "gm-dbo";


\unset ON_ERROR_STOP
drop function public.gm_transfer_users(name, text) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create or replace function gm.create_user(name, text)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_username alias for $1;
	_password alias for $2;
	_database text;
	_query text;
BEGIN
	perform 1 from pg_user where usename = _username;
	if not FOUND then
		_query := ''create user '' || quote_ident(_username)
					|| '' with password '' || quote_literal(_password)
					|| '';'';
		execute _query;
		perform 1 from pg_user where usename = _username;
		if not FOUND then
			raise exception ''cannot create user [%]'', _username;
			return false;
		end if;
	end if;

	_query := ''alter group "gm-logins" add user '' || quote_ident(_username) || '';'';
	execute _query;

	_query := ''alter group "gm-doctors" add user '' || quote_ident(_username) || '';'';
	execute _query;

	_query := ''alter group "gm-public" add user '' || quote_ident(_username) || '';'';
	execute _query;

	-- satisfy "database = samegroup" in pg_hba.conf
	select into _database current_database();
	_query := ''alter group '' || quote_ident(_database) || '' add user '' || quote_ident(_username) || '';'';
	execute _query;

	return true;
END;';


revoke all on function gm.create_user(name, text) from public;
grant execute on function gm.create_user(name, text) to "gm-dbo";


comment on function gm.create_user(name, text) is
'To create users one needs to have CREATEROLE rights.
 Only gm-dbo is GRANTed EXECUTE. This way users need
 to know the gm-dbo (GNUmed admin) password to execute
 the function.';


\unset ON_ERROR_STOP
drop function public.gm_create_user(name, text) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create or replace function gm.drop_user(name)
	returns boolean
	language 'plpgsql'
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


revoke all on function gm.drop_user(name) from public;
grant execute on function gm.drop_user(name) to "gm-dbo";


comment on function gm.drop_user(name) is
'To drop users one needs to have CREATEROLE rights.
 Only gm-dbo is GRANTed EXECUTE.
 This way users need to know the gm-dbo (GNUmed admin) password
 to execute the function.';


\unset ON_ERROR_STOP
drop function public.gm_drop_user(name, text) cascade;
\set ON_ERROR_STOP 1


-- --------------------------------------------------------------
create or replace function gm.disable_user(name)
	returns boolean
	language 'plpgsql'
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


revoke all on function gm.disable_user(name) from public;
grant execute on function gm.disable_user(name) to "gm-dbo";


comment on function gm.disable_user(name) is
'To disable users one needs to have CREATEROLE rights.
 Only gm-dbo is GRANTed EXECUTE.
 This way users need to know the gm-dbo (GNUmed admin) password
 to execute the function.';


\unset ON_ERROR_STOP
drop function public.gm_disable_user(name, text) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create or replace function gm.get_users(name)
	returns text[]
	language 'plpgsql'
	as '
DECLARE
	_db alias for $1;
	_gm_users text[];
	_user text;
BEGIN

	_gm_users := ARRAY[''gm-logins'', ''gm-public'', ''gm-doctors'', _db];

	-- add members of groups gm-logins, gm-public, _db
	FOR _user in
		select distinct rolname from pg_roles where oid in (
			select member from pg_auth_members where roleid in (
				select oid from pg_roles where rolname in (''gm-logins'', ''gm-public'', _db)
			)
		)
	LOOP
		continue when _user = ''postgres'';
		continue when _user = any(_gm_users);
		_gm_users := _gm_users || _user;
	END LOOP;

	-- add *.modified_by entries
	FOR _user in select distinct modified_by from audit.audit_fields LOOP
		continue when _user = ''postgres'';
		continue when _user = any(_gm_users);
		_gm_users := _gm_users || _user;
	END LOOP;

	-- add dem.staff.db_user entries
	FOR _user in select distinct db_user from dem.staff LOOP
		continue when _user = ''postgres'';
		continue when _user = any(_gm_users);
		_gm_users := _gm_users || _user;
	END LOOP;

	return _gm_users;
END;';


revoke all on function gm.get_users(name) from public;
grant execute on function gm.get_users(name) to "gm-dbo";


create or replace function gm.get_users()
	returns text[]
	language sql
	as 'select gm.get_users(current_database());';


revoke all on function gm.get_users() from public;
grant execute on function gm.get_users() to "gm-dbo";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-gm-role_management-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-gm-role_management-dynamic.sql,v $
-- Revision 1.1  2008-12-01 12:09:41  ncq
-- - new
--
--