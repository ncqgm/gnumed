-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: 
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_narrative cascade;

create view clin.v_pat_narrative as
select
	vpi.pk_patient as pk_patient,
	cn.clin_when as date,
	coalesce (
		(select short_alias from dem.staff where db_user = cn.modified_by),
		'<' || cn.modified_by || '>'
	) as provider,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.pk_item as pk_item,
	cn.pk as pk_narrative,
	vpi.pk_health_issue as pk_health_issue,
	cn.fk_episode as pk_episode,
	cn.fk_encounter as pk_encounter,
	cn.xmin as xmin_clin_narrative
from
	clin.clin_narrative cn,
	clin.v_pat_items vpi
where
	cn.pk_item = vpi.pk_item
;

comment on view clin.v_pat_narrative is
	'patient narrative aggregated from all clin_root_item child tables;
	 the narrative is unprocessed and denormalized context using v_pat_items is added';

-- --------------------------------------------------------------
grant select on clin.v_pat_narrative to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSile:asfdasd zzz-template.sql,v $', '$Revision: 1.1 $');
