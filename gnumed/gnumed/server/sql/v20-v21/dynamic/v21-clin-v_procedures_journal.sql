-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_procedures_at_hospital_journal cascade;

create view clin.v_procedures_at_hospital_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_pr.modified_when
		as modified_when,
	c_pr.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_pr.modified_by),
		'<' || c_pr.modified_by || '>'
	)
		as modified_by,
	c_pr.soap_cat
		as soap_cat,
	_('Procedure') || ' "' || c_pr.narrative	|| '"'
		|| ' ('
			|| d_ou.description || ' @ ' || d_o.description
			|| coalesce (
				(', ' || _('until') || ' ' || to_char(c_pr.clin_end, 'YYYY Mon DD')),
				case
					when (c_pr.is_ongoing is True)
						then ', ' || _('ongoing')
						else ''
				end
			)
		|| E')'
		|| coalesce ((
				E'\n' || array_to_string (
					(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
					 from
					 	clin.lnk_code2procedure c_lc2p
					 		inner join
						ref.coding_system_root r_csr on c_lc2p.fk_generic_code = r_csr.pk_coding_system
							inner join
						ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
					where
						c_lc2p.fk_item = c_pr.pk
					),
					'; '
				) || ';'
			),
			''
		)
		as narrative,
	c_pr.fk_encounter
		as pk_encounter,
	c_pr.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_pr.pk
		as src_pk,
	'clin.procedure'::text
		as src_table,
	c_pr.row_version,

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
	clin.procedure c_pr
		inner join clin.encounter c_enc on c_pr.fk_encounter = c_enc.pk
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		inner join clin.episode c_epi on c_pr.fk_episode = c_epi.pk
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		left join clin.hospital_stay c_hs on c_pr.fk_hospital_stay = c_hs.pk
			left join dem.org_unit d_ou on c_hs.fk_org_unit = d_ou.pk
				left join dem.org d_o on d_ou.fk_org = d_o.pk
where
	c_pr.fk_hospital_stay is not null
;


grant select on clin.v_procedures_at_hospital_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_procedures_not_at_hospital_journal cascade;

create view clin.v_procedures_not_at_hospital_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_pr.modified_when
		as modified_when,
	c_pr.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_pr.modified_by),
		'<' || c_pr.modified_by || '>'
	)
		as modified_by,
	c_pr.soap_cat
		as soap_cat,
	_('Procedure') || ' "' || c_pr.narrative	|| '"'
		|| ' ('
			|| d_ou.description || ' @ ' || d_o.description
			|| coalesce (
				(', ' || _('until') || ' ' || to_char(c_pr.clin_end, 'YYYY Mon DD')),
				case
					when (c_pr.is_ongoing is True)
						then ', ' || _('ongoing')
						else ''
				end
			)
		|| E')'
		|| coalesce ((
				E'\n' || array_to_string (
					(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
					 from
					 	clin.lnk_code2procedure c_lc2p
					 		inner join
						ref.coding_system_root r_csr on c_lc2p.fk_generic_code = r_csr.pk_coding_system
							inner join
						ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
					where
						c_lc2p.fk_item = c_pr.pk
					),
					'; '
				) || ';'
			),
			''
		)
		as narrative,
	c_pr.fk_encounter
		as pk_encounter,
	c_pr.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_pr.pk
		as src_pk,
	'clin.procedure'::text
		as src_table,
	c_pr.row_version,

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
	clin.procedure c_pr
		inner join clin.encounter c_enc on c_pr.fk_encounter = c_enc.pk
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		inner join clin.episode c_epi on c_pr.fk_episode = c_epi.pk
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		left join dem.org_unit d_ou on c_pr.fk_org_unit = d_ou.pk
			left join dem.org d_o on d_ou.fk_org = d_o.pk
where
	c_pr.fk_hospital_stay is null
;


grant select on clin.v_procedures_not_at_hospital_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_procedures_journal cascade;

create view clin.v_procedures_journal as

	select * from clin.v_procedures_at_hospital_journal
		union all
	select * from clin.v_procedures_not_at_hospital_journal
;


grant select on clin.v_procedures_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_procedures_journal.sql', '21.0');
