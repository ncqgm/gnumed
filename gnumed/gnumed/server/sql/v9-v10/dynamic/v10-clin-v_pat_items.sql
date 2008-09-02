-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_pat_items.sql,v 1.1 2008-09-02 15:41:21 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_items cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_items as
select
--	extract(epoch from cri.clin_when) as age,
	cri.modified_when as modified_when,
	cri.modified_by as modified_by,
	cri.clin_when as clin_when,
	case cri.row_version
		when 0 then false
		else true
	end as is_modified,
	vpep.pk_patient as pk_patient,
	cri.pk_item as pk_item,
	cri.fk_encounter as pk_encounter,
	cri.fk_episode as pk_episode,
	vpep.pk_health_issue as pk_health_issue,
	cri.soap_cat as soap_cat,
	cri.narrative as narrative,
	pgc.relname as src_table
from
	clin.clin_root_item cri,
	clin.v_pat_episodes vpep,
	pg_class pgc
where
	vpep.pk_episode = cri.fk_episode
		and
	cri.tableoid = pgc.oid
;


grant select on clin.v_pat_items TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_pat_items.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_pat_items.sql,v $
-- Revision 1.1  2008-09-02 15:41:21  ncq
-- - new
--
--
