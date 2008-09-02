-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-blobs-v_doc_med_journal.sql,v 1.1 2008-09-02 15:41:19 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_med_journal cascade;
\set ON_ERROR_STOP 1


create view blobs.v_doc_med_journal as
select
	(select fk_patient from clin.encounter where pk = dm.fk_encounter)
		as pk_patient,
	dm.modified_when
		as modified_when,
	dm.date
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = dm.modified_by),
		'<' || dm.modified_by || '>'
	)
		as modified_by,
	null::text
		as soap_cat,
	_('Document') || ': ' || _(dt.name)
		|| coalesce(' "' || dm.ext_ref || '" (', ' (')
		|| to_char(dm.date, 'YYYY-MM-DD HH24:MI') || ')'
		|| coalesce(E'\n ' || dm.comment, '')
		as narrative,
	dm.fk_encounter
		as pk_encounter,
	dm.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = dm.fk_episode)
		as pk_health_issue,
	dm.pk
		as src_pk,
	'blobs.doc_med'::text
		as src_table
from
	blobs.doc_med dm,
	blobs.doc_type dt
where
	dt.pk = dm.fk_type
;


grant select on blobs.v_doc_med_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-blobs-v_doc_med_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-blobs-v_doc_med_journal.sql,v $
-- Revision 1.1  2008-09-02 15:41:19  ncq
-- - new
--
--
