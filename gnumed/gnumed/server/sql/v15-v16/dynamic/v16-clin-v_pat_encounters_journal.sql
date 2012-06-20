-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_encounters_journal as
select
	cenc.fk_patient
		as pk_patient,
	cenc.modified_when
		as modified_when,
	-- FIXME: or last_affirmed ?
	cenc.started
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cenc.modified_by),
		'<' || cenc.modified_by || '>'
	) 	as modified_by,
	null::text
		as soap_cat,
	_('Encounter') || ': '
			|| (select _(description) from clin.encounter_type where pk = cenc.fk_type)
			|| to_char(cenc.started::timestamp with time zone, ' YYYY-MM-DD HH24:MI')
			|| to_char(cenc.last_affirmed::timestamp with time zone, ' - HH24:MI')
			|| coalesce(E'\n ' || _('RFE') || ': ' || cenc.reason_for_encounter, '')
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
							c_lc2r.fk_item = cenc.pk
						),
						'; '
					) || ';'
				),
				''
			)
			|| coalesce(E'\n ' || _('AOE') || ': ' || cenc.assessment_of_encounter, '')
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
							c_lc2a.fk_item = cenc.pk
						),
						'; '
					) || ';'
				),
				''
			)
		as narrative,
	cenc.pk
		as pk_encounter,
	-1	as pk_episode,
	-1	as pk_health_issue,
	cenc.pk
		as src_pk,
	'clin.encounter'::text as src_table,
	cenc.row_version
from
	clin.encounter cenc
;


grant select on clin.v_pat_encounters_journal TO GROUP "gm-doctors";


select i18n.upd_tx('de', 'Encounter', 'Kontakt');
select i18n.upd_tx('de', 'RFE', 'BU');
select i18n.upd_tx('de', 'AOE', 'BE');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_pat_encounters_journal.sql', 'v16');

-- ==============================================================
