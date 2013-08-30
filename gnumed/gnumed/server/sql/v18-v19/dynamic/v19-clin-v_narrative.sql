-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_narrative cascade;
drop view if exists clin.v_narrative cascade;


create view clin.v_narrative as
select
	c_enc.fk_patient
		as pk_patient,
	c_n.clin_when as date,
	coalesce (
		(select short_alias from dem.staff where db_user = c_n.modified_by),
		'<' || c_n.modified_by || '>'
	) as modified_by,
	c_n.soap_cat as soap_cat,
	c_n.narrative as narrative,
	c_epi.description
		as episode,
	c_hi.description
		as health_issue,
	c_n.pk_item as pk_item,
	c_n.pk
		as pk_narrative,
	c_epi.fk_health_issue AS pk_health_issue,
	c_n.fk_episode as pk_episode,
	c_n.fk_encounter as pk_encounter,
	c_n.xmin as xmin_clin_narrative,
	c_n.modified_when,
	c_n.row_version,
	c_n.pk_audit,
	c_n.modified_by as modified_by_raw,
	coalesce (
		(select array_agg(c_lc2n.fk_generic_code) from clin.lnk_code2narrative c_lc2n where c_lc2n.fk_item = c_n.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes
from
	clin.clin_narrative c_n
		left join clin.encounter c_enc on c_n.fk_encounter = c_enc.pk
			left join clin.episode c_epi on c_n.fk_episode = c_epi.pk
				left join clin.health_issue c_hi on c_epi.fk_health_issue = c_hi.pk
;


comment on view clin.v_narrative is
	'patient narrative with denormalized context added';


grant select on clin.v_narrative to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-v_narrative.sql', '19.0');
