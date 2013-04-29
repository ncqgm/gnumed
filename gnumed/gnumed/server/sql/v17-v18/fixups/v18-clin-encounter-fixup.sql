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
-- update .last_affirmed if < .started
update clin.encounter set
	last_affirmed = started,
	assessment_of_encounter = coalesce(assessment_of_encounter, '')
		|| ' [previous end of encounter (.last_affirmed=' || last_affirmed
		|| ') auto-set to start of encounter (.started=' || started
		|| ') because the encounter ended before it started]'
where
	last_affirmed < started
;

-- add constraint
\unset ON_ERROR_STOP
alter table clin.encounter drop constraint clin_enc_sane_duration cascade;
\set ON_ERROR_STOP 1


alter table clin.encounter
	add constraint clin_enc_sane_duration
		check (last_affirmed >= started);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-clin-encounter-fixup.sql', '18.4');
