-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - add view blobs.v_doc_desc
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-v_doc_desc.sql,v 1.1 2006-09-16 21:43:37 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_desc cascade;
\set ON_ERROR_STOP 1


create view blobs.v_doc_desc as
select
	vdm.pk_patient as pk_patient,
	dd.doc_id as pk_doc,
	dd.text as description,
	vdm.pk_encounter as pk_encounter,
	vdm.pk_episode as pk_episode,
	vdm.pk_health_issue as pk_health_issue,
	dd.pk as pk_doc_desc
from
	blobs.doc_desc dd,
	blobs.v_doc_med vdm
where
	dd.doc_id = vdm.pk_doc
;


comment on view blobs.v_doc_desc is
	'aggregates some data document descriptions';

-- --------------------------------------------------------------
grant select on blobs.v_doc_desc to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-v_doc_desc.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: blobs-v_doc_desc.sql,v $
-- Revision 1.1  2006-09-16 21:43:37  ncq
-- - create view
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
