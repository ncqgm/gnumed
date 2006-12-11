-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: clin-v_pat_narrative.sql,v 1.1 2006-12-11 16:59:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_narrative cascade;
\set ON_ERROR_STOP 1

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

-- ==============================================================
-- $Log: clin-v_pat_narrative.sql,v $
-- Revision 1.1  2006-12-11 16:59:47  ncq
-- - use dem.v_staff -> dem.staff in provider resolution
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
