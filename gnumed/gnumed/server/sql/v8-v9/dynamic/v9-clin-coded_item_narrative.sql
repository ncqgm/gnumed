-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-coded_item_narrative.sql,v 1.2 2008-01-27 21:24:58 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_coded_item_narrative cascade;
\set ON_ERROR_STOP 1


create view clin.v_coded_item_narrative as
select
	vn4s.pk_patient as pk_identity,
	vn4s.soap_cat as soap_cat,
	vn4s.narrative as narrative,
	cp.code as code,
	cp.xfk_coding_system as coding_system,
	cp.pk as pk_coded_phrase,
	vn4s.pk_encounter,
	vn4s.pk_episode,
	vn4s.pk_health_issue,
	vn4s.src_table,
	vn4s.src_pk
from
	clin.v_narrative4search vn4s
		inner join
	clin.coded_phrase cp
		on vn4s.narrative = cp.term
;

grant select on clin.v_coded_item_narrative to group "gm-doctors";

comment on view clin.v_coded_item_narrative is
	'This view shows all patient related narrative for which
	 a corresponding code is known to the system.';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-coded_item_narrative.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-clin-coded_item_narrative.sql,v $
-- Revision 1.2  2008-01-27 21:24:58  ncq
-- - improved naming of alias
--
-- Revision 1.1  2007/12/30 21:06:54  ncq
-- - new
--
-- Revision 1.1  2007/12/30 15:51:49  ncq
-- - added
--
--
