-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-blobs-v_doc_med.sql,v 1.2 2008-12-09 23:13:24 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_med cascade;
\set ON_ERROR_STOP 1


create view blobs.v_doc_med as
select
	(select fk_patient from clin.encounter where pk = dm.fk_encounter) as pk_patient,
	dm.pk as pk_doc,
	dm.clin_when as clin_when,
	dt.name as type,
	_(dt.name) as l10n_type,
	dm.ext_ref as ext_ref,
	cle.description as episode,
	dm.comment as comment,
	cle.is_open as episode_open,
	dm.fk_type as pk_type,
	dm.fk_encounter as pk_encounter,
	dm.fk_episode as pk_episode,
	cle.fk_health_issue as pk_health_issue,
	dm.modified_when as modified_when,
	dm.modified_by as modified_by,
	dm.xmin as xmin_doc_med
from
	blobs.doc_med dm,
	blobs.doc_type dt,
	clin.episode cle
where
	dt.pk = dm.fk_type
		and
	cle.pk = dm.fk_episode
;

-- --------------------------------------------------------------
GRANT SELECT ON blobs.v_doc_med TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-blobs-v_doc_med.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-blobs-v_doc_med.sql,v $
-- Revision 1.2  2008-12-09 23:13:24  ncq
-- - .date -> .clin_when
--
-- Revision 1.1  2008/12/01 21:46:34  ncq
-- - new
--
--