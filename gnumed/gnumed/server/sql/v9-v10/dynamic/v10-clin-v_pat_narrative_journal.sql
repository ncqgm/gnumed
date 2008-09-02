-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_pat_narrative_journal.sql,v 1.1 2008-09-02 15:41:21 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_narrative_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_narrative_journal as
select
	(select fk_patient from clin.encounter where pk = cn.fk_encounter)
		as pk_patient,
	cn.modified_when
		as modified_when,
	cn.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cn.modified_by),
		'<' || cn.modified_by || '>'
	)
		as modified_by,
	cn.soap_cat
		as soap_cat,
	cn.narrative
		as narrative,
	cn.fk_encounter
		as pk_encounter,
	cn.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = cn.fk_episode)
		as pk_health_issue,
	cn.pk as src_pk,
	'clin.clin_narrative'::text as src_table
from
	clin.clin_narrative cn
;


grant select on clin.v_pat_narrative_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_pat_narrative_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_pat_narrative_journal.sql,v $
-- Revision 1.1  2008-09-02 15:41:21  ncq
-- - new
--
--
