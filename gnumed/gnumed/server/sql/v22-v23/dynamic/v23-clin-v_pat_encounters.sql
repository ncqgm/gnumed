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
drop view if exists clin.v_pat_encounters cascade;


create view clin.v_pat_encounters as
select
	c_enc.pk as pk_encounter,
	c_enc.fk_patient as pk_patient,
	c_enc.started as started,
	c_et.description as type,
--	_(c_et.description)
	coalesce(tx_exact_lang.trans, tx_reduced_lang.trans, c_et.description)
		as l10n_type,
	c_enc.reason_for_encounter as reason_for_encounter,
	c_enc.assessment_of_encounter as assessment_of_encounter,
	c_enc.last_affirmed as last_affirmed,
	c_enc.source_time_zone,
	(select started at time zone (
		select source_time_zone
		from clin.encounter c_enc1
		where c_enc1.pk = c_enc.pk
	)) as started_original_tz,
	(select last_affirmed at time zone (
		select source_time_zone
		from clin.encounter c_enc1
		where c_enc1.pk = c_enc.pk
	)) as last_affirmed_original_tz,
	coalesce(d_ou.description, '?')
		as praxis_branch,
	coalesce(d_o.description, '?')
		as praxis,
	c_enc.fk_location
		as pk_org_unit,
	d_ou.fk_org
		as pk_org,
	d_ou.fk_category
		as pk_unit_type,
	d_o.fk_category
		as pk_org_type,
	c_enc.fk_type as pk_type,
	c_enc.xmin
		as xmin_encounter,
	-- needed by Jerzy's enhancements:
	c_enc.row_version,
	c_enc.pk_audit,
	c_enc.modified_when,
	c_enc.modified_by
		as modified_by_raw,
	coalesce (
		(select staff.short_alias from dem.staff where staff.db_user = c_enc.modified_by),
		'<'::text || c_enc.modified_by::text || '>'::text
	) AS modified_by
from
	clin.encounter c_enc
		left join clin.encounter_type c_et on (c_enc.fk_type = c_et.pk)
			LEFT JOIN i18n.translations tx_exact_lang ON
				tx_exact_lang.orig = c_et.description
					AND
				tx_exact_lang.lang = (SELECT lang FROM i18n.curr_lang WHERE db_user = current_user)
			LEFT JOIN i18n.translations tx_reduced_lang ON
				tx_reduced_lang.orig = c_et.description
					AND
				tx_reduced_lang.lang = (SELECT regexp_replace(lang, '_.*$', '') FROM i18n.curr_lang WHERE db_user = current_user)
		left join dem.org_unit d_ou on (c_enc.fk_location = d_ou.pk)
			left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;


comment on view clin.v_pat_encounters is
	'Details on encounters.';


grant select on clin.v_pat_encounters TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_pat_encounters.sql', '23.0');
