-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-waiting_list-dynamic.sql,v 1.4 2009-01-22 11:17:33 ncq Exp $
-- $Revision: 1.4 $


set default_transaction_read_only to off;
-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
set check_function_bodies to on;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.waiting_list drop constraint non_empty_area;
\set ON_ERROR_STOP 1

alter table clin.waiting_list
	add constraint non_empty_area
		check (trim(area) <> '');

comment on column clin.waiting_list.area is
	'an arbitrary value by which filtering waiting patients into zones becomes possible';

select gm.add_table_for_notifies('clin', 'waiting_list');
select gm.add_table_for_notifies('clin', 'waiting_list', 'waiting_list_generic');

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_waiting_list cascade;
\set ON_ERROR_STOP 1

create view clin.v_waiting_list as
select
	wl.list_position
		as list_position,
	wl.area
		as waiting_zone,
	wl.urgency
		as urgency,
	i.title
		as title,
	n.firstnames
		as firstnames,
	n.lastnames
		as lastnames,
	n.preferred
		as preferred_name,
	i.dob
		as dob,
	i.gender
		as gender,
	_(i.gender)
		as l10n_gender,
	wl.registered
		as registered,
	(select now() - wl.registered)
		as waiting_time,
	(select to_char(age(now(), wl.registered), 'TMDD HH24:MI'))
		as waiting_time_formatted,
--	(select started from clin.v_most_recent_encounters where wl.fk_patient = vmre.pk_patient)
--		as start_most_recent_encounter,
--	(select reason_for_encounter from clin.v_most_recent_encounters where wl.fk_patient = vmre.pk_patient)
--		as most_recent_rfe,
	wl.comment
		as comment,
--	(select started from clin.encounter ce
--	 where vmre.pk_encounter = ce.pk
--	 order by last_affirmed desc limit 1 offset 1
--	)	as start_previous_encounter,
	i.pk
		as pk_identity,
	n.id
		as pk_name,
	i.pupic
		as pupic,
	wl.pk
		as pk_waiting_list
from
	clin.waiting_list wl,
	dem.identity i,
	dem.names n
where
	wl.fk_patient = i.pk and
	wl.fk_patient = n.id_identity and
	i.deceased is NULL and
	n.active is true
;


grant select on clin.v_waiting_list to group "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function clin.move_waiting_list_entry(integer, integer) cascade;
\set ON_ERROR_STOP

create or replace function clin.move_waiting_list_entry(integer, integer)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_wl_pos_src alias for $1;
	_wl_pos_dest alias for $2;

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
		raise notice ''clin.move_waiting_list_entry(): Cannot move entry [%] to [%]. Entry does not exist.'', _wl_pos_src, wl_pos_dest ;
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
-- factor out
delete from clin.waiting_list where
	area = 'LMcC'
	and comment = 'wants to see Dr.McCoy for scar problems'
	and fk_patient = (
		select pk_identity from dem.v_basic_person where
			lastnames = 'Kirk'
			and firstnames = 'James Tiberius'
	);

insert into clin.waiting_list (
	fk_patient,
	list_position,
	comment,
	area
) values (
	12,
	1,
	'wants to see Dr.McCoy for scar problems',
	'LMcC'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-waiting_list-dynamic.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: v10-clin-waiting_list-dynamic.sql,v $
-- Revision 1.4  2009-01-22 11:17:33  ncq
-- - function to move entries in waiting list
--
-- Revision 1.3  2009/01/21 22:39:39  ncq
-- - display days, too
--
-- Revision 1.2  2009/01/17 23:16:35  ncq
-- - add proper signals
-- - improve view
--
-- Revision 1.1  2009/01/16 13:30:40  ncq
-- - new
--
--