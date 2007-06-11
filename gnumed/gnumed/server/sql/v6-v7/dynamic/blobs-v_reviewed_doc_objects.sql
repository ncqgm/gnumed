-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- What it does:
-- - upgrade blobs.v_reviewed_doc_objects
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-v_reviewed_doc_objects.sql,v 1.1 2007-06-11 18:41:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view blobs.v_reviewed_doc_objects cascade;
\set ON_ERROR_STOP 1


create view blobs.v_reviewed_doc_objects as
select
	rdo.fk_reviewed_row as pk_doc_obj,
	coalesce (
		(select short_alias from dem.staff where pk=rdo.fk_reviewer),
		'<#' || rdo.fk_reviewer || '>'
	) as reviewer,
	rdo.is_technically_abnormal as is_technically_abnormal,
	rdo.clinically_relevant as clinically_relevant,
	exists(select 1 from blobs.doc_obj where pk=rdo.fk_reviewed_row and fk_intended_reviewer=rdo.fk_reviewer)
		as is_review_by_responsible_reviewer,
	exists(select 1 from dem.staff where pk=rdo.fk_reviewer and db_user=CURRENT_USER)
		as is_your_review,
	rdo.comment,
	rdo.modified_when as reviewed_when,
	rdo.modified_by as modified_by,
	rdo.pk as pk_review_root,
	rdo.fk_reviewer as pk_reviewer,
	(select pk_patient from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_patient,
	(select pk_encounter from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_encounter,
	(select pk_episode from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_episode,
	(select pk_health_issue from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_health_issue
from
	blobs.reviewed_doc_objs rdo
;


-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on blobs.v_reviewed_doc_objects to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: blobs-v_reviewed_doc_objects.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: blobs-v_reviewed_doc_objects.sql,v $
-- Revision 1.1  2007-06-11 18:41:31  ncq
-- - new
--
-- Revision 1.1  2007/03/08 15:10:52  ncq
-- - add filename to blobs object view
--
-- Revision 1.2  2006/12/11 17:01:28  ncq
-- - use coalesce to detect reviewer
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
