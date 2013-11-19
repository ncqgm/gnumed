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
update clin.encounter set
	fk_location = NULL
where
	fk_location = -1
;


\unset ON_ERROR_STOP
alter table clin.encounter drop constraint "encounter_fk_location_fkey";
\set ON_ERROR_STOP 1

alter table clin.encounter add foreign key (fk_location)
	references dem.org_unit(pk)
	on update cascade
	on delete restrict
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_encounters as
select
	c_enc.pk as pk_encounter,
	c_enc.fk_patient as pk_patient,
	c_enc.started as started,
	c_et.description as type,
	_(c_et.description) as l10n_type,
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
	coalesce (
		(select array_agg(c_lc2r.fk_generic_code) from clin.lnk_code2rfe c_lc2r where c_lc2r.fk_item = c_enc.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes_rfe,
	coalesce (
		(select array_agg(c_lc2a.fk_generic_code) from clin.lnk_code2aoe c_lc2a where c_lc2a.fk_item = c_enc.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes_aoe,
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
			left join dem.org_unit d_ou on (c_enc.fk_location = d_ou.pk)
				left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;


comment on view clin.v_pat_encounters is
	'Details on encounters.';


grant select on clin.v_pat_encounters TO GROUP "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters_journal cascade;
\set ON_ERROR_STOP 1


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
	-1	as pk_episode,
	-1	as pk_health_issue,
	c_enc.pk
		as src_pk,
	'clin.encounter'::text as src_table,
	c_enc.row_version
from
	clin.encounter c_enc
		left join dem.org_unit d_ou on (c_enc.fk_location = d_ou.pk)
			left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;


grant select on clin.v_pat_encounters_journal TO GROUP "gm-doctors";


select i18n.upd_tx('de', 'branch', 'Zweigstelle');
select i18n.upd_tx('de', 'of', 'von');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-encounter-dynamic.sql', '19.0');
