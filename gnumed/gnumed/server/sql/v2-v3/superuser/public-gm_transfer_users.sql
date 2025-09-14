-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
set default_transaction_read_only to off;

\set ON_ERROR_STOP 1

-- --------------------------------------------------------------

create or replace function gm_transfer_users(text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_source_group alias for $1;
	target_group text;
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
	select into target_group current_database();
	perform 1 from pg_group where groname = target_group;
	if not FOUND then
		raise exception ''gm_transfer_users(): target group [%] does not exist'', target_group;
		return false;
	end if;

	-- loop over group member IDs
	select into member_ids grolist from pg_group where groname = _source_group;
	FOR idx IN coalesce(array_lower(member_ids, 1), 0) .. coalesce(array_upper(member_ids, 1), -1) LOOP
		raise notice ''idx: %'', idx;
		member_id := member_ids[idx];
		raise notice ''user (group member) id: %'', member_id;
		select into member_name usename from pg_user where usesysid = member_id;
		raise notice ''name: %'', member_name;
		tmp := ''gm_transfer_users(text): transferring "''
				|| member_name || ''" (''
				|| member_id || '') from group "''
				|| _source_group || ''" to group "''
				|| target_group || ''"'';
		raise notice ''%'', tmp;
		-- satisfy "database = samerole" in pg_hba.conf
		tmp := ''alter group '' || quote_ident(target_group) || '' add user '' || quote_ident(member_name) || '';'';
		execute tmp;

	end LOOP;

	return true;
END;';

-- ==============================================================
