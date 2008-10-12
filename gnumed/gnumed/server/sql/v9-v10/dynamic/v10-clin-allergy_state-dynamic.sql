-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-allergy_state-dynamic.sql,v 1.1 2008-10-12 14:58:07 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.allergy_state
	alter column fk_encounter
		set not null;


alter table clin.allergy_state
	drop constraint allergy_state_has_allergy_check;

alter table clin.allergy_state
	add check (has_allergy in (null::integer, 0, 1));

alter table clin.allergy_state
	add check (
		(has_allergy is null) or
		(has_allergy is not null) and (last_confirmed is not null)
	);



\unset ON_ERROR_STOP
drop function clin.trf_ensure_one_allergy_state_per_patient() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_ensure_one_allergy_state_per_patient()
	returns trigger
	language 'plpgsql'
	as '
declare
	_new_pk_patient integer;
	_old_pk_patient integer;
begin
	select into _new_pk_patient fk_patient
		from clin.encounter
		where pk = NEW.fk_encounter;

	-- new row, patient already there ?
	if TG_OP = ''INSERT'' then
		perform exists (
			select 1 from clin.allergy_state
			where fk_encounter in (
				select pk from clin.encounter where fk_patient = _new_pk_patient
			)
		);

		if FOUND then
			raise exception ''Cannot insert second allergy state for patient %.'', _new_pk_patient;
			return NEW;
		end if;

		return NEW;
	end if;

	if TG_OP = ''UPDATE'' then
		if NEW.fk_encounter = OLD.fk_encounter then
			return NEW;
		end if;

		select into _old_pk_patient fk_patient
			from clin.encounter
			where pk = OLD.fk_encounter;

		if _new_pk_patient = _old_pk_patient then
			return NEW;
		end if;

		raise exception ''Invalid fk_encounter update (% -> %): it would change the associated patient (% -> %).'', OLD.fk_encounter, NEW.fk_encounter, _old_pk_patient, _new_pk_patient;
		return NEW;
	end if;

	return NEW;
end;';

create trigger tr_ensure_one_allergy_state_per_patient
	before insert or update on clin.allergy_state
	for each row execute procedure clin.trf_ensure_one_allergy_state_per_patient()
;



comment on column clin.allergy_state.comment is
'A comment on the state, such as "patient says no allergies but I think he is holding back some".';

comment on column clin.allergy_state.last_confirmed is
'When was the state of allergies last confirmed. Must be not NULL if has_allergy is not NULL.';


-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_allergy_state cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_allergy_state as

select
	(select fk_patient from clin.encounter where pk = a.fk_encounter)
		as pk_patient,
	a.modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = a.modified_by),
		'<' || a.modified_by || '>'
	)
		as modified_by,
	a.last_confirmed,
	a.has_allergy,
	a.comment,
	a.fk_encounter
		as pk_encounter,
	a.pk as pk_allergy_state,
	a.xmin as xmin_allergy_state
from
	clin.allergy_state a
;

grant select on clin.v_pat_allergy_state to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_allergy_state_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_allergy_state_journal as

select
	(select fk_patient from clin.encounter where pk = a.fk_encounter)
		as pk_patient,
	a.modified_when
		as modified_when,
	a.last_confirmed
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = a.modified_by),
		'<' || a.modified_by || '>'
	)
		as modified_by,
	'o'::text
		as soap_cat,
	_('Allergy state') || ': '
		|| case
			when a.has_allergy is null then _('unknown, unasked')
			when a.has_allergy = 0 then _('no known allergies')
			when a.has_allergy = 1 then _('does have allergies')
		   end
		|| coalesce (
			' (' || _('last confirmed') || to_char(a.last_confirmed, ' YYYY-MM-DD HH24:MI') || ')',
			''
		) || coalesce (
			E'\n ' || a.comment
		) as narrative,
	a.fk_encounter
		as fk_encounter,
	null::integer
		as fk_episode,
	null::integer
		as pk_health_issue,
	a.pk
		as src_pk,
	'clin.allergy_state'::text
		as src_table
from
	clin.allergy_state a
;

grant select on clin.v_pat_allergy_state_journal to group "gm-doctors";

select i18n.i18n('Allergy state');
select i18n.i18n('no known allergies');
select i18n.i18n('does have allergies');
select i18n.i18n('unknown, unasked');
select i18n.i18n('last confirmed');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-allergy_state-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-allergy_state-dynamic.sql,v $
-- Revision 1.1  2008-10-12 14:58:07  ncq
-- - new
--
--