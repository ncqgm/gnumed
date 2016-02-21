-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_health_issues_journal cascade;


create view clin.v_health_issues_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_hi.modified_when
		as modified_when,
	coalesce (
		(select dem.identity.dob + c_hi.age_noted
		 from dem.identity
		 where pk = (select fk_patient from clin.encounter where pk = c_hi.fk_encounter)
		),
		c_enc.started
	)
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_hi.modified_by),
		'<' || c_hi.modified_by || '>'
	) 	as modified_by,
	'a'::text
		as soap_cat,
	_('Health Issue') || ' ('
			|| case when c_hi.is_active
				then _('active')
				else _('inactive')
			   end
			|| ', '
			|| case when c_hi.clinically_relevant
				then _('clinically relevant')
				else _('clinically not relevant')
			   end
			|| coalesce((', ' || c_hi.diagnostic_certainty_classification), '')
			|| '): '
			|| c_hi.description
			|| coalesce((E';\n' || _('noted at age') || ': ' || c_hi.age_noted::text || E';\n'), E';\n')
			|| coalesce((_('Laterality') || ': ' || c_hi.laterality || ' / '), '')
			|| case when c_hi.is_confidential
				then _('confidential') || ' / ' else ''
			   end
			|| case when c_hi.is_cause_of_death
				then _('cause of death') else ''
			   end
			|| coalesce((E';\n' || _('Summary') || E':\n' || c_hi.summary), E'')
			|| coalesce ((
					E';\n' || array_to_string (
						(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
						 from
						 	clin.lnk_code2h_issue c_lc2h
						 		inner join
							ref.coding_system_root r_csr on c_lc2h.fk_generic_code = r_csr.pk_coding_system
								inner join
							ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
						where
							c_lc2h.fk_item = c_hi.pk
						),
						'; '
					) || ';'
				),
				''
			)
		as narrative,
	c_hi.fk_encounter
		as pk_encounter,
	NULL::integer
		as pk_episode,
	c_hi.pk
		as pk_health_issue,
	c_hi.pk
		as src_pk,
	'clin.health_issue'::text
		as src_table,
	c_hi.row_version,

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
	NULL::text
		as episode,
	NULL::boolean
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
	clin.health_issue c_hi
		inner join clin.encounter c_enc on c_hi.fk_encounter = c_enc.pk
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
;


grant select on clin.v_health_issues_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_health_issues_journal.sql', '21.0');
