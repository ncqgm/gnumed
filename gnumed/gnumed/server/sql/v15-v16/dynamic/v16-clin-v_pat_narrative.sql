-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_narrative cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_narrative as
select
	cenc.fk_patient
		as pk_patient,
	cn.clin_when as date,
	coalesce (
		(select short_alias from dem.staff where db_user = cn.modified_by),
		'<' || cn.modified_by || '>'
	) as provider,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.pk_item as pk_item,
	cn.pk as pk_narrative,
	(select fk_health_issue from clin.episode where pk = cn.fk_episode) as pk_health_issue,
	cn.fk_episode as pk_episode,
	cn.fk_encounter as pk_encounter,
	cn.xmin as xmin_clin_narrative,
	cn.modified_when,
	cn.row_version,
	coalesce (
		(select array_agg(c_lc2n.fk_generic_code) from clin.lnk_code2narrative c_lc2n where c_lc2n.fk_item = cn.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes
from
	clin.clin_narrative cn
		inner join clin.encounter cenc on (cn.fk_encounter = cenc.pk)
;


comment on view clin.v_pat_narrative is
	'patient narrative aggregated from all clin_root_item child tables;
	 the narrative is unprocessed, denormalized context using v_pat_items is added';


grant select on clin.v_pat_narrative to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_pat_narrative.sql', '16.0');

-- ==============================================================
