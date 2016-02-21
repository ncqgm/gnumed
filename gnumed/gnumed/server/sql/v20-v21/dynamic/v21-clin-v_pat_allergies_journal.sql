-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_allergies_journal cascade;


create view clin.v_pat_allergies_journal as

select
	c_enc.fk_patient
		as pk_patient,
	c_all.modified_when
		as modified_when,
	c_all.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_all.modified_by),
		'<' || c_all.modified_by || '>'
	)
		as modified_by,
	c_all.soap_cat
		as soap_cat,
	_('Allergy') || ' (' || _(c_at.value) || '): ' || coalesce(c_all.narrative, '') || E'\n'
		|| _('substance') || ': ' || c_all.substance || '; '
		|| coalesce((_('allergene') || ': ' || c_all.allergene || '; '), '')
		|| coalesce((_('generic')   || ': ' || c_all.generics || '; '), '')
		|| coalesce((_('ATC code')  || ': ' || c_all.atc_code || '; '), '')
		as narrative,
	c_all.fk_encounter
		as pk_encounter,
	c_all.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_all.pk
		as src_pk,
	'clin.allergy'::text
		as src_table,
	c_all.row_version,

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
	clin.allergy c_all
		inner join clin._enum_allergy_type c_at on (c_all.fk_type = c_at.pk)
			inner join clin.encounter c_enc on (c_all.fk_encounter = c_enc.pk)
				inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
					inner join clin.episode c_epi on (c_all.fk_episode = c_epi.pk)
						left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
;


grant select on clin.v_pat_allergies_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_pat_allergies_journal.sql', '21.0');
