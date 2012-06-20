-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .soap_cat

-- fix NULL values
update clin.procedure set
	soap_cat = 'p'::text
where
	soap_cat is NULL;


alter table clin.procedure
	alter column soap_cat
		set default 'p'::text;



-- .end
comment on column clin.procedure.clin_end is
'When did this procedure end/is expected to end.

- NULL if unknown or .clin_when (=start) is sufficient (eg. insignificant duration)';


\unset ON_ERROR_STOP
alter table clin.procedure drop constraint procedure_sane_end cascade;
\set ON_ERROR_STOP 1


alter table clin.procedure
	add constraint procedure_sane_end check (
		(clin_end is NULL)
			OR
		(clin_end >= clin_when)
	);



-- .is_ongoing
comment on column clin.procedure.is_ongoing is
'Whether this procedure is still going on (such as desensibilisation, chemotherapy, etc).';


alter table clin.procedure
	alter column is_ongoing
		set default false;

update clin.procedure set
	is_ongoing = DEFAULT
where
	is_ongoing is NULL
;


alter table clin.procedure
	alter column is_ongoing
		set not null;


alter table clin.procedure
	add constraint procedure_sane_ongoing check (
		(is_ongoing is FALSE)
			OR
		(
			(clin_end is NULL)
				OR
			(clin_end > now())
		)
	);



\unset ON_ERROR_STOP
drop function clin.trf_normalize_proc_is_ongoing() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_normalize_proc_is_ongoing()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	if NEW.clin_end is NULL then
		return NEW;
	end if;

	if NEW.clin_end > clock_timestamp() then
		NEW.is_ongoing := TRUE;
	else
		NEW.is_ongoing := FALSE;
	end if;

	return NEW;
END;';


create trigger tr_normalize_proc_is_ongoing
	before update on clin.procedure
	for each row execute procedure clin.trf_normalize_proc_is_ongoing()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-procedure-dynamic.sql', 'Revision: 1.1');
