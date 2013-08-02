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
\unset ON_ERROR_STOP
drop view clin.v_pat_hospital_stays_journal cascade;
drop view clin.v_hospital_stays_journal cascade;
\set ON_ERROR_STOP 1

create view clin.v_hospital_stays_journal as
select
	(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
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
	_('hospital stay') || ': '
		|| to_char(clin_when, 'YYYY-MM-DD') || ' - '
		|| coalesce(to_char(discharge, 'YYYY-MM-DD'), '?')
		|| ' "' || d_ou.description || ' @ ' || d_o.description || '"'
		|| coalesce(' ' || c_hs.narrative, '')
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
		as row_version
from
	clin.hospital_stay c_hs
		left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
			left join dem.org d_o on (d_o.pk = d_ou.fk_org)
;


grant select on clin.v_hospital_stays_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-v_hospital_stays_journal.sql', '19.0');
