-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_pat_narrative.sql,v 1.1 2008-09-02 18:56:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_narrative cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_narrative as
select
	(select fk_patient from clin.encounter where pk = cn.fk_encounter) as pk_patient,
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
	cn.xmin as xmin_clin_narrative
from
	clin.clin_narrative cn
;


comment on view clin.v_pat_narrative is
	'patient narrative aggregated from all clin_root_item child tables;
	 the narrative is unprocessed, denormalized context using v_pat_items is added';


grant select on clin.v_pat_narrative to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSile:asfdasd zzz-templatesdf.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_pat_narrative.sql,v $
-- Revision 1.1  2008-09-02 18:56:39  ncq
-- - new
--
--