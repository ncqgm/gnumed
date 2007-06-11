-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - upgrade blobs.v_doc_med
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-v_doc_med.sql,v 1.1 2007-06-11 18:41:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_med cascade;
\set ON_ERROR_STOP 1


create view blobs.v_doc_med as
select
	dm.fk_identity as pk_patient,
	dm.pk as pk_doc,
	dm.date as date,
	vdt.type as type,
	vdt.l10n_type as l10n_type,
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
	blobs.v_doc_type vdt,
	clin.episode cle
where
	vdt.pk_doc_type = dm.fk_type and
	cle.pk = dm.fk_episode
;

-- --------------------------------------------------------------
GRANT SELECT ON blobs.v_doc_med TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: blobs-v_doc_med.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: blobs-v_doc_med.sql,v $
-- Revision 1.1  2007-06-11 18:41:31  ncq
-- - new
--
-- Revision 1.3  2006/10/24 13:10:04  ncq
-- - type -> fk_type
--
-- Revision 1.2  2006/09/28 14:40:37  ncq
-- - add index on fk_patient
--
-- Revision 1.1  2006/09/25 10:55:01  ncq
-- - added here
--
-- Revision 1.1  2006/09/16 21:45:14  ncq
-- - add PKs for narrative search
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
