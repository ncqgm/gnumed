-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
drop function if exists clin.move_waiting_list_entry(integer, integer) cascade;
drop function if exists clin.move_waiting_list_entry(IN _wl_pos_src integer, IN _wl_pos_dest integer) cascade;

create function clin.move_waiting_list_entry(IN _wl_pos_src integer, IN _wl_pos_dest integer)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_tmp_pos integer;
	_curr_max_pos integer;
BEGIN
	if _wl_pos_src = _wl_pos_dest then
		return true;
	end if;

	if _wl_pos_dest < 1 then
		raise notice ''clin.move_waiting_list_entry(): Will not move entry [%] before start of list [%].'', _wl_pos_src, _wl_pos_dest;
		return False;
	end if;

	select max(list_position) into _curr_max_pos from clin.waiting_list;
	-- do not move last entry further down
	if _wl_pos_src = _curr_max_pos then
		if _wl_pos_dest > _wl_pos_src then
			raise notice ''clin.move_waiting_list_entry(): Will not move last entry [%] beyond end of list to [%].'', _wl_pos_src, _wl_pos_dest;
			return False;
		end if;
	end if;

	-- does the source row exist ?
	perform 1 from clin.waiting_list where list_position = _wl_pos_src;
	if not found then
		raise notice ''clin.move_waiting_list_entry(): Cannot move entry [%] to [%]. Entry does not exist.'', _wl_pos_src, _wl_pos_dest ;
		return false;
	end if;

	-- load destination row
	perform 1 from clin.waiting_list where list_position = _wl_pos_dest;

	-- does not exist
	if not found then
		-- do not move entry beyond end of list more than necessary
		if _wl_pos_dest > (_curr_max_pos + 1) then
			_tmp_pos := _curr_max_pos + 1;
		else
			_tmp_pos := _wl_pos_dest;
		end if;
		-- so update row to move and be done with it
		update clin.waiting_list
			set list_position = _tmp_pos
			where list_position = _wl_pos_src;
		return true;
	end if;

	-- move existing row out of the way
	select (max(list_position) + _wl_pos_dest + _wl_pos_src) into _tmp_pos from clin.waiting_list;
	update clin.waiting_list
		set list_position = _tmp_pos
		where list_position = _wl_pos_dest;

	-- move row to move
	update clin.waiting_list
		set list_position = _wl_pos_dest
		where list_position = _wl_pos_src;

	-- move back existing row
	update clin.waiting_list
		set list_position = _wl_pos_src
		where list_position = _tmp_pos;

	return true;
END;';

comment on function clin.move_waiting_list_entry(integer, integer) is
'Move row with logical position $1 into logical position $2. If another row
 exists with position $2 it will be moved to position $1 in the process.
 Fails if there is no row with position $1.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-move_waiting_list_entry-fixup.sql', '22.24');
