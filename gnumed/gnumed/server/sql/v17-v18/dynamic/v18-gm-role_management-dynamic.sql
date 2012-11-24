-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1
set check_function_bodies to on;

--set default_transaction_read_only to off;
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

	_query := ''alter group "gm-public" add user '' || quote_ident(_username) || '';'';
	execute _query;

	-- satisfy "database = samerole" in pg_hba.conf
	select into _database current_database();
	_query := ''alter group '' || quote_ident(_database) || '' add user '' || quote_ident(_username) || '';'';
	execute _query;

	return true;
END;';


revoke all on function gm.create_user(name, text) from public;
grant execute on function gm.create_user(name, text) to "gm-dbo";


comment on function gm.create_user(name, text) is
'To create users one needs to have CREATEROLE rights. Only gm-dbo is
 GRANTed EXECUTE. This way users need to know the gm-dbo (GNUmed admin)
 password to execute the function.

 Newly created users belong to group "gm-public" by default.';

-- --------------------------------------------------------------
create or replace function gm.add_user_to_permission_group(name, name)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_username alias for $1;
	_target_group alias for $2;
	_valid_groups name[];
	_group name;
	_query text;
BEGIN
	-- verify user
	perform 1 from pg_user where usename = _username;
	if not FOUND then
		raise warning ''[gm.add_user_to_permission_group]: user [%] does not exist'', _username;
		return False;
	end if;

	-- verify logical group validity
	-- no "gm-nurse", "gm-admin" just yet
	_valid_groups := ARRAY[quote_ident(''gm-public''), quote_ident(''gm-staff''), quote_ident(''gm-doctors'')];
	if quote_ident(_target_group) <> all(_valid_groups) then
		raise warning ''[gm.add_user_to_permission_group]: invalid group [%]'', _target_group;
		return False;
	end if;

	-- verify group existance
	perform 1 from pg_group where groname = _target_group;
	if not FOUND then
		raise warning ''[gm.add_user_to_permission_group]: group [%] does not exist'', _target_group;
		return False;
	end if;

	-- drop user from all groups
	--FOREACH _group IN ARRAY _valid_groups LOOP
	FOR _group IN SELECT unnest(_valid_groups) LOOP
		_query := ''alter group '' || _group || '' drop user '' || quote_ident(_username) || '';'';
		execute _query;
	END LOOP;

	-- add user to desired group
	_query := ''alter group '' || quote_ident(_target_group) || '' add user '' || quote_ident(_username) || '';'';
	execute _query;

	return True;
END;';


revoke all on function gm.add_user_to_permission_group(name, name) from public;
grant execute on function gm.add_user_to_permission_group(name, name) to "gm-dbo";


comment on function gm.add_user_to_permission_group(name, name) is
'Only gm-dbo is GRANTed EXECUTE on this function. This way users need
 to know the gm-dbo (GNUmed admin) password to execute it.';

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

	-- GNUmed group roles
	_gm_users := ARRAY[''gm-logins'', ''gm-public'', ''gm-doctors'', ''gm-staff'', _db];

	-- add roles being *members* of groups gm-logins, gm-public, _db
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

	-- add roles mentioned in any *.modified_by fields
	FOR _user in select distinct modified_by from audit.audit_fields LOOP
		continue when _user = ''postgres'';
		continue when _user = any(_gm_users);
		_gm_users := _gm_users || _user;
	END LOOP;

	-- add roles mentioned in dem.staff.db_user
	FOR _user in select distinct db_user from dem.staff LOOP
		continue when _user = ''postgres'';
		continue when _user = any(_gm_users);
		_gm_users := _gm_users || _user;
	END LOOP;

	return _gm_users;
END;';


revoke all on function gm.get_users(name) from public;
grant execute on function gm.get_users(name) to "gm-dbo";


comment on function gm.get_users(name) is
	'Convenience function listing all PostgreSQL accounts (roles) needed for a consistent dump of the database.';


create or replace function gm.get_users()
	returns text[]
	language sql
	as 'select gm.get_users(current_database());';


revoke all on function gm.get_users() from public;
grant execute on function gm.get_users() to "gm-dbo";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-gm-role_management-dynamic.sql', '18.0');
