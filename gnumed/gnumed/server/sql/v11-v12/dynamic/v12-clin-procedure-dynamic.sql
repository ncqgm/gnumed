-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-clin-procedure-dynamic.sql,v 1.3 2009-09-17 22:01:58 ncq Exp $
-- $Revision: 1.3 $

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
		check (
			((fk_hospital_stay is null) and (clin_where is not null))
				or
			((fk_hospital_stay is not null) and (clin_where is null))
		)
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


grant select, insert, update, delete on
	clin.procedure
TO GROUP "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_procedures cascade;
\set ON_ERROR_STOP 1



create view clin.v_pat_procedures as

select
	cpr.pk
		as pk_procedure,
	(select enc.fk_patient from clin.encounter enc where enc.pk = cpr.fk_encounter)
		as pk_patient,
	cpr.soap_cat,
	cpr.clin_when,
	cpr.narrative
		as performed_procedure,
	coalesce (
		(select chs.narrative from clin.hospital_stay chs where cpr.fk_hospital_stay = chs.pk),
		cpr.clin_where
	)	as clin_where,
	(select description from clin.episode where pk = cpr.fk_episode)
		as episode,
	(select description from clin.health_issue where pk = (
		select fk_health_issue from clin.episode where pk = cpr.fk_episode
	))
		as health_issue,

	cpr.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cpr.modified_by),
		'<' || cpr.modified_by || '>'
	)
		as modified_by,
	cpr.row_version,
	cpr.fk_encounter
		as pk_encounter,
	cpr.fk_episode
		as pk_episode,
	cpr.fk_hospital_stay
		as pk_hospital_stay,
	(select epi.fk_health_issue from clin.episode epi where epi.pk = cpr.fk_episode)
		as pk_health_issue,
	cpr.xmin as xmin_procedure
from
	clin.procedure cpr
;



grant select on
	clin.v_pat_procedures
TO GROUP "gm-doctors";

-- --------------------------------------------------------------

-- emr journal

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-procedure-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v12-clin-procedure-dynamic.sql,v $
-- Revision 1.3  2009-09-17 22:01:58  ncq
-- - fix single_location check
-- - v-pat-procedures
--
-- Revision 1.2  2009/09/15 15:21:01  ncq
-- - fix proper check on stay vs clin_where
--
-- Revision 1.1  2009/09/13 18:17:28  ncq
-- - new table
--
--