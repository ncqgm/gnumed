-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-clin-procedure-dynamic.sql,v 1.1 2009-09-13 18:17:28 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select audit.add_table_for_audit('clin', 'procedure');
select gm.add_table_for_notifies('clin', 'procedure');



comment on table clin.procedure is
'This table holds procedure/operations performed on the patient
 both in hospital or in community care.';

comment on column clin.procedure.narrative is
'Which procedure/operation was performed.';

comment on column clin.procedure.clin_where is
'Where was the procedure/operation performed,
 unless fk_hospital_stay is not null';

comment on column clin.procedure.fk_hospital_stay is
'At which hospital was the procedure performed,
 unless clin_where is not null,
 if null it was an ambulatory procedure.';



alter table clin.procedure
	alter column fk_hospital_stay
		set default null;


alter table clin.procedure
	alter column clin_where
		set default null;



\unset ON_ERROR_STOP
alter table clin.procedure drop constraint sane_location cascade;
\set ON_ERROR_STOP 1

alter table clin.procedure
	add constraint sane_location
		check (gm.is_null_or_non_empty_string(clin_where))
;



\unset ON_ERROR_STOP
alter table clin.procedure drop constraint sane_location_definition cascade;
\set ON_ERROR_STOP 1

alter table clin.procedure
	add constraint single_location_definition
		check ((
			(fk_hospital_stay is null)
				and
			(clin_where is null)
		) is false )
;



\unset ON_ERROR_STOP
alter table clin.procedure drop constraint sane_soap_cat cascade;
\set ON_ERROR_STOP 1

alter table clin.procedure
	add constraint sane_soap_cat
		check(soap_cat in ('a', 'p'))
;



-- x-check fk_episode vs fk_hospital_stay
\unset ON_ERROR_STOP
drop function clin.trf_sanity_check_episode() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_sanity_check_episode()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_hospital_stay_episode_pk integer;
BEGIN
	if NEW.fk_hospital_stay is null then
		return NEW;
	end if;

	select into _hospital_stay_episode_pk fk_episode
		from clin.hospital_stay
		where pk = NEW.fk_hospital_stay;

	if NEW.fk_episode = _hospital_stay_episode_pk then
		return NEW;
	end if;

	raise exception ''[clin.procedure]: INSERT/UPDATE failed: fk_episode (%) does not match fk_episode (%) behind fk_hospital_stay (%)'', NEW.fk_episode, _hospital_stay_episode_pk, fk_hospital_stay;
	return NEW;
END;';


create trigger tr_sanity_check_episode
	before insert or update on clin.procedure
		for each row execute procedure clin.trf_sanity_check_episode()
;

-- --------------------------------------------------------------
grant select, insert, update, delete on
	clin.procedure
TO GROUP "gm-doctors";

-- --------------------------------------------------------------

-- emr journal
-- search terms

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-procedure-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-procedure-dynamic.sql,v $
-- Revision 1.1  2009-09-13 18:17:28  ncq
-- - new table
--
--