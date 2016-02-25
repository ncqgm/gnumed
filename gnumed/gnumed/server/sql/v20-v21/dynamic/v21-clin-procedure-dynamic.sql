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
update clin.procedure set
	is_ongoing = False
where
	is_ongoing is True
		and
	clin_end is not null
		and
	clin_end < (now() + '15 minutes'::interval)
;

-- --------------------------------------------------------------
alter table clin.procedure
	drop constraint if exists
		procedure_sane_ongoing
;

-- --------------------------------------------------------------
drop function if exists clin.trf_normalize_proc_is_ongoing() cascade;

create function clin.trf_normalize_proc_is_ongoing()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	if NEW.clin_end > clock_timestamp() then
		NEW.is_ongoing := TRUE;
	else
		NEW.is_ongoing := FALSE;
	end if;

	return NEW;
END;';


create trigger tr_normalize_proc_is_ongoing
	before update or insert on clin.procedure
	for each row
	when (NEW.clin_end IS NOT NULL)
	execute procedure clin.trf_normalize_proc_is_ongoing()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-procedure-dynamic.sql', '21.0');
