-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-clin-v_pat_items.sql,v 1.2 2009-11-08 20:52:17 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_items cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_items as
select
	cri.modified_when as modified_when,
	cri.modified_by as modified_by,
	cri.clin_when as clin_when,
	case cri.row_version
		when 0 then false
		else true
	end as is_modified,
	cenc.fk_patient as pk_patient,
	cri.pk_item as pk_item,
	cri.fk_encounter as pk_encounter,
	cri.fk_episode as pk_episode,
	cepi.fk_health_issue as pk_health_issue,
	cri.soap_cat as soap_cat,
	cri.narrative as narrative,
	pgn.nspname || '.' || pgc.relname as src_table
from
	clin.clin_root_item cri,
	clin.encounter cenc,
	clin.episode cepi,
	pg_class pgc left join pg_namespace pgn on (pgc.relnamespace = pgn.oid)
where
	cri.fk_encounter = cenc.pk
		and
	cri.fk_episode = cepi.pk
		and
	cri.tableoid = pgc.oid
;


grant select on clin.v_pat_items TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-v_pat_items.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-clin-v_pat_items.sql,v $
-- Revision 1.2  2009-11-08 20:52:17  ncq
-- - incluce schema in src_table
--
-- Revision 1.1  2009/09/01 22:12:47  ncq
-- - new
--
--