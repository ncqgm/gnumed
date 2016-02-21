-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_episodes_journal cascade;


create view clin.v_pat_episodes_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_epi.modified_when
		as modified_when,
	c_enc.started
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_epi.modified_by),
		'<' || c_epi.modified_by || '>'
	)
		as modified_by,
	'a'::text
		as soap_cat,
	_('Episode') || ' ('
		|| case when c_epi.is_open
			then _('open')
			else _('closed')
			end
		|| coalesce((', ' || c_epi.diagnostic_certainty_classification), '')
		|| '): '
		|| c_epi.description || ';'
		|| coalesce((E'\n ' || _('Synopsis') || ': ' || c_epi.summary || ';'), '')
		|| coalesce ((
				E'\n' || array_to_string (
					(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
					 from
					 	clin.lnk_code2episode c_lc2e
					 		inner join
						ref.coding_system_root r_csr on c_lc2e.fk_generic_code = r_csr.pk_coding_system
							inner join
						ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
					where
						c_lc2e.fk_item = c_epi.pk
					),
					'; '
				) || ';'
			),
			''
		)
		as narrative,
	c_epi.fk_encounter
		as pk_encounter,
	c_epi.pk
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_epi.pk
		as src_pk,
	'clin.episode'::text
		as src_table,
	c_epi.row_version,

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
	clin.episode c_epi
		inner join clin.encounter c_enc on (c_epi.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
				left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
;


grant select on clin.v_pat_episodes_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_pat_episodes_journal.sql', '21.0');
