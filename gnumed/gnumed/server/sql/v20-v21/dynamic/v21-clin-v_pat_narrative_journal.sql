-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_narrative_journal cascade;


create view clin.v_pat_narrative_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_n.modified_when
		as modified_when,
	case
		-- pre-sort:
		when c_n.soap_cat in ('s','o','u') then c_enc.started
		when c_n.soap_cat is NULL then c_enc.last_affirmed
		when c_n.soap_cat in ('a','p') then c_enc.last_affirmed
	end
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_n.modified_by),
		'<' || c_n.modified_by || '>'
	)
		as modified_by,
	c_n.soap_cat
		as soap_cat,
	c_n.narrative
		as narrative,
	c_n.fk_encounter
		as pk_encounter,
	c_n.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_n.pk
		as src_pk,
	'clin.clin_narrative'::text
		as src_table,
	c_n.row_version,

	-- issue
	c_hi.description
		as health_issue,
	c_hi.laterality
		as issue_laterality,
	c_hi.is_active
		as issue_active,
	c_hi.clinically_relevant
		as issue_clinically_relevant,
	c_hi.is_confidential
		as issue_confidential,

	-- episode
	c_epi.description
		as episode,
	c_epi.is_open
		as episode_open,

	-- encounter
	c_enc.started
		as encounter_started,
	c_enc.last_affirmed
		as encounter_last_affirmed,
	c_ety.description
		as encounter_type,
	_(c_ety.description)
		as encounter_l10n_type

from
	clin.clin_narrative c_n
		inner join clin.encounter c_enc on (c_n.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
				inner join clin.episode c_epi on (c_n.fk_episode = c_epi.pk)
					left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
;


grant select on clin.v_pat_narrative_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_pat_narrative_journal.sql', '21.0');
