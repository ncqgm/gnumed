-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_vaccinations_journal cascade;


create view clin.v_vaccinations_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_vacc.modified_when
		as modified_when,
	c_vacc.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_vacc.modified_by),
		'<' || c_vacc.modified_by || '>'
	)
		as modified_by,
	c_vacc.soap_cat
		as soap_cat,

	(_('Vaccination') || ': '
		|| r_dp.description || ' '
		|| '[' || c_vacc.batch_no || ']'
		|| coalesce(' (' || c_vacc.site || ')', '')
		|| coalesce(E'\n' || _('Reaction') || ': ' || c_vacc.reaction, '')
		|| coalesce(E'\n' || _('Comment') || ': ' || c_vacc.narrative, '')
		|| coalesce (
			(
				E'\n' || _('Indications') || ': '
				|| array_to_string ((
					select
						array_agg(_(r_s.atc || '-target'))
		 			from
								ref.lnk_dose2drug r_ld2d
									inner join ref.dose r_d on (r_d.pk = r_ld2d.fk_dose)
										inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
					where
						r_ld2d.fk_drug_product = r_dp.pk
					),
					' / '
				)
			),
			''
		)
	)
		as narrative,

	c_vacc.fk_encounter
		as pk_encounter,
	c_vacc.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = c_vacc.fk_episode)
		as pk_health_issue,
	c_vacc.pk
		as src_pk,
	'clin.vaccination'::text
		as src_table,
	c_vacc.row_version
		as row_version,

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
	clin.vaccination c_vacc
		join clin.encounter c_enc on (c_enc.pk = c_vacc.fk_encounter)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		inner join clin.episode c_epi on (c_vacc.fk_episode = c_epi.pk)
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		inner join ref.vaccine r_vcine on (r_vcine.pk = c_vacc.fk_vaccine)
			inner join ref.drug_product r_dp on (r_vcine.fk_drug_product = r_dp.pk)
;


comment on view clin.v_vaccinations_journal is
	'Vaccination data denormalized for the EMR journal.';


grant select on clin.v_vaccinations_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_vaccinations_journal.sql', '22.0');
