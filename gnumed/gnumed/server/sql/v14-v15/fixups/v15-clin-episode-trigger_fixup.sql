-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_encounter vs .fk_health_issue
\unset ON_ERROR_STOP
drop function clin.trf_sanity_check_enc_vs_issue_on_epi() cascade;
\set ON_ERROR_STOP 1


create or replace function clin.trf_sanity_check_enc_vs_issue_on_epi()
	returns trigger
	language plpgsql
	as '
declare
	_identity_from_encounter integer;
	_identity_from_issue integer;
begin
	-- if issue is NULL, do not worry about mismatch
	if NEW.fk_health_issue is NULL then
		return NEW;
	end if;

	-- .fk_episode must belong to the same patient as .fk_encounter
	select fk_patient into _identity_from_encounter from clin.encounter where pk = NEW.fk_encounter;
	select fk_patient into _identity_from_issue     from clin.encounter where pk = (
		select fk_encounter from clin.health_issue where pk = NEW.fk_health_issue
	);

	if _identity_from_encounter <> _identity_from_issue then
		raise exception ''INSERT/UPDATE into %.%: Sanity check failed. Encounter % patient = %. Issue % patient = %.'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.fk_encounter,
			_identity_from_encounter,
			NEW.fk_health_issue,
			_identity_from_issue
		;
		return NULL;
	end if;

	return NEW;

end;';


create trigger tr_sanity_check_enc_vs_issue_on_epi
	before insert or update
	on clin.episode
	for each row
		execute procedure clin.trf_sanity_check_enc_vs_issue_on_epi();

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-episode-trigger_fixup.sql', '15.12');
