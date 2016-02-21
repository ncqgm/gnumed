-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- stays w/o discharge date
drop view if exists clin.v_hospital_stays_journal_no_discharge cascade;

create view clin.v_hospital_stays_journal_no_discharge as
	select
		c_enc.fk_patient
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('hospital stay') || E'\n'
			|| ' ' || _('admitted') || ': ' || to_char(clin_when, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('hospital') || ': "' || d_ou.description || ' @ ' || d_o.description || '"'
			|| coalesce(E'\n ' || c_hs.narrative, '')
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
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
		clin.hospital_stay c_hs
			inner join clin.encounter c_enc on (c_hs.fk_encounter = c_enc.pk)
				inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
					inner join clin.episode c_epi on (c_hs.fk_episode = c_epi.pk)
						left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
							left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
								left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		c_hs.discharge is NULL
;


grant select on clin.v_hospital_stays_journal_no_discharge to group "gm-doctors";

-- --------------------------------------------------------------
-- one-day stays
drop view if exists clin.v_hospital_stays_journal_one_day cascade;

create view clin.v_hospital_stays_journal_one_day as
	select
		c_enc.fk_patient
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('hospital stay') || E'\n'
			|| ' ' || _('admitted/discharged') || ': ' || to_char(clin_when, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('hospital') || ': "' || d_ou.description || ' @ ' || d_o.description || '"' || E'\n'
			|| coalesce(E'\n ' || c_hs.narrative, '')
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
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
		clin.hospital_stay c_hs
			inner join clin.encounter c_enc on (c_hs.fk_encounter = c_enc.pk)
				inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
					inner join clin.episode c_epi on (c_hs.fk_episode = c_epi.pk)
						left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
							left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
								left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is not NULL)
			and
		(to_char(c_hs.clin_when, 'YYYYMMDD') = to_char(c_hs.discharge, 'YYYYMMDD'))
;


grant select on clin.v_hospital_stays_journal_one_day to group "gm-doctors";

-- --------------------------------------------------------------
-- several days stays: admission
drop view if exists clin.v_hospital_stays_journal_multi_day_adm cascade;

create view clin.v_hospital_stays_journal_multi_day_adm as
	select
		c_enc.fk_patient
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('hospital stay') || E'\n'
			|| ' ' || _('admitted') || ': ' || to_char(clin_when, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('discharged') || ': ' || to_char(discharge, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('hospital') || ': "' || d_ou.description || ' @ ' || d_o.description || '"' || E'\n'
			|| coalesce(E'\n ' || c_hs.narrative, '')
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
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
		clin.hospital_stay c_hs
			inner join clin.encounter c_enc on (c_hs.fk_encounter = c_enc.pk)
				inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
					inner join clin.episode c_epi on (c_hs.fk_episode = c_epi.pk)
						left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
							left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
								left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is not NULL)
			and
		(to_char(c_hs.clin_when, 'YYYYMMDD') != to_char(c_hs.discharge, 'YYYYMMDD'))
;


grant select on clin.v_hospital_stays_journal_multi_day_adm to group "gm-doctors";

-- --------------------------------------------------------------
-- several days stays: discharge
drop view if exists clin.v_hospital_stays_journal_multi_day_dis cascade;

create view clin.v_hospital_stays_journal_multi_day_dis as
	select
		c_enc.fk_patient
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.discharge
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('discharged from') || ' "' || d_ou.description || ' @ ' || d_o.description || '"'
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
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
		clin.hospital_stay c_hs
			inner join clin.encounter c_enc on (c_hs.fk_encounter = c_enc.pk)
				inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
					inner join clin.episode c_epi on (c_hs.fk_episode = c_epi.pk)
						left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
							left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
								left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is not NULL)
			and
		(to_char(c_hs.clin_when, 'YYYYMMDD') != to_char(c_hs.discharge, 'YYYYMMDD'))
;


grant select on clin.v_hospital_stays_journal_multi_day_dis to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_hospital_stays_journal cascade;


create view clin.v_hospital_stays_journal as
	select * from clin.v_hospital_stays_journal_no_discharge
union all
	select * from clin.v_hospital_stays_journal_one_day
union all
	select * from clin.v_hospital_stays_journal_multi_day_adm
union all
	select * from clin.v_hospital_stays_journal_multi_day_dis
;

grant select on clin.v_hospital_stays_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_hospital_stays_journal.sql', '21.0');
