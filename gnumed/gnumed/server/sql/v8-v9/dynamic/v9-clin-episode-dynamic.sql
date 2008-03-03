-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-episode-dynamic.sql,v 1.3 2008-03-03 14:26:07 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.health_issue.fk_encounter is
	'The encounter during which this episode was added (begun).';

-- ensure consistency
\unset ON_ERROR_STOP
drop function clin.trf_ensure_episode_encounter_patient_consistency() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_ensure_episode_encounter_patient_consistency()
	returns trigger
	language 'plpgsql'
	as '
declare
	encounter_patient integer;
	msg text;
begin
	select into encounter_patient fk_patient from clin.encounter where pk = NEW.fk_encounter;
	if encounter_patient != NEW.fk_patient then
		msg := ''clin.trf_ensure_episode_encounter_patient_consistency(): Integrity error. Encounter '' || NEW.fk_encounter
		|| '' belongs to patient '' || encounter_patient
		|| '' but episode '' || NEW.pk
		|| '' belongs to patient '' || NEW.fk_patient
		|| ''. Cannot link the two.'';
		raise exception ''%'', msg;
	end if;
	return NEW;
end;';

create trigger tr_ensure_episode_encounter_patient_consistency
	before insert or update on clin.episode
	for each row execute procedure clin.trf_ensure_episode_encounter_patient_consistency()
;

-- update data
create or replace function tmp_add_encounters_to_episodes()
	returns boolean
	language plpgsql
	as '
DECLARE
	_row record;
	msg text;

	min_clin_when timestamp with time zone;
	pk_encounter_min_clin_when integer;

	min_modified_when timestamp with time zone;
	pk_encounter_min_modified_when integer;

	pk_target_encounter integer;
BEGIN
	for _row in select * from clin.episode where fk_encounter is null loop

		msg := ''episode: '' || _row.pk;
		raise notice ''%'', msg;

		-- find earliest modification time of any clinical item within this episode
		pk_encounter_min_modified_when := null;
		min_modified_when := null;
		select fk_encounter, modified_when into pk_encounter_min_modified_when, min_modified_when
		from clin.clin_root_item where
			modified_when = (
				select min(modified_when) from clin.clin_root_item where fk_episode = _row.pk
			)
			and fk_episode = _row.pk
		limit 1;
		msg := ''earliest modification time: '' || min_modified_when || '' encounter: '' || pk_encounter_min_modified_when;
		raise notice ''%'', msg;

		-- find earliest clinical time for any clinical item within this episode
		pk_encounter_min_clin_when := null;
		min_clin_when := null;
		select fk_encounter, clin_when into pk_encounter_min_clin_when, min_clin_when
		from clin.clin_root_item where
			clin_when = (
				select min(clin_when) from clin.clin_root_item where fk_episode = _row.pk
			)
			and fk_episode = _row.pk
		limit 1;
		msg := ''earliest clinical time: '' || min_clin_when || '' encounter: '' || pk_encounter_min_clin_when;
		raise notice ''%'', msg;

		pk_target_encounter := coalesce(pk_encounter_min_modified_when, pk_encounter_min_clin_when);

		if min_modified_when <= min_clin_when then
			pk_target_encounter := pk_encounter_min_modified_when;
		end if;

		if min_modified_when > min_clin_when then
			pk_target_encounter :=  pk_encounter_min_clin_when;
		end if;

		if pk_target_encounter is null then
			-- there was no clinical item for this episode
			-- in that case we will have to attach it to a fake encounter
			raise notice ''creating new encounter'';

			perform 1 from clin.encounter_type where description = ''administrative encounter'';
			if not found then
				raise notice ''creating encounter type "administrative encounter"'';
				insert into clin.encounter_type (description) values (i18n.i18n(''administrative encounter''));
			end if;

			insert into clin.encounter (
				fk_patient,
				fk_type,
				started,
				last_affirmed
			) values (
				(select pk_patient from clin.v_pat_episodes where pk_episode = _row.pk),
				(select pk from clin.encounter_type where description = ''administrative encounter''),
				(select modified_when from clin.episode where pk = _row.pk),
				(select modified_when from clin.episode where pk = _row.pk)
			);
			select currval(pg_get_serial_sequence(''clin.encounter'', ''pk'')) into pk_target_encounter;

		end if;

		msg := ''linking episode ('' || _row.pk || '') <-> encounter ('' || pk_target_encounter || '')'';
		raise notice ''%'', msg;

		update clin.episode set fk_encounter = pk_target_encounter where pk = _row.pk;

	end loop;
	return true;
END;';

select tmp_add_encounters_to_episodes();

drop function tmp_add_encounters_to_episodes();

-- set not null
alter table clin.episode alter column fk_encounter set not null;

-- alter views

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-episode-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v9-clin-episode-dynamic.sql,v $
-- Revision 1.3  2008-03-03 14:26:07  ncq
-- - need to check against fk_health_issue/fk_episode, too
--
-- Revision 1.2  2008/03/03 13:45:19  ncq
-- - need to explicitely null relevant variables inside loop
--
-- Revision 1.1  2008/03/02 11:25:55  ncq
-- - new files
--
--
