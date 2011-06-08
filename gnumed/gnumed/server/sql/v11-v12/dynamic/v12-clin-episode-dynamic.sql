-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-episode-dynamic.sql,v 1.5 2009-12-03 17:52:12 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .description
\unset ON_ERROR_STOP
alter table clin.episode drop constraint sane_description cascade;
\set ON_ERROR_STOP 1


alter table clin.episode
	add constraint sane_description
		check(gm.is_null_or_blank_string(description) is False);


\unset ON_ERROR_STOP
alter table clin.episode drop constraint episode_description_check cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .diagnostic_certainty_classification
comment on column clin.episode.diagnostic_certainty_classification is
'The certainty at which this problem is believed to be a diagnosis:

A: sign (Symptom)
B: cluster of signs (Symptomkomplex)
C: syndromic diagnosis (Bild einer Diagnose)
D: proven diagnosis (diagnostisch gesichert)'
;


alter table clin.episode
	add constraint valid_diagnostic_certainty_classification
		check (diagnostic_certainty_classification in ('A', 'B', 'C', 'D', NULL));


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
			_identity_from_episode
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
select gm.log_script_insertion('$RCSfile: v12-clin-episode-dynamic.sql,v $', '$Revision: 1.5 $');

-- ==============================================================
-- $Log: v12-clin-episode-dynamic.sql,v $
-- Revision 1.5  2009-12-03 17:52:12  ncq
-- - improved constraints
--
-- Revision 1.4  2009/11/06 15:34:01  ncq
-- - better formatting
--
-- Revision 1.3  2009/10/29 17:25:51  ncq
-- - trigger to sanity check patient behind issue vs encounter
--
-- Revision 1.2  2009/09/01 22:43:14  ncq
-- - diagnostic-certainty -> *-classification
--
-- Revision 1.1  2009/08/28 12:45:26  ncq
-- - add diagnostic certainty
--
--
