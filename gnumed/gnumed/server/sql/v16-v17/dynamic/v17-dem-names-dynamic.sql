-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function dem.trf_protect_active_name_of_person() cascade;
\set ON_ERROR_STOP 1

create or replace function dem.trf_protect_active_name_of_person()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_name_count integer;
	_msg text;
BEGIN
	-- how many names are there for the identity at the end of the Tx ?
	select count(1) into _name_count
	from dem.names
	where
		id_identity = OLD.id_identity
			and
		active is true
	;

	-- less than one name ?
	if _name_count < 1 then
		_msg := ''person '' || OLD.id_identity || '' must have at least one, active, name entry'';
		raise exception check_violation using message = _msg;
		return OLD;
	end if;

	return OLD;
END;';


comment on function dem.trf_protect_active_name_of_person() is
	'A person must have at least one, active, name record.';


create constraint trigger tr_protect_active_name_of_person
	after update or delete on dem.names
		deferrable
		initially deferred
	for each row execute procedure dem.trf_protect_active_name_of_person()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-names-dynamic.sql', '17.0');
