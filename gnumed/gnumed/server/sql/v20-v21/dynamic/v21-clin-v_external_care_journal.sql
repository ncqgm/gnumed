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
drop view if exists clin.v_external_care_journal cascade;

create view clin.v_external_care_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_ec.modified_when
		as modified_when,
	c_ec.modified_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_ec.modified_by),
		'<' || c_ec.modified_by || '>'
	)
		as modified_by,
	's'::text
		as soap_cat,
	_('External care')
		|| coalesce(' ' || _('by') || ' ' || c_ec.provider, '')
		|| ' @ ' || d_ou.description || ' ' || _('of') || ' ' || d_o.description || E'\n'
		|| _('Issue:') || ' ' || coalesce(c_hi.description, c_ec.issue) || E'\n'
		|| coalesce(_('Comment:') || ' ' || c_ec.comment, '')
		as narrative,
	c_ec.fk_encounter
		as pk_encounter,
	NULL::integer
		as pk_episode,
	c_ec.fk_health_issue
		as pk_health_issue,
	c_ec.pk
		as src_pk,
	'clin.external_care'::text
		as src_table,
	c_ec.row_version
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
	null::text
		as episode,
	null::boolean
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
	clin.external_care c_ec
		inner join clin.encounter c_enc on (c_ec.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		left join clin.health_issue c_hi on (c_ec.fk_health_issue = c_hi.pk)
		left join dem.org_unit d_ou on (c_ec.fk_org_unit = d_ou.pk)
			left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;


revoke all on clin.v_external_care_journal from public;
grant select on clin.v_external_care_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_external_care_journal.sql', '21.0');
