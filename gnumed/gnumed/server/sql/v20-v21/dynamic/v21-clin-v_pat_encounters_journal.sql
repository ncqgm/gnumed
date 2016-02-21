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
drop view if exists clin.v_pat_encounters_journal cascade;


create view clin.v_pat_encounters_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_enc.modified_when
		as modified_when,
	-- FIXME: or last_affirmed ?
	c_enc.started
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_enc.modified_by),
		'<' || c_enc.modified_by || '>'
	) 	as modified_by,
	null::text
		as soap_cat,
	_('Encounter') || ': '
			|| (select _(description) from clin.encounter_type where pk = c_enc.fk_type)
			|| to_char(c_enc.started::timestamp with time zone, ' YYYY-MM-DD HH24:MI')
			|| to_char(c_enc.last_affirmed::timestamp with time zone, ' - HH24:MI')
			|| coalesce(E'\n @ ' || _('branch') || ' "' || d_ou.description || '" ' || _('of') || ' "' || d_o.description || '"', '')
			|| coalesce(E'\n ' || _('RFE') || ': ' || c_enc.reason_for_encounter, '')
			|| coalesce ((
					E'\n' || array_to_string (
						(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
						 from
							clin.lnk_code2rfe c_lc2r
								inner join
							ref.coding_system_root r_csr on c_lc2r.fk_generic_code = r_csr.pk_coding_system
								inner join
							ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
						where
							c_lc2r.fk_item = c_enc.pk
						),
						'; '
					) || ';'
				),
				''
			)
			|| coalesce(E'\n ' || _('AOE') || ': ' || c_enc.assessment_of_encounter, '')
			|| coalesce ((
					E'\n' || array_to_string (
						(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
						 from
							clin.lnk_code2aoe c_lc2a
								inner join
							ref.coding_system_root r_csr on c_lc2a.fk_generic_code = r_csr.pk_coding_system
								inner join
							ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
						where
							c_lc2a.fk_item = c_enc.pk
						),
						'; '
					) || ';'
				),
				''
			)
		as narrative,
	c_enc.pk
		as pk_encounter,
	NULL::integer
		as pk_episode,
	NULL::integer
		as pk_health_issue,
	c_enc.pk
		as src_pk,
	'clin.encounter'::text as src_table,
	c_enc.row_version,

	-- issue
	NULL::text
		as health_issue,
	NULL::text
		as issue_laterality,
	NULL::boolean
		as issue_active,
	NULL::boolean
		as issue_clinically_relevant,
	NULL::boolean
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
	clin.encounter c_enc
		inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
			left join dem.org_unit d_ou on (c_enc.fk_location = d_ou.pk)
				left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;


grant select on clin.v_pat_encounters_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_pat_encounters_journal.sql', '21.0');
