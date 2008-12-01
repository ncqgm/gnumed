-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-blobs-v_doc_desc.sql,v 1.1 2008-12-01 21:46:33 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_desc cascade;
\set ON_ERROR_STOP 1


create view blobs.v_doc_desc as
select
	vdm.pk_patient as pk_patient,
	dd.fk_doc as pk_doc,
	dd.text as description,
	vdm.pk_encounter as pk_encounter,
	vdm.pk_episode as pk_episode,
	vdm.pk_health_issue as pk_health_issue,
	dd.pk as pk_doc_desc
from
	blobs.doc_desc dd,
	blobs.v_doc_med vdm
where
	dd.fk_doc = vdm.pk_doc
;


comment on view blobs.v_doc_desc is
	'aggregates some document data descriptions';

-- --------------------------------------------------------------
grant select on blobs.v_doc_desc to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-blobs-v_doc_desc.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-blobs-v_doc_desc.sql,v $
-- Revision 1.1  2008-12-01 21:46:33  ncq
-- - new
--
--