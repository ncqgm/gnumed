-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-health_issue-dynamic.sql,v 1.5 2008-04-11 12:31:43 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.health_issue.fk_encounter is
	'The encounter during which this health issue was added.';

-- ensure consistency
\unset ON_ERROR_STOP
drop function clin.trf_ensure_issue_encounter_patient_consistency() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_ensure_issue_encounter_patient_consistency()
	returns trigger
	language 'plpgsql'
	as '
declare
	encounter_patient integer;
	msg text;
begin
	select into encounter_patient fk_patient from clin.encounter where pk = NEW.fk_encounter;
	if encounter_patient != NEW.fk_patient then
		msg := ''clin.trf_ensure_issue_encounter_patient_consistence(): Integrity error. Encounter '' || NEW.fk_encounter
		|| '' belongs to patient '' || encounter_patient
		|| ''. Health issue '' || NEW.pk
		|| '' belongs to patient '' || NEW.fk_patient
		|| ''. Cannot link the two.'';
		raise exception ''%'', msg;
	end if;
	return NEW;
end;';

create trigger tr_ensure_issue_encounter_patient_consistency
	before insert or update on clin.health_issue
	for each row execute procedure clin.trf_ensure_issue_encounter_patient_consistency()
;

-- update data
create or replace function tmp_add_encounters_to_issues()
	returns boolean
	language plpgsql
	as '
DECLARE
	_row record;
	msg text;

	pk_target_encounter integer;
BEGIN
	for _row in select * from clin.health_issue where fk_encounter is null loop

		msg := ''issue: '' || _row.pk;
		raise notice ''%'', msg;

		-- find earliest modification time of any episode within this issue
		pk_target_encounter := null;
		select fk_encounter into pk_target_encounter from clin.episode where
			modified_when = (
				select min(modified_when) from clin.episode where fk_health_issue = _row.pk
			)
			and fk_health_issue = _row.pk
			limit 1;

		if found then
			msg := ''encounter with earliest modification time: '' || pk_target_encounter;
			raise notice ''%'', msg;
		else

			-- no episode for issue, so create new encounter
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
				(select fk_patient from clin.health_issue where pk = _row.pk),
				(select pk from clin.encounter_type where description = ''administrative encounter''),
				(select modified_when from clin.health_issue where pk = _row.pk),
				(select modified_when from clin.health_issue where pk = _row.pk)
			);
			select currval(pg_get_serial_sequence(''clin.encounter'', ''pk'')) into pk_target_encounter;

		end if;

		msg := ''linking issue ('' || _row.pk || '') <-> encounter ('' || pk_target_encounter || '')'';
		raise notice ''%'', msg;

		update clin.health_issue
		set fk_encounter = pk_target_encounter
		where pk = _row.pk;

	end loop;
	return true;
END;';

select tmp_add_encounters_to_issues();

drop function tmp_add_encounters_to_issues();

alter table clin.health_issue alter column fk_encounter set not null;

-- alter views
-- ... missing  ...


\unset ON_ERROR_STOP
drop function audit.trf_announce_h_issue_mod() cascade;
\set ON_ERROR_STOP 1
select gm.add_table_for_notifies('clin', 'health_issue');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-health_issue-dynamic.sql,v $', '$Revision: 1.5 $');

-- ==============================================================
-- $Log: v9-clin-health_issue-dynamic.sql,v $
-- Revision 1.5  2008-04-11 12:31:43  ncq
-- - drop announce triggers so they can be recreated
--
-- Revision 1.4  2008/03/03 14:26:07  ncq
-- - need to check against fk_health_issue/fk_episode, too
--
-- Revision 1.3  2008/03/03 14:05:51  ncq
-- - need to test _row.pk against fk_health_issue when dealing with clin.episode...
--
-- Revision 1.2  2008/03/03 13:45:19  ncq
-- - need to explicitely null relevant variables inside loop
--
-- Revision 1.1  2008/03/02 11:25:55  ncq
-- - new files
--
--
